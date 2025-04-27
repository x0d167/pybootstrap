---
# 📦 pybootstrap

A simple, modular Python bootstrap script for setting up a clean Fedora laptop environment.
---

## 🛠 What it Does

- Organizes my Home directory structure
- Updates and upgrades my Fedora system
- Adds important repositories (RPM Fusion, Mullvad, 1Password, ProtonVPN, etc.)
- Installs core system and development packages (DNF, Flatpak)
- Installs and organizes Nerd Fonts
- Applies security hardening:
  - Sets up UFW firewall
  - Applies sysctl network settings
  - Enables Fail2ban
  - Installs Portmaster
- Final cleanup and system refresh

---

## 📂 Project Structure

```text
pybootstrap/
├── main.py              # Master orchestrator
├── README.md
├── config/
│   └── packages.json    # DNF and Flatpak package lists
├── scripts/
│   ├── fonts.py
│   ├── home.py
│   ├── packages.py
│   ├── repo.py
│   ├── system.py
│   └── security.py
└── utils/
    ├── aliases.py
    ├── common.py
    ├── 1password.txt    # Repo template
    └── mullvad.txt      # Repo template
```

---

## 🚀 How to Run

> ⚡ Important: This script assumes a clean Fedora install, and will modify your system configuration.

1. Clone or download this repository
2. Open a terminal in the `pybootstrap/` directory
3. Make sure you have Python 3 installed
4. Run:

```bash
python3 main.py
```

✅ Done! The system will walk through each setup stage automatically and log it.

---

## ⚠️ Warnings

- This script assumes **you want opinionated defaults** for directory layout, security, and installed packages.
- You should review the `scripts/` and `config/` folders first if you want to customize.
- While it _should_ be safe, **always have a backup** before using automation like this on a fresh system.

---

## 🧠 Notes

- Fedora is assumed, but could be adapted to other RPM-based distros.
- Some error handling is intentionally light — this is designed for **personal use**, not public distribution.
- After bootstrap, you should manually configure:
  - rkhunter
  - lynis
  - any desktop environment tweaks

---

# 🎯 Final Thoughts

This project was built as a learning exercise to deepen skills in:

- Python
- Linux automation
- Project structuring
- Modular scripting philosophy

And it's designed to evolve over time.
