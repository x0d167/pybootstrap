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
    """Log current DNF settings and advise manual review."""
    util.print_and_log_header("Optimizing DNF Settings")

    util.print_and_log("Checking /etc/dnf/dnf.conf contents...")

    exit_code, output = util.run_cmd(["cat", "/etc/dnf/dnf.conf"])
    if exit_code == 0:
        util.print_and_log(output)
    else:
        util.print_and_log(
            "Could not read /etc/dnf/dnf.conf. You may need to manually review it."
        )

    util.print_and_log(
        "If not already present, add these settings manually to /etc/dnf/dnf.conf:\n"
        "  - max_parallel_downloads=10\n"
        "  - fastestmirror=True\n"
        "  - defaultyes=True"
    )
