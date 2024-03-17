import subprocess
import json
import time
import socket

from secrets import token_urlsafe
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from markupsafe import escape

app = Flask(__name__, static_url_path="/static")
local = socket.gethostbyname(socket.gethostname())
print(local)

app.secret_key = token_urlsafe(16)

PROBLEM_TITLES = []
PROBLEM_TEXTS = []
PROBLEM_INPUTS = []
PROBLEM_OUTPUTS = []
PROBLEM_SCORES = []

DURATION = 120
START_TIME = float('inf')

for problem in (Path(__file__).parent / "problems").glob('*'):
    if not problem.is_dir():
        continue

    with open(problem / "problem.txt", "r") as f:
        txt = f.readlines()
        PROBLEM_TITLES.append(txt.pop(0)[:-1])
        PROBLEM_TEXTS.append("")

        inner = False
        i = 0
        while i < len(txt := "".join(txt)):
            try:
                if txt[i:i+4] == "```\n" and not inner:
                    PROBLEM_TEXTS[-1] += '<pre class="code"><code>'
                    inner = True
                    i += 4
                elif txt[i:i+4] == "\n```" and inner:
                    PROBLEM_TEXTS[-1] += '</code></pre>'
                    inner = False
                    i += 4
                else:
                    raise IndexError()
            except IndexError:
                PROBLEM_TEXTS[-1] += txt[i]
                i += 1


    with open(problem / "tests.json", "r") as f:
        data = json.load(f)
        PROBLEM_SCORES.append(data.pop(0))

        data = list(map(list, zip(*data)))
        PROBLEM_INPUTS.append(data[0])
        PROBLEM_OUTPUTS.append(data[1])

scores = {}

@app.route("/")
def home():
    print(request.remote_addr)
    if request.remote_addr == "127.0.0.1" or request.remote_addr == local:
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('problems', problem_id=0))


@app.route("/problems", methods=['GET', 'POST'])
def problems():
    if 'username' not in session:
        return redirect(url_for('login'))

    complete = False
    problem_number = session['first_unsolved_problem']
    
    if problem_number > len(PROBLEM_INPUTS) - 1:
        return redirect(url_for('leaderboard', extra_content='Welp, looks like you finished all the problems! Time for the event admin to get back to work :)'))
    
    match request.method:
        case 'POST':
            try:
                user_input = request.form['user_input']

                for i, j in enumerate(PROBLEM_INPUTS[problem_number]):
                    process = subprocess.Popen(["python", "-c", user_input], stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                    for k in j:
                        process.stdin.write(k + "\n")

                    process.stdin.close()

                    output, error = process.communicate(timeout=1)

                    if error:
                        output = error
                        break

                    output = output.strip().split("\n")
                    expt_output = PROBLEM_OUTPUTS[problem_number][i].copy()

                    if output == expt_output:
                        continue

                    else:
                        new_output = f"Wrong answer on testcase {i + 1}: \nYour output:        Correct output:\n"
                        if len(output) < len(expt_output):
                            output += [""] * (len(expt_output) - len(output))
                        else:
                            expt_output += [""] * (len(output) - len(expt_output))

                        for actual, expt in zip(output, expt_output):
                            new_output += actual + "".join((20 - len(actual)) * [" "]) + expt + "\n"
                        output = new_output
                        break

                else:
                    output = "Congratulations, your program passed all the testcases!"
                    complete = True

                    session['first_unsolved_problem'] += 1

                    scores[session["username"]][0] += 1
                    scores[session["username"]][1] += round(PROBLEM_SCORES[problem_number] * (1 - (time.time() - START_TIME) / DURATION))

            except subprocess.CalledProcessError as e:
                output = f"Error: {e.output}"

        case 'GET':
            output = "Output shows up here!"
            complete = False
            user_input = "# Code goes here!"

    return render_template('problem.html',
                           title=PROBLEM_TITLES[problem_number],
                           statement=PROBLEM_TEXTS[problem_number],
                           content=user_input,
                           output=output,
                           complete=complete)


@app.route("/get_scores")
def get_scores():
    return jsonify(scores)


@app.route("/leaderboard", methods=['GET', 'POST'])
def leaderboard():
    admin = request.remote_addr == "127.0.0.1" or request.remote_addr == local
    match request.method:
        case "POST":
            if admin:
                del scores[list(request.form.keys())[0]]

    return render_template('leaderboard.html',
                           extra_content=request.args.get('extra_content') or "",
                           admin=admin)


@app.route("/admin", methods=['POST', 'GET'])
def admin():
    if request.remote_addr == "127.0.0.1" or request.remote_addr == local:
        match request.method:
            case "POST":
                global START_TIME
                START_TIME = time.time()
                return redirect(url_for('leaderboard'))

            case "GET":
                return render_template('admin.html')

    else:
        return "", 403


@app.route("/auth")
def auth():
    if request.remote_addr == "127.0.0.1" or request.remote_addr == local:
        return "1"
    else:
        return "0"


@app.route("/login", methods=['POST', 'GET'])
def login():
    match request.method:
        case "POST":
            username = request.form['user_input']
            if username not in scores:
                session['username'] = username
                session['first_unsolved_problem'] = 0
                scores[username] = [0, 0]
                return redirect(url_for('waiting_room'))
            else:
                return render_template('login.html',
                                       extra_content="That username is already taken, try again!")
        case "GET":
            return render_template('login.html',
                                   extra_content=request.args.get('extra_content') or "")


@app.route("/waiting_room")
def waiting_room():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template('waiting_room.html', username=session['username'])


@app.route("/get_begun")
def get_begun():
    return str(int(START_TIME < float('inf')))


@app.route("/get_valid_username")
def get_valid_username():
    if session.get('username') in scores and time.time() < START_TIME + DURATION:
        return "0"
    elif session.get('username') not in scores:
        return "1"
    else:
        return "2"
