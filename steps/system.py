from pathlib import Path
from utils import common as util
from utils import RPM, rpm_url, exit_messages, ESCALATE, PKG
from utils import MULLVAD_REPO, ONE_PASSWORD


def full_system_update():
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
    util.print_and_log_header("Optimizing DNF Settings")
    for setting, value in [
        ("max_parallel_downloads", "10"),
        ("fastestmirror", "True"),
        ("defaultyes", "True"),
    ]:
        if not util.ensure_dnf_settings(setting, value):
            message = f"Failed to apply {setting}. Check permissions or path."
            util.print_and_log(message)

    util.print_and_log_header("Installing DNF Plugins")
    exit_code, output = util.run_cmd(
        [ESCALATE, PKG.d, "install", "-y", "dnf-plugins-core"]
    )
    message = exit_messages.get(exit_code, "Unexpected return code")
    util.print_and_log(message)


def install_rpm_fusion():
    util.print_and_log_header("Installing RPM Fusion")
    if RPM["free"].exists() and RPM["nonfree"].exists():
        message = "RPM Fusion is already installed."
        util.print_and_log(message)
    else:
        for url in rpm_url:
            exit_code, output = util.run_cmd([ESCALATE, PKG.d, "install", "-y", url])
            message = exit_messages.get(exit_code, "Unexpected return code")
            util.print_and_log(message)


def enable_mullvad_repo():
    util.print_and_log_header("Enabling Mullvad Repo")
    mullvad_repo = MULLVAD_REPO
    mullvad_template = Path("utils/mullvad.txt")

    # is mullvad repo already there?
    if mullvad_repo.exists():
        message = "Mullvad repo is already present."
        util.print_and_log(message)
    else:
        util.print_and_log("Mullvad repo not found. Adding it manually")

        with mullvad_template.open("r") as template:
            lines = template.readlines()

        temp_path = Path("/tmp/mullvad.repo")
        with temp_path.open("w") as temp_file:
            temp_file.writelines(lines)

        mv_exit_code, _ = util.run_cmd(
            [ESCALATE, "mv", str(temp_path), str(mullvad_repo)]
        )
        if mv_exit_code == 0:
            util.print_and_log("Mullvad repo moved successfully.")
        else:
            util.print_and_log("Failed to move Mullvad repo. Please check manually.")


def enable_1password_repo():
    util.print_and_log_header("Enabling 1Password Repo")
    onepassword_repo = ONE_PASSWORD
    onepassword_template = Path("utils/1password.txt")

    # Is 1Password repo already there?
    if onepassword_repo.exists():
        message = "1Password repo is already present."
        util.print_and_log(message)
    else:
        util.print_and_log("1Password repo not found. Adding it manually")

        # Import the GPG key for 1Password
        util.print_and_log("Importing 1Password GPG key...")
        key_exit_code, _ = util.run_cmd(
            [
                ESCALATE,
                PKG.r,
                "--import",
                "https://downloads.1password.com/linux/keys/1password.asc",
            ]
        )
        if key_exit_code == 0:
            util.print_and_log("GPG key imported successfully.")
        else:
            util.print_and_log("Failed to import GPG key. Please check manually.")

        # Handle repo creation
        with onepassword_template.open("r") as file:
            lines = file.readlines()

        temp_path = Path("/tmp/1password.repo")
        with temp_path.open("w") as temp_file:
            temp_file.writelines(lines)

        onepass_exit_code, _ = util.run_cmd(
            [ESCALATE, "mv", str(temp_path), str(onepassword_repo)]
        )
        if onepass_exit_code == 0:
            util.print_and_log("1Password repo moved successfully")
        else:
            util.print_and_log("Failed to move 1Password repo. Please check manually")


def enable_yazi_copr():
    util.print_and_log_header("Enabling lihaohong/yazi copr")
    exit_code, _ = util.run_cmd([ESCALATE, PKG.d, "copr", "enable", "lihaohong/yazi"])
    if exit_code == 0:
        util.print_and_log("lihaohong/yazi successfully enabled.")
    else:
        util.print_and_log("Failed to enable lihaohong/yazi. Please check manually")


def enable_protonvpn_repo():
    util.print_and_log_header("Enabling ProtonVPN Repo")
    os_version = int(util.get_os_version())
    proton_rpm = "protonvpn-stable-release-1.0.3-1.noarch.rpm"
    proton_url = f"https://repo.protonvpn.com/fedora-{os_version}-stable/protonvpn-stable-release/{proton_rpm}"
    proton_rpm_path = Path("/tmp") / proton_rpm

    # Check if ProtonVPN repo is already installed
    exit_code, _ = util.run_cmd([PKG.r, "-q", "protonvpn-stable-release"])
    if exit_code == 0:
        util.print_and_log("ProtonVPN repo already installed.")
        return

    util.print_and_log("Downloading ProtonVPN repo RPM...")

    # Download the RPM
    dl_exit_code, _ = util.run_cmd(["curl", "-fLo", str(proton_rpm_path), proton_url])
    if dl_exit_code != 0:
        util.print_and_log(
            "Failed to download ProtonVPN repo RPM. Skipping ProtonVPN setup..."
        )
        return

    # Install the downloaded RPM to enable the repo
    install_exit_code, _ = util.run_cmd(
        [ESCALATE, PKG.d, "install", "-y", str(proton_rpm_path)]
    )
    if install_exit_code != 0:
        util.print_and_log(
            "Failed to install ProtonVPN repo RPM. Skipping ProtonVPN client install..."
        )
        return

    util.print_and_log("ProtonVPN repo installed successfully.")

    # Install the ProtonVPN desktop client
    client_exit_code, _ = util.run_cmd(
        [ESCALATE, PKG.d, "install", "-y", "proton-vpn-gnome-desktop"]
    )
    if client_exit_code == 0:
        util.print_and_log("ProtonVPN client installed successfully.")
    else:
        util.print_and_log("Failed to install ProtonVPN client.")


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


def enable_openh264_repo():
    util.print_and_log_header("Enable OpenH264 Codec Repo")

    # Check if the repo is enabled
    result, output = util.run_cmd(["dnf", "repolist", "enabled"])
    if "fedora-cisco-openh264" in output:
        util.log_line("OpenH264 repo already enabled.")
    else:
        util.log_line("Enabling fedora-cisco-openh264 repo...")
        result, output = util.run_cmd([...])
        if result == 0:
            util.print_and_log("OpenH264 repo enabled successfully.")
        else:
            util.print_and_log("Failed to enable OpenH264 repo.")
