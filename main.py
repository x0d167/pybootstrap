import subprocess


def run_cmd(cmd):
    return subprocess.run(
        cmd,
        shell=False,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()


def main():
    print("Hello from pybootstrap!")
    cmd = ["echo", "hello world"]
    output = run_cmd(cmd)
    print(output)


if __name__ == "__main__":
    main()
