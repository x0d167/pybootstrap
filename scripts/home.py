from pathlib import Path
from utils import common as util


def setup_home_directories():
    """This will organize the home directory cleanly and update XDG defaults"""
    util.print_and_log_header("Setting up Home Directory Structure")

    home = Path.home()

    # Step 1: Create base folders
    new_dirs = [
        home / "archive",
        home / "bin",
        home / "dev",
        home / "docs",
        home / "media",
        home / "tmp",
        home / "logarchive",
    ]
    for dir in new_dirs:
        if not dir.exists():
            dir.mkdir(parents=True, exist_ok=True)
            util.print_and_log(f"Created {dir}")

    # Step 2: Update user-dirs.dirs mappings
    util.print_and_log("Updating user-dirs.dirs default directories")
    user_dirs = Path.home() / ".config" / "user-dirs.dirs"
    folders_map = {
        "XDG_DESKTOP_DIR": "$HOME/archive/desktop",
        "XDG_DOWNLOAD_DIR": "$HOME/tmp/downloads",
        "XDG_TEMPLATES_DIR": "$HOME/archive/templates",
        "XDG_PUBLICSHARE_DIR": "$HOME/tmp/public",
        "XDG_DOCUMENTS_DIR": "$HOME/docs",
        "XDG_MUSIC_DIR": "$HOME/media/music",
        "XDG_PICTURES_DIR": "$HOME/media/pictures",
        "XDG_VIDEOS_DIR": "$HOME/media/videos",
    }
    if user_dirs.exists():
        with user_dirs.open("r") as file:
            lines = file.readlines()
        user_dirs.with_suffix(".dirs.bak").write_text("".join(lines))

        new_lines = []
        for line in lines:
            for key, path in folders_map.items():
                if line.strip().startswith(key):
                    line = f'{key}="{path}"\n'
            new_lines.append(line)

        with user_dirs.open("w") as file:
            file.writelines(new_lines)

    # Step 3: Move XDG folders into new structure
    move_mapping = {
        "Documents": "docs",
        "Downloads": "tmp",
        "Pictures": "media",
        "Music": "media",
        "Videos": "media",
        "Public": "tmp",
        "Templates": "archive",
        "Desktop": "archive",
    }

    moved_count = 0
    skipped_count = 0

    for old, new in move_mapping.items():
        old_path = home / old
        new_name = old.lower()
        new_path = home / new / new_name

        if old_path.exists():
            # Create parent if missing (just extra safe)
            new_path.parent.mkdir(parents=True, exist_ok=True)

            util.run_cmd(["mv", str(old_path), str(new_path)])
            util.print_and_log(f"Moved {old} -> {new_name}")
            moved_count += 1
        else:
            util.print_and_log(f"Skipping {old}: directory not found.")
            skipped_count += 1

    util.print_and_log(
        f"Finished moving directories: {moved_count} moved, {skipped_count} skipped."
    )

    # Step 4: refresh user-dirs settings
    util.run_cmd(["xdg-user-dirs-update"])

    util.print_and_log("✅ User's Home Directory setup complete.")
