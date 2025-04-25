# pybootstrap

Converting my large Fedora bash bootstrap script to python for... reasons...

I don't plan to distrohop often, so I may or may not expand it to be
environment agnostic. This is a super simplistic way to automate my
personal dotfiles and is basically just a toy utility script sitting on my laptop.

Honestly, the final project structure will depend. I've already deviated from
the structure outlined below. Let's just say, that's the initial gut check, and
we'll see what we see. Right now I'm just replicating my scripts and testing them.
When I have it all, I'll decide what makes sense.

Plan is to be as low stress as my current bash scripts. Spin up a new system and
run it. It should organize my home directory the way I like, install all the
packages I care about, set up my system the way I like (firewall, systemd schedules,
port monitoring, vpn, device maintenance schedules, keybindings, etc), and then
set up my dotfiles so I feel right at home with my tools. It should be a set it
and forget it, and all I need to do after is log into things and do the finishing
touches.

## Project Structure

```bash
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

```bash
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
