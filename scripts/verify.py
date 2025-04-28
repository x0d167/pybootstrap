import subprocess
import json
import time
from pathlib import Path


# Utility functions
def check_path_exists(path):
    return Path(path).exists()


def check_user_dirs(expected_mappings):
    """Check ~/.config/user-dirs.dirs for expected directory mappings."""
    user_dirs_file = Path.home() / ".config" / "user-dirs.dirs"
    try:
        with open(user_dirs_file, "r") as file:
            contents = file.read()
    except FileNotFoundError:
        return False

    for key, expected_value in expected_mappings.items():
        expected_line = f'{key}="$HOME/{expected_value}"'
        if expected_line not in contents:
            return False
    return True


def check_package_installed(package_name):
    result = subprocess.run(["rpm", "-q", package_name], stdout=subprocess.DEVNULL)
    return result.returncode == 0


def check_flatpak_installed(app_id):
    result = subprocess.run(["flatpak", "info", app_id], stdout=subprocess.DEVNULL)
    return result.returncode == 0


def check_service_active(service_name):
    result = subprocess.run(["systemctl", "is-active", "--quiet", service_name])
    return result.returncode == 0


def check_vconsole_font(expected_font):
    try:
        with open("/etc/vconsole.conf", "r") as file:
            contents = file.read()
            return f"FONT={expected_font}" in contents
    except FileNotFoundError:
        return False


def log_message(message):
    """Logs the verification check for future records"""
    logpath = Path.home() / ".local" / "var" / "log" / "pybootstrap"
    try:
        logpath.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Failed to create log file location: {e}")

    logfile = logpath / "bootstrap-verify.log"
    with open(logfile, "a") as log:
        log.write(message)


def print_and_log(message):
    """Prints and logs the message"""
    print(message)
    log_message(message)


def print_and_log_header(label):
    """Prints headers for sections and adds to the logfile"""
    logpath = Path.home() / ".local" / "var" / "log" / "pybootstrap"
    try:
        logpath.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Failed to create log file location: {e}")

    line = "#" + "=" * (len(label) + 4)
    block = f"{line}\n#  {label}  #\n{line}\n"
    print(block)

    logfile = logpath / "bootstrap-verify.log"
    with open(logfile, "a") as log:
        log.write(block + "\n")


# Main test functions
def main():
    checks = []

    # Directory checks
    home = Path.home()
    directories = ["archive", "bin", "dev", "docs", "media", "tmp", "logarchive"]
    for dir_name in directories:
        path = home / dir_name
        checks.append((f"Directory exists: {path}", check_path_exists(path)))

    # After other checks
    expected_mappings = {
        "XDG_DOCUMENTS_DIR": "docs",
        "XDG_DOWNLOAD_DIR": "tmp",
        "XDG_PICTURES_DIR": "media/pictures",
        "XDG_MUSIC_DIR": "media/music",
        "XDG_VIDEOS_DIR": "media/videos",
        "XDG_PUBLICSHARE_DIR": "tmp/public",
        "XDG_TEMPLATES_DIR": "archive/templates",
        "XDG_DESKTOP_DIR": "archive/desktop",
    }

    checks.append(
        ("User directories remapped correctly", check_user_dirs(expected_mappings))
    )

    # Package checks (add as needed)
    package_list = Path("config/packages.json")
    with open(package_list) as file:
        packages = json.load(file)

    for manager, segment in packages.items():
        match manager:
            case "dnf":
                for segment_name, pkg_list in segment.items():
                    for pkg in pkg_list:
                        checks.append(
                            (
                                f"DNF Package installed: {pkg}",
                                check_package_installed(pkg),
                            )
                        )

            case "flatpak":
                for pkg in pkg_list:
                    checks.append(
                        (f"Flatpak App installed: {pkg}", check_flatpak_installed(pkg))
                    )

    # Service checks
    services = ["fail2ban", "ufw"]
    for service in services:
        checks.append((f"Service active: {service}", check_service_active(service)))

    # Console font check
    checks.append(("Console font set correctly", check_vconsole_font("ter-v32b")))

    # Results
    success = 0
    fail = 0
    print("\nPost-Bootstrap Verification Results:\n" + "=" * 40)
    print_and_log_header("Post-Bootstrap Verification Results:")
    for description, result in checks:
        if result:
            print_and_log(f"✅ {description}")
            success += 1
        else:
            print_and_log(f"❌ {description}")
            fail += 1

    print_and_log("=" * 40)
    print_and_log(f"Summary: {success} passed, {fail} failed.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()

    duration = end_time - start_time
    minutes, seconds = divmod(duration, 60)
    print_and_log(
        f"Verification completed in {int(minutes)} minutes and {int(seconds)} seconds."
    )

    print("Opening report card for review...")
    log_path = (
        Path.home() / ".local" / "var" / "log" / "pybootstrap" / "bootstrap-verify.log"
    )
    subprocess.run(["xdg-open", str(log_path)])
