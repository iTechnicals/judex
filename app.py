import subprocess
import json

from secrets import token_urlsafe
from pathlib import Path
from flask import Flask, render_template, request

app = Flask(__name__, static_url_path="/static")

PROBLEM_TEXTS = []
PROBLEM_INPUTS = []
PROBLEM_OUTPUTS = []

PROBLEM_IDS = {}

for problem in (Path(__file__).parent / "problems").glob('*'):
    if not problem.is_dir():
        continue

    with open(problem / "problem.txt", "r") as f:
        PROBLEM_TEXTS.append(f.read())

    with open(problem / "tests.json", "r") as f:
        data = list(map(list, zip(*json.load(f))))
        PROBLEM_INPUTS.append(data[0])
        PROBLEM_OUTPUTS.append(data[1])

for i in range(len(PROBLEM_TEXTS)):
    PROBLEM_IDS[str(i)] = i
    # PROBLEM_IDS[token_urlsafe(16)] = i

PROBLEM_REV_IDS = {j: i for i, j in PROBLEM_IDS.items()}
print(PROBLEM_REV_IDS)

@app.route("/problem/<problem_id>", methods=['GET', 'POST'])
def problem(problem_id):
    complete = False
    problem_number = PROBLEM_IDS[problem_id]
    match request.method:
        case 'POST':
            try:
                user_input = request.form['user_input']

                for i, j in enumerate(PROBLEM_INPUTS[problem_number]):
                    process = subprocess.Popen(["python", "-c", user_input], stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                    for k in j:
                        process.stdin.write(k + "\n")

                    process.stdin.close()

                    output, _ = process.communicate(timeout=1)
                    output = output.strip().split("\n")

                    if output == PROBLEM_OUTPUTS[problem_number][i]:
                        continue

                    else:
                        new_output = f"Wrong answer on testcase {i + 1}: \nYour output:        Correct output:\n"
                        for actual, expt in zip(output, PROBLEM_OUTPUTS[problem_number][i]):
                            new_output += actual + "".join((20 - len(actual)) * [" "]) + expt + "\n"
                        output = new_output
                        break

                else:
                    output = "Congratulations, your program passed all the testcases!"
                    complete = True

            except subprocess.CalledProcessError as e:
                output = f"Error: {e.output}"

        case 'GET':
            output = None
            complete = False
            user_input = "# Code goes here!"

    print(PROBLEM_REV_IDS.get(problem_number + 1, False))

    return render_template('problem.html',
                           statement=PROBLEM_TEXTS[problem_number],
                           content=user_input,
                           output=output,
                           complete=complete,
                           next_problem_id=PROBLEM_REV_IDS.get(problem_number + 1, False))

@app.route("/done")
def done():
    return render_template('done.html')
