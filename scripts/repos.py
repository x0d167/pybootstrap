from pathlib import Path
from utils import common as util
from utils.aliases import ESCALATE, PKG, MULLVAD_REPO, ONE_PASSWORD
from utils.aliases import exit_messages, RPM


def install_rpm_fusion():
    """Installs RPM Fusion if not present."""
    util.print_and_log_header("Installing RPM Fusion")

    # Dynamically get Fedora version
    _, fedora_version = util.run_cmd(["rpm", "-E", "%fedora"])
    fedora_version = fedora_version.strip()

    rpm_urls = [
        f"https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-{fedora_version}.noarch.rpm",
        f"https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-{fedora_version}.noarch.rpm",
    ]

    if RPM["free"].exists() and RPM["nonfree"].exists():
        message = "RPM Fusion is already installed."
        util.print_and_log(message)
    else:
        for url in rpm_urls:
            exit_code, _ = util.run_cmd([ESCALATE, PKG.d, "install", "-y", url])
            message = exit_messages.get(exit_code, "Unexpected return code")
            util.print_and_log(message)


def enable_mullvad_repo():
    """Enable Mullvad Repo for later installation of vpn"""
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
    """Enable the 1Password Repo for later installation."""
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
    """Enables yazi copr repo for later installation with packages."""
    util.print_and_log_header("Enabling lihaohong/yazi copr")
    exit_code, _ = util.run_cmd(
        [ESCALATE, PKG.d, "copr", "enable", "--yes", "lihaohong/yazi"]
    )
    if exit_code == 0:
        util.print_and_log("lihaohong/yazi successfully enabled.")
    else:
        util.print_and_log("Failed to enable lihaohong/yazi. Please check manually")


def enable_protonvpn_repo():
    """Enables ProtonVPN Repo and installs it"""
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


def enable_openh264_repo():
    """Enables non-FOSS media codec"""
    util.print_and_log_header("Enable OpenH264 Codec Repo")

    # Check if the repo is enabled
    result, output = util.run_cmd([PKG.d, "repolist", "enabled"])
    if "fedora-cisco-openh264" in output:
        util.log_line("OpenH264 repo already enabled.")
    else:
        util.log_line("Enabling fedora-cisco-openh264 repo...")
        result, output = util.run_cmd([PKG.d, "repolist", "enabled"])
        if result == 0:
            util.print_and_log("OpenH264 repo enabled successfully.")
        else:
            util.print_and_log("Failed to enable OpenH264 repo.")


def add_needed_repos():
    util.print_and_log_header("Adding Needed Repos")

    # Start with RPM Fusion if not already installed.
    install_rpm_fusion()

    # Enable 1Password repo
    enable_1password_repo()

    # Enable Mullvad repo
    enable_mullvad_repo()

    # Enable ProtonVPN repo
    enable_protonvpn_repo()

    # Enable Yazi copr
    enable_yazi_copr()

    # Enable openH264 repo
    enable_openh264_repo()
