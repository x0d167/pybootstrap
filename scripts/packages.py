from pathlib import Path
from utils import common as util
from utils.aliases import ESCALATE, PKG
import json
import urllib.request


def install_new_packages():
    """This functions loops through a json list of required packages and
    installs"""

    packages = Path("config/packages.json")

    util.print_and_log_header("Installing DNF and Flatpak Packages")
    util.print_and_log("This may take a while")

    with open(packages) as file:
        package_list = json.load(file)

    for manager, segments in package_list.items():
        match manager:
            case "dnf":
                util.print_and_log("Processing dnf list...")
                for segment_name, pkg_list in segments.items():
                    util.print_and_log(f"Adding {segment_name} packages")
                    for pkg in pkg_list:
                        util.print_and_log(f"Checking for {pkg}...")
                        exit_code, _ = util.run_cmd(["rpm", "-q", str(pkg)])
                        if exit_code != 0:
                            fail_exit, _ = util.run_cmd(["which", str(pkg)])
                            if fail_exit != 0:
                                util.print_and_log(f"{pkg} not found. Installing now.")
                                install_code, _ = util.run_cmd(
                                    [ESCALATE, PKG.d, "install", "-y", str(pkg)]
                                )
                                if install_code in (0, 10):
                                    util.print_and_log(f"{pkg} install successful")
                                else:
                                    util.print_and_log(
                                        f"{pkg} install failed. Install manually."
                                    )
                            else:
                                util.print_and_log(
                                    f"{pkg} already installed, skipping..."
                                )
                        else:
                            util.print_and_log(f"{pkg} already installed, skipping...")
                    util.print_and_log(f"{segment_name} packages have been completed")
                util.print_and_log(f"{manager} package installation step complete.")

            case "flatpak":
                util.print_and_log("Making sure Flathub repo is added...")
                util.run_cmd(
                    [
                        "flatpak",
                        "remote-add",
                        "--if-not-exists",
                        "flathub",
                        "https://flathub.org/repo/flathub.flatpakrepo",
                    ]
                )

                util.print_and_log("Processing flatpak list...")
                for pkg in segments:
                    util.print_and_log(f"Checking for {pkg}...")
                    exit_code, _ = util.run_cmd([PKG.f, "info", str(pkg)])
                    if exit_code == 0:
                        util.print_and_log(f"{pkg} exists. Skipping...")
                    else:
                        util.print_and_log(f"{pkg} not found. Adding flatpak...")
                        install_code, _ = util.run_cmd(
                            [PKG.f, "install", "flathub", "-y", str(pkg)]
                        )
                        if install_code == 0:
                            util.print_and_log(f"{pkg} successfully installed.")
                        else:
                            util.print_and_log(
                                f"{pkg} install failed. Install manually."
                            )
                util.print_and_log(f"{manager} package installation step complete.")
    util.print_and_log("Package Installation is complete.")


def install_mullvad():
    """Downloads and installs Mullvad VPN RPM manually."""

    util.print_and_log("Starting manual Mullvad VPN install...")

    url = "https://mullvad.net/en/download/app/rpm/latest"
    temp_path = Path("/tmp/mullvad-latest.rpm")

    util.print_and_log("Downloading Mullvad VPN...")
    util.run_cmd(["curl", "-L", "-o", str(temp_path), url])

    util.print_and_log("Installing Mullvad VPN...")
    util.run_cmd([ESCALATE, PKG.d, "install", "-y", str(temp_path)])

    util.print_and_log("Cleaning up temporary RPM...")
    util.run_cmd(["rm", "-f", str(temp_path)])

    util.print_and_log("Mullvad VPN install complete!")


def install_rustup():
    """Install rustup and set up Rust toolchain properly."""
    util.print_and_log("Checking if Rust is already installed...")

    exit_code, _ = util.run_cmd(["which", "rustc"])
    if exit_code == 0:
        util.print_and_log("Rust is already installed. Skipping rustup installation.")
        return

    util.print_and_log("Rust not found. Installing Rustup...")

    rustup_script_path = Path("/tmp/rustup-init.sh")

    try:
        urllib.request.urlretrieve("https://sh.rustup.rs", str(rustup_script_path))
    except Exception as e:
        util.print_and_log(f"Failed to download Rustup installer: {e}")
        return

    util.run_cmd(["chmod", "+x", str(rustup_script_path)])
    install_code, _ = util.run_cmd([str(rustup_script_path), "-y"])

    if install_code == 0:
        util.print_and_log("Rustup installed successfully.")
    else:
        util.print_and_log("Rustup installation failed. Please check manually.")

    util.run_cmd(["rm", "-f", str(rustup_script_path)])
    util.print_and_log("Rust installed. You may need to restart your terminal.")


def install_proton_pass():
    """Install Proton Pass as alternative to 1Password. Installing both for
    now"""

    util.print_and_log("Installing Proton Pass...")
    url = "https://proton.me/download/PassDesktop/linux/x64/ProtonPass.rpm"
    temp_path = Path("/tmp/protonpass.rpm")

    util.print_and_log("Downloading ProtonPass.rpm")
    util.run_cmd(["curl", "-L", "-o", temp_path, url])

    util.print_and_log("Installing package...")
    install_code, _ = util.run_cmd([ESCALATE, PKG.d, "install", "-y", str(temp_path)])
    if install_code == 0:
        util.print_and_log("Proton Pass installed successfully")
    else:
        util.print_and_log("Proton Pass installation failed.")

    util.print_and_log("Cleaning up temporary files.")
    util.run_cmd(["rm", "-f", str(temp_path)])


def install_packages():
    """Orchestrator of the package install scripts."""
    util.print_and_log_header("Installing Required System Packages")

    # Install all dnf and flatpaks
    install_new_packages()

    # Install Mullvad VPN
    install_mullvad()

    # Install rustup
    install_rustup()

    # Install Proton Pass
    install_proton_pass()
