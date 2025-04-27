from pathlib import Path
from utils import common as util
from utils import ESCALATE, PKG
import json


def install_packages():
    """This functions loops through a json list of required packages and
    installs"""

    packages = Path("config/packages.json")

    util.print_and_log_header("Installing Required System Packages")
    util.print_and_log("This may take a while")

    with open(packages) as file:
        package_list = json.load(file)

    for manager, segments in package_list.items():
        match manager:
            case "dnf":
                util.print_and_log("Processing dnf list...")
                for segment_dict in segments:
                    for segment_name, pkg_list in segment_dict.items():
                        util.print_and_log(f"Adding {segment_name} packages")
                        for pkg in pkg_list:
                            util.print_and_log(f"Checking for {pkg}...")
                            exit_code = util.run_cmd(
                                [PKG.d, "list", "installed", str(pkg)]
                            )
                            if exit_code != 0:
                                util.print_and_log(f"{pkg} not found. Installing now.")
                                install_code = util.run_cmd(
                                    [ESCALATE, PKG.d, "install", "-y", str(pkg)]
                                )
                                if install_code == 0:
                                    util.print_and_log(f"{pkg} install successful")
                                else:
                                    util.print_and_log(
                                        f"{pkg} install failed. Install manually."
                                    )
                            else:
                                util.print_and_log(
                                    f"{pkg} already installed, skipping..."
                                )
                        util.print_and_log(
                            f"{segment_name} packages have been completed"
                        )
                util.print_and_log(f"{manager} package installation step complete.")

            case "flatpak":
                util.print_and_log("Processing flatpak list...")
                for pkg in segments:
                    util.print_and_log(f"Checking for {pkg}...")
                    exit_code = util.run_cmd([PKG.f, "info", str(pkg)])
                    if exit_code == 0:
                        util.print_and_log(f"{pkg} exists. Skipping...")
                    else:
                        util.print_and_log(f"{pkg} not found. Adding flatpak...")
                        install_code = util.run_cmd([PKG.f, "install", str(pkg)])
                        if install_code == 0:
                            util.print_and_log(f"{pkg} successfully installed.")
                        else:
                            util.print_and_log(
                                f"{pkg} install failed. Install manually."
                            )
                util.print_and_log(f"{manager} package installation step complete.")
    util.print_and_log("Package Installation is complete.")
