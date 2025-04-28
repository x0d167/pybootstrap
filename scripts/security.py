from pathlib import Path
from utils import common as util
from utils.aliases import ESCALATE, PKG


def enable_and_configure_ufw():
    """A function to enable and configure UFW firewall settings"""
    util.print_and_log("Confirming presence of UFW...")
    exit_code, _ = util.run_cmd([PKG.d, "list", "installed", "ufw"])
    if exit_code != 0:
        util.print_and_log("UFW not found. Installing...")
        install_code, _ = util.run_cmd([ESCALATE, PKG.d, "install", "ufw"])
        if install_code == 0:
            util.print_and_log("UFW has now been installed.")
        else:
            util.print_and_log("UFW failed install. please try manually.")
    else:
        util.print_and_log("UFW is on your system. Let's configure it.")

    # run the setup commands
    util.print_and_log("enabling sensible settings...")
    # disable UFW
    util.run_cmd([ESCALATE, "ufw", "disable"])
    # change settings
    util.print_and_log("Default to deny incoming")
    util.run_cmd([ESCALATE, "ufw", "default", "deny", "incoming"])
    util.print_and_log("Default to allow outgoing")
    util.run_cmd([ESCALATE, "ufw", "default", "allow", "outgoing"])
    util.print_and_log("Limit ssh...")
    util.run_cmd([ESCALATE, "ufw", "limit", "ssh"])
    # re-enable UFW
    util.print_and_log("Enabling UFW...")
    util.run_cmd([ESCALATE, "ufw", "--force", "enable"])

    util.print_and_log("Checking UFW status...")
    _, status_output = util.run_cmd([ESCALATE, "ufw", "status", "verbose"])
    util.print_and_log(status_output)

    util.print_and_log("UFW is now enabled. Firewall status checked!")

    util.print_and_log("Enabling and starting UFW systemd service...")
    util.run_cmd([ESCALATE, "systemctl", "enable", "--now", "ufw"])


def sysctl_system_hardening():
    """Add settings hardening sysctl with sensible defaults"""

    util.print_and_log("Updating sysctl settings...")

    sysctl_settings = [
        "net.ipv4.icmp_echo_ignore_broadcasts = 1\n",
        "net.ipv4.conf.all.accept_source_route = 0\n",
        "net.ipv4.tcp_syncookies = 1\n",
        "net.ipv4.conf.all.accept_redirects = 0\n",
        "net.ipv4.conf.all.send_redirects = 0\n",
        "net.ipv4.conf.all.rp_filter = 1\n",
        "net.ipv4.conf.all.log_martians = 1\n",
    ]

    temp_conf = Path("/tmp/99-laptop-hardening.conf")
    sysctl_harden_conf = Path("/etc/sysctl.d/99-laptop-hardening.conf")

    # Write to a temp file first
    with temp_conf.open("w") as file:
        file.writelines(sysctl_settings)

    # Move it into place with sudo
    move_exit_code, _ = util.run_cmd(
        [ESCALATE, "mv", str(temp_conf), str(sysctl_harden_conf)]
    )

    if move_exit_code == 0:
        util.print_and_log("Sysctl config moved successfully.")
    else:
        util.print_and_log("Sysctl config move failed. Please check manually.")

    util.run_cmd([ESCALATE, "sysctl", "--system"])
    util.print_and_log("sysctl settings have been updated.")


def enable_fail2ban():
    """Simple command to enable fail2ban if installed"""
    exit_code, _ = util.run_cmd([PKG.d, "list", "installed", "fail2ban"])
    if exit_code == 0:
        util.print_and_log("Enabling Fail2ban...")
        util.run_cmd([ESCALATE, "systemctl", "enable", "--now", "fail2ban"])
        _, status = util.run_cmd(
            [ESCALATE, "systemctl", "status", "fail2ban", "--no-pager"]
        )
        util.print_and_log(status)
        util.print_and_log("Fail2ban has been enabled")
    else:
        util.print_and_log("Fail2ban not installed. Review manually.")


def install_portmaster():
    util.print_and_log("Starting Portmaster install...")
    url = (
        "https://updates.safing.io/latest/linux_amd64/packages/portmaster-installer.rpm"
    )
    util.run_cmd(["curl", "-L", "-o", "/tmp/portmaster.rpm", url])
    util.run_cmd([ESCALATE, PKG.d, "install", "-y", "/tmp/portmaster.rpm"])
    util.run_cmd(["rm", "/tmp/portmaster.rpm"])
    util.print_and_log("Portmaster installed and ready")


def security_setup():
    """Orchestrate the security setup."""
    util.print_and_log_header("Setting Up Common Sense Security")

    # Install Portmaster
    install_portmaster()

    # Harden sysctl
    sysctl_system_hardening()

    # Enable ufw
    enable_and_configure_ufw()

    # Enable Fail2ban
    enable_fail2ban()

    util.print_and_log("Security setup is complete...")


if __name__ == "__main__":
    security_setup()
