import time
import subprocess
from pathlib import Path
from scripts import packages, security, repos, system, home, fonts
from utils import common as util


def main():
    util.print_and_log_header("PyBootstrap... Good luck...")

    # Set up home directory first
    home.setup_home_directories()

    # Update DNF settings
    system.optimize_dnf()

    # Perform Initial full system update
    system.full_system_update()

    # Add needed repos
    repos.add_needed_repos()

    # Add chosen fonts
    fonts.install_fonts()

    # Add required packages
    packages.install_packages()

    # Configure security
    security.security_setup()

    # Perform another full system update
    system.full_system_update()

    # Perform a system clean
    system.system_clean()

    print("\nBootstrap complete!")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()

    duration = end_time - start_time
    minutes, seconds = divmod(duration, 60)
    util.print_and_log_header(
        f"Bootstrap completed in {int(minutes)} minutes and {int(seconds)} seconds."
    )

    print("Opening log file for review...")
    log_path = Path.home() / "archive" / "logs" / "bootstrap" / "bootstrap.log"
    subprocess.run(["xdg-open", str(log_path)])
