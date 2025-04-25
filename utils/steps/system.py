from pathlib import Path
from utils import common as util
from utils import RPM, rpm_url, exit_messages, ESCALATE, PKG


def full_system_update():
    util.print_and_log_header("DNF Update")
    cmd = [ESCALATE, PKG.d, "upgrade", "--refresh", "-y"]
    exit_code, output = util.run_cmd(cmd)
    message = exit_messages.get(exit_code, "Unexpected return code")
    print(message)
    util.log_line(message)

    util.print_and_log_header("Flatpak Update")
    flatpak_cmd, output = util.run_cmd([PKG.f, "update", "-y"])
    flatpak_code = exit_messages.get(flatpak_cmd, "Unexpected return code")
    print(flatpak_code)
    util.log_line(flatpak_code)


def system_clean():
    util.print_and_log_header("Remove Orphaned Packages")
    remove, output = util.run_cmd([ESCALATE, PKG.d, "autoremove", "-y"])
    message_remove = exit_messages.get(remove, "Unexpected return code")
    print(message_remove)
    util.log_line(message_remove)

    util.print_and_log_header("Clean DNF Cache")
    clean, output = util.run_cmd([ESCALATE, PKG.d, "clean", "all"])
    message_clean = exit_messages.get(clean, "Unexpected return code")
    print(message_clean)
    util.log_line(message_clean)

    util.print_and_log_header("Cleaning Unused Flatpaks")
    flatpak_clean, output = util.run_cmd([PKG.f, "uninstall", "--unused", "-y"])
    flatpak_code = exit_messages.get(flatpak_clean, "Unexpected return code")
    print(flatpak_code)
    util.log_line(flatpak_code)


def optimize_dnf():
    util.print_and_log_header("Optimizing DNF Settings")
    for setting, value in [
        ("max_parallel_downloads", "10"),
        ("fastestmirror", "True"),
        ("defaultyes", "True"),
    ]:
        if not util.ensure_dnf_settings(setting, value):
            message = f"Failed to apply {setting}. Check permissions or path."
            print(message)
            util.log_line(message)

    util.print_and_log_header("Installing DNF Plugins")
    exit_code, output = util.run_cmd(
        [ESCALATE, PKG.d, "install", "-y", "dnf-plugins-core"]
    )
    message = exit_messages.get(exit_code, "Unexpected return code")
    print(message)
    util.log_line(message)


def install_rpm_fusion():
    if RPM["free"].exists() and RPM["nonfree"].exists():
        message = "RPM Fusion is already installed."
        print(message)
        util.log_line(message)
    else:
        for url in rpm_url:
            exit_code, output = util.run_cmd([ESCALATE, PKG.d, "install", "-y", url])
            message = exit_messages.get(exit_code, "Unexpected return code")
            print(message)
            util.log_line(message)


def ensure_dnf_settings(setting, value):
    """Ensure a key=value line is present in  /etc/dnf/dnf.conf"""
    conf_path = Path("/etc/dnf/dnf.conf")

    try:
        with conf_path.open("r") as file:
            lines = file.readlines()
    except PermissionError:
        print("You need to run this script with elevated privileges.")
        return
    except FileNotFoundError:
        print("dnf.conf not found! Are you sure DNF is installed?")
        return

    setting_line = f"{setting}={value}\n"
    found = False

    for i, line in enumerate(lines):
        if line.strip().startswith(f"{setting}="):
            lines[i] = setting_line
            found = True
            break

    if not found:
        lines.append(setting_line)

    with conf_path.open("w") as file:
        file.writelines(lines)

    message = f"Ensured: {setting}={value}"
    print(message)
    util.log_line(message)

    return True


def enable_openh264_repo():
    util.print_and_log_header("Enable OpenH264 Codec Repo")

    # Check if the repo is enabled
    result, output = util.run_cmd(["dnf", "repolist", "enabled"])

    if "fedora-cisco-openh264" in output:
        util.print_and_log("✅ OpenH264 repo already enabled.")
    else:
        util.print_and_log("📡 Enabling fedora-cisco-openh264 repo...")
        util.run_cmd(
            [
                util.ESCALATE,
                "dnf",
                "config-manager",
                "--enable",
                "fedora-cisco-openh264",
            ]
        )
