from pathlib import Path
from utils import common as util
from utils.aliases import exit_messages, ESCALATE, PKG


def full_system_update():
    """Run a full system update."""
    util.print_and_log_header("DNF Update")
    cmd = [ESCALATE, PKG.d, "upgrade", "--refresh", "-y"]
    exit_code, output = util.run_cmd(cmd)
    message = exit_messages.get(exit_code, "Unexpected return code")
    util.print_and_log(message)

    util.print_and_log_header("Flatpak Update")
    flatpak_exit_code, output = util.run_cmd([PKG.f, "update", "-y"])
    flatpak_code = exit_messages.get(flatpak_exit_code, "Unexpected return code")
    util.print_and_log(flatpak_code)


def system_clean():
    """A function to run through DNF system clean of orphan packages."""
    util.print_and_log_header("Remove Orphaned Packages")
    remove, output = util.run_cmd([ESCALATE, PKG.d, "autoremove", "-y"])
    message_remove = exit_messages.get(remove, "Unexpected return code")
    util.print_and_log(message_remove)

    util.print_and_log_header("Clean DNF Cache")
    clean, output = util.run_cmd([ESCALATE, PKG.d, "clean", "all"])
    message_clean = exit_messages.get(clean, "Unexpected return code")
    util.print_and_log(message_clean)

    util.print_and_log_header("Cleaning Unused Flatpaks")
    flatpak_clean, output = util.run_cmd([PKG.f, "uninstall", "--unused", "-y"])
    flatpak_code = exit_messages.get(flatpak_clean, "Unexpected return code")
    util.print_and_log(flatpak_code)


def optimize_dnf():
    """Optimizes DNF settings before package installation later"""
    util.print_and_log_header("Optimizing DNF Settings")
    for setting, value in [
        ("max_parallel_downloads", "10"),
        ("fastestmirror", "True"),
        ("defaultyes", "True"),
    ]:
        if not ensure_dnf_settings(setting, value):
            message = f"Failed to apply {setting}. Check permissions or path."
            util.print_and_log(message)

    util.print_and_log_header("Installing DNF Plugins")
    exit_code, output = util.run_cmd(
        [ESCALATE, PKG.d, "install", "-y", "dnf-plugins-core"]
    )
    message = exit_messages.get(exit_code, "Unexpected return code")
    util.print_and_log(message)


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
    util.log_line(message)

    return True
