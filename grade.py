import subprocess
import resource

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable



@dataclass
class Language:
    id: str
    name: str
    extension: str
    comment: str
    compiled: bool
    runcmd: Callable[[str], list[str]]
    compcmd: Optional[Callable[[str], list[str]]] = None


class Languages:
    PYTHON = Language(
        "python", "Python", ".py", "#", False,
        lambda code: ["python", code]
    )

    CPP = Language(
        "cpp", "C++", ".cpp", "//", True,
        lambda code: [code + ".exe"],
        lambda code: ["g++", code, "-o", code + ".exe", "-Wall", "-Wextra", "-O2", "-static", "-lm"]
    )

    table = {
        "python": PYTHON,
        "cpp": CPP
    }


def limit(time=1, mem=64, proc=10):
    resource.setrlimit(resource.RLIMIT_CPU, (time + 1, resource.RLIM_INFINITY))
    resource.setrlimit(resource.RLIMIT_AS, (mem * 1024 * 1024, resource.RLIM_INFINITY))
    resource.setrlimit(resource.RLIMIT_NPROC, (proc, resource.RLIM_INFINITY))


def compile(code, language=Languages.CPP):
    return subprocess.run(
        language.compcmd(str(code)),
        capture_output=True, check=True
    )


def run(code, stdin, language=Languages.PYTHON, limits=(1, 64, 10)):
    return subprocess.run(
        ["sudo", "-u", "nobody"] + language.runcmd(str(code)),
        input=stdin, text=True, capture_output=True, timeout=1, check=True, preexec_fn=lambda: limit(*limits)
    )


def grade(code, stdin, stdout, language=Languages.PYTHON, limits=(1, 64, 10)):
    verdict = None

    if language.compiled:
        try:
            compile(code, language)
        except subprocess.CalledProcessError as e:
            verdict = "CE"
            # magic number yayyy
            # should always cut off the path to the file, assuming its length is constant
            output = e.stderr.decode('utf-8')[44:]

    if not verdict:
        for i, j in enumerate(stdin):
            stdin_format = "\n".join(j)

            try:
                output = run(code, stdin_format, language, limits).stdout.strip().split("\n")
                expt_output = stdout[i]

                if output != expt_output:
                    verdict = f"WA{i}"
                    new_output = f"Wrong answer on testcase {i + 1}: \nYour output:        Correct output:\n"

                    if len(output) < len(expt_output):
                        output += [""] * (len(expt_output) - len(output))
                    else:
                        expt_output += [""] * (len(output) - len(expt_output))

                    for actual, expt in zip(output, expt_output):
                        new_output += actual + "".join((20 - len(actual)) * [" "]) + expt + "\n"

                    output = new_output
                    break

            except subprocess.CalledProcessError as e:
                verdict = f"RE/MLE{i}"
                output = e.stderr
                if e.stdout:
                    output += f"\nBefore exiting, your program outputted the following:\n{e.stdout}"

                break

            except subprocess.TimeoutExpired as e:
                verdict = f"TLE{i}"
                output = "Your program was terminated for taking too long to complete."
                if e.stdout:
                    output += f"\nBefore being terminated, your program outputted the following:\n{e.stdout.decode('utf-8')}"

                break

        else:
            verdict = "AC"
            output = "Congratulations, your program passed all the testcases!"

    if output is None:
        output = "(no output given)"

    if len(output) > 2000:
        output = output[:2000]
        output += "...\nOutput was truncated for exceeding 2000 characters."

    return verdict, output
