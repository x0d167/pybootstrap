from pathlib import Path
from types import SimpleNamespace

rpm_url = [
    "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm",
    "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm",
]

RPM = {
    "free": Path("/etc/yum.repos.d/rpmfusion_free.repo"),
    "nonfree": Path("/etc/yum.repos.d/rpmfusion-nonfree.repo"),
}


ESCALATE = "sudo"
PKG = SimpleNamespace(
    d="dnf",
    r="rpm",
    f="flatpak",
)

exit_messages = {
    0: "No updates available. System is up to date.",
    100: "Updates were available and processed.",
    1: "Handled error occurred. Review output for details.",
    3: "Unknown error occurred. Investigate.",
    200: "Lock error. Is another package manager running?",
}
