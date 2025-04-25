import subprocess
from pathlib import Path
from datetime import datetime


def run_cmd(cmd):
    """A function for running commands and saving their output to logs"""
    process = subprocess.Popen(
        cmd,
        shell=False,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output = []
    for line in process.stdout:
        print(line, end="")
        log_line(line)
        output.append(line)

    process.stdout.close()
    process.wait()
    return process.returncode, "".join(output)


def get_logfile_path():
    logfile = Path("~/.bootstrap/logs/bootstrap.log").expanduser()
    logfile.parent.mkdir(parents=True, exist_ok=True)  # make the dir if nonexistent
    return logfile


def print_and_log(message):
    print(message)
    log_line(message)


def log_line(message):
    logfile = get_logfile_path()

    with open(logfile, "a") as log:
        log.write(f"[{datetime.now()}] {message}\n")


def print_and_log_header(label):
    line = "#" + "=" * (len(label) + 4)
    block = f"{line}\n#  {label}  #\n{line}\n"
    print(block)
    logfile = get_logfile_path()
    with open(logfile, "a") as log:
        log.write(block + "\n")


def get_os_version():
    os_release = Path("/etc/os-release")

    if not os_release.exists():
        raise FileNotFoundError("/etc/os-release not found. Are you linux?")

    with os_release.open("r") as file:
        for line in file:
            if line.startswith("VERSION_ID="):
                version = line.strip().split("=")[1].strip('"')
                return version

    raise ValueError("VERSION_ID not foung in /etc/os-release")
