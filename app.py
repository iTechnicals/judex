import subprocess
import json
import time
import resource

from secrets import token_urlsafe
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

app = Flask(__name__, static_url_path="/static")

app.secret_key = token_urlsafe(16)
authtoken = token_urlsafe(16)
print(authtoken)

PROBLEM_TITLES = []
PROBLEM_TEXTS = []
PROBLEM_INPUTS = []
PROBLEM_OUTPUTS = []
PROBLEM_SCORES = []

DURATION = 180
START_TIME = float('inf')

root = Path(__file__).parent / "problems"

i = 0
while True:
    problem = root / str(i)

    try:
        with open(problem / "problem.txt", "r") as f:
            txt = f.readlines()
            PROBLEM_TITLES.append(txt.pop(0)[:-1])
            PROBLEM_TEXTS.append("")

            inner = False
            j = 0
            while j < len(txt := "".join(txt)):
                try:
                    if txt[j:j + 4] == "```\n" and not inner:
                        PROBLEM_TEXTS[-1] += '<pre class="code"><code>'
                        inner = True
                        j += 4
                    elif txt[j:j + 4] == "\n```" and inner:
                        PROBLEM_TEXTS[-1] += '</code></pre>'
                        inner = False
                        j += 4
                    else:
                        raise IndexError()
                except IndexError:
                    PROBLEM_TEXTS[-1] += txt[j]
                    j += 1

        i += 1

    except FileNotFoundError:
        break


    with open(problem / "tests.json", "r") as f:
        data = json.load(f)
        PROBLEM_SCORES.append(data.pop(0))

        data = list(map(list, zip(*data)))
        PROBLEM_INPUTS.append(data[0])
        PROBLEM_OUTPUTS.append(data[1])

scores = {}


def limit(mem=64, proc=1):
    resource.setrlimit(resource.RLIMIT_AS, (mem * 1024 * 1024, mem * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NPROC, (proc, proc))


@app.route("/")
def home():
    if session.get('admin'):
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

    output = "Output shows up here!"
    user_input = "# Code goes here!"

    match request.method:
        case 'POST':
            try:
                user_input = request.form['user_input']

                for i, j in enumerate(PROBLEM_INPUTS[problem_number]):
                    program_input = "\n".join(j)

                    try:
                        output = subprocess.run(["sudo", "-u", "nobody", "python", "-c", user_input],
                                                input=program_input,
                                                text=True,
                                                capture_output=True,
                                                timeout=1,
                                                check=True,
                                                preexec_fn=limit)

                        output = output.stdout

                    except subprocess.CalledProcessError as e:
                        output = e.stderr
                        if e.stdout:
                            output += f"\nBefore exiting, your program outputted the following:\n{e.stdout}"

                        break

                    except subprocess.TimeoutExpired as e:
                        output = "Your program was terminated for taking too long to complete."
                        if e.stdout:
                            output += f"\nBefore being terminated, your program outputted the following:\n{e.stdout.decode('utf-8')}"

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
                    scores[session["username"]][1] += round(PROBLEM_SCORES[problem_number] * (1 - 2/3 * (time.time() - START_TIME) / DURATION))

            except subprocess.CalledProcessError as e:
                output = f"Error: {e.output}"

    if output is None:
        output = "(no output given)"

    if len(output) > 2000:
        output = output[:2000]
        output += "...\nOutput was truncated for exceeding 2000 characters."

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
    match request.method:
        case "POST":
            if admin:
                del scores[list(request.form.keys())[0]]

    return render_template('leaderboard.html',
                           extra_content=request.args.get('extra_content') or "",
                           admin=admin)


@app.route("/admin", methods=['POST', 'GET'])
def admin():
    if session.get('admin'):
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
    if session.get('admin'):
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


@app.route(f"/{authtoken}")
def authtoken():
    session['admin'] = True
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
