import os
from pathlib import Path
from utils import common as util
from utils import PKG, ESCALATE


def install_nerd_fonts():
    """Install Nerd Fonts from github repos"""

    util.print_and_log_header("Installing Nerd Fonts")

    fonts_dir = Path.home() / ".local" / "share" / "fonts"
    fonts_dir.mkdir(parents=True, exist_ok=True)

    font_urls = [
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/0xProto.zip",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/CascadiaMono.zip",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/CascadiaCode.zip",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraMono.zip",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/GeistMono.zip",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.zip",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/Meslo.zip",
    ]

    for url in font_urls:
        zipname = util.get_filename_from_url(url)
        zip_path = Path.home() / "tmp" / zipname
        unzip_name = util.get_filename_from_zip(zipname)
        unzip_path = Path.home() / "tmp" / unzip_name
        util.run_cmd(["curl", "-L", "-o", str(zip_path), url])

        util.print_and_log(f"unzipping {zipname}...")
        util.run_cmd(["unzip", str(zip_path), "-d", str(unzip_path)])

        util.print_and_log("Now moving font to fonts directory")
        util.run_cmd(["mv", str(unzip_path), str(fonts_dir)])

        util.print_and_log(f"Cleaning {zipname} from tmp directory")
        util.run_cmd(["rm", "-rf", str(zip_path)])

    util.print_and_log("Nerd Fonts are now installed.")


def install_terminus_console_font():
    """Install and set Terminus console font for TTY."""

    util.print_and_log_header("Installing Terminus Console Font")

    # Check if Terminus font already installed
    font_path = Path("/usr/lib/kbd/consolefonts/ter-v32b.psf.gz")
    if font_path.exists():
        util.print_and_log("Terminus console font already installed.")
    else:
        util.print_and_log("Terminus console font not found. Installing...")
        exit_code = util.run_cmd(
            [ESCALATE, PKG.d, "install", "-y", "terminus-fonts-console"]
        )
        if exit_code == 0:
            util.print_and_log("Terminus console font installed successfully.")
        else:
            util.print_and_log("Failed to install Terminus console font.")

    # Set Terminus as the default console font in /etc/vconsole.conf
    util.print_and_log("Setting Terminus font in /etc/vconsole.conf...")
    exit_code = util.run_cmd(
        [ESCALATE, "sed", "-i", "s/^FONT=.*/FONT=ter-v32b/", "/etc/vconsole.conf"]
    )
    if exit_code != 0:
        util.run_cmd(
            [
                ESCALATE,
                "sh",
                "-c",
                'echo "FONT=ter-v32b" | tee -a /etc/vconsole.conf',
            ]
        )

    # Only try setting font if we are *not* in a graphical environment
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        util.print_and_log("Applying Terminus font to TTY...")
        util.run_cmd([ESCALATE, "setfont", "-C", "/dev/tty1", "ter-v32b"])
    else:
        util.print_and_log("Skipping TTY font setup (graphical session detected).")


def install_fonts():
    """High-level runner: Install all fonts needed."""
    util.print_and_log_header("Installing Fonts")

    install_nerd_fonts()
    install_terminus_console_font()

    # Refresh font cache
    util.print_and_log("Refreshing font cache")
    util.run_cmd(["fc-cache", "-fv"])
    util.print_and_log("Fonts installation complete.")
