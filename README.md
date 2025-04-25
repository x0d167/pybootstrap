# pyBootstrap

Converting my large Fedora bash bootstrap script to python for... reasons...

I don't plan to distrohop often, so I may or may not expand it to be
environment agnostic. This is a super simplistic way to automate my
personal dotfiles and is basically just a toy utility script sitting on my laptop.

## Folder Structure

```
bootstrap/
├── main.py                  # Entry point
├── utils/
│   ├── __init__.py
│   ├── packages.py          # Install, remove, query packages
│   ├── flatpak.py           # Flatpak-specific setup
│   ├── files.py             # Symlinks, dotfile copy/setup
│   ├── services.py          # Enable/disable systemd units
│   └── logging.py           # Unified CLI output/logging
├── config/
│   ├── packages.json        # Lists of packages to install by category
│   ├── flatpaks.json
│   └── services.json
└── README.md                # Usage and layout docs
```

## Alt Structure (wip)

```
bootstrap/
├── __main__.py            # Entry point
├── core/
│   ├── logger.py          # Unified logging
│   ├── prompts.py         # (Optional) interactive / fallback prompts
│   ├── utils.py           # Shared helper functions
├── modules/
│   ├── system.py          # Hostname, locales, basic packages
│   ├── security.py        # Firewall, Portmaster, etc.
│   ├── devtools.py        # Git, editors, CLI tools
│   ├── desktop.py         # Gnome setup, extensions, themes
│   └── cleanup.py         # Orphan packages, bloat removal
├── config/
│   └── defaults.json      # Optional default settings
└── README.md              # Explanation and setup

```
