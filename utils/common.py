import subprocess
from pathlib import Path
from datetime import datetime
from utils import PROJECT_NAME


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
    """Gets or makes the log file path on the system"""
    log_base = Path.home() / ".local" / "var" / "log" / PROJECT_NAME
    log_base.mkdir(parents=True, exist_ok=True)
    return log_base / "bootstrap.log"


def print_and_log(message):
    """Simply print message to terminal then log it"""
    print(message)
    log_line(message)


def log_line(message):
    """writes logs to the logfile with timestamps"""
    logfile = get_logfile_path()

    with open(logfile, "a") as log:
        log.write(f"[{datetime.now()}] {message}\n")


def print_and_log_header(label):
    """Prints headers for sections and adds to the logfile"""
    line = "#" + "=" * (len(label) + 4)
    block = f"{line}\n#  {label}  #\n{line}\n"
    print(block)
    logfile = get_logfile_path()
    with open(logfile, "a") as log:
        log.write(block + "\n")


def get_os_version():
    """Little helper for OS-Release if needed."""
    os_release = Path("/etc/os-release")

    if not os_release.exists():
        raise FileNotFoundError("/etc/os-release not found. Are you linux?")

    with os_release.open("r") as file:
        for line in file:
            if line.startswith("VERSION_ID="):
                version = line.strip().split("=")[1].strip('"')
                return version

    raise ValueError("VERSION_ID not foung in /etc/os-release")


def get_filename_from_url(url):
    """Get the filename from a download url e.g. git"""
    return url.split("/")[-1]


def get_filename_from_zip(zipname):
    """Get the unzipped filename from a .zip filename"""
    return zipname.rsplit(".", 1)[0]
