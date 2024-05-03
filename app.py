import json
import time

from secrets import token_urlsafe
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, session

from grade import grade, Languages

app = Flask(__name__, static_url_path="/static")

app.secret_key = token_urlsafe(16)
authtoken = token_urlsafe(16)
print(authtoken)

PROBLEM_TITLES = []
PROBLEM_TEXTS = []
PROBLEM_INPUTS = []
PROBLEM_OUTPUTS = []
PROBLEM_SCORES = []

DURATION = 1800
START_TIME = float('inf')

root = Path(__file__).parent

i = 0
while True:
    problem = root / "problems" / str(i)

    try:
        with open(problem / "problem.txt", "r") as f:
            txt = f.readlines()
            PROBLEM_TITLES.append(txt.pop(0)[:-1])
            PROBLEM_TEXTS.append("")

            inner = False
            j = 0
            while j < len(txt := "".join(txt).strip()):
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
    elif START_TIME > float('inf'):
        return redirect(url_for('waiting_room'))

    problem_number = session['first_unsolved_problem']

    user_input = ""
    language = Languages.PYTHON
    output = "Output shows up here!"

    match request.method:
        case 'POST':
            user_input = request.form['user_input']
            language = Languages.table[request.form['language']]

            with open("submissions.json", "r") as f:
                submissions = json.load(f)
                while (id := token_urlsafe(16)) in submissions:
                    pass

            code_dir = root / "submissions"
            if not code_dir.exists():
                code_dir.mkdir()
            code_path = root / "submissions" / (id + language.extension)
            with open(code_path, "w+") as f:
                f.write(user_input)

            verdict, output = grade(code_path, PROBLEM_INPUTS[problem_number], PROBLEM_OUTPUTS[problem_number], language=language)

            if verdict == "AC":
                user_input = ""
                session['first_unsolved_problem'] += 1

                scores[session["username"]][0] += 1
                scores[session["username"]][1] += round(PROBLEM_SCORES[problem_number] * (1 - 2/3 * (time.time() - START_TIME) / DURATION))

            submissions[id] = {
                "username": session['username'],
                "language": language.id,
                "problem": problem_number,
                "verdict": verdict,
                "time": time.time() - START_TIME
            }

            with open("submissions.json", "w") as f:
                json.dump(submissions, f, indent=4)

            problem_number = session['first_unsolved_problem']

    if problem_number > len(PROBLEM_INPUTS) - 1:
        return redirect(url_for('leaderboard', extra_content='Welp, looks like you finished all the problems! Time for the event admin to get back to work :)'))

    return render_template(
        'problem.html',
        title=PROBLEM_TITLES[problem_number],
        statement=PROBLEM_TEXTS[problem_number],
        content=user_input,
        language=language.id,
        output=output
    )


@app.route("/get_scores")
def get_scores():
    return jsonify(scores)


# this is probably hella slow ngl
@app.route("/get_submissions")
def get_submissions():
    if session.get('admin'):
        with open("submissions.json", "r") as f:
            submissions = json.load(f)
            for id, s in submissions.items():
                with open(root / "submissions" / (id + Languages.table[s["language"]].extension), "r") as f:
                    s["code"] = f.read()
        return jsonify(submissions)
    else:
        return "", 403



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
        global START_TIME
        match request.method:
            case "POST":
                START_TIME = time.time()
                return redirect(url_for('leaderboard'))

            case "GET":
                if START_TIME < float('inf'):
                    return render_template('submissions.html')
                else:
                    return render_template('start.html')

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
