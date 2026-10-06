# forgejo-sync-manager-gui <sup>v1.0.8</sup>

Desktop GUI application for batch synchronization of Forgejo repositories to local machine.

---

[![GitHub top language](https://img.shields.io/github/languages/top/smartlegionlab/forgejo-sync-manager-gui)](https://github.com/smartlegionlab/forgejo-sync-manager-gui)
[![GitHub license](https://img.shields.io/github/license/smartlegionlab/forgejo-sync-manager-gui)](https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/smartlegionlab/forgejo-sync-manager-gui)](https://github.com/smartlegionlab/forgejo-sync-manager-gui/)
[![GitHub stars](https://img.shields.io/github/stars/smartlegionlab/forgejo-sync-manager-gui?style=social)](https://github.com/smartlegionlab/forgejo-sync-manager-gui/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/smartlegionlab/forgejo-sync-manager-gui?style=social)](https://github.com/smartlegionlab/forgejo-sync-manager-gui/network/members)

---

## ⚠️ Disclaimer

**By using this software, you agree to the full disclaimer terms.**

**Summary:** Software provided "AS IS" without warranty. You assume all risks.

**Full legal disclaimer:** See [DISCLAIMER.md](https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/DISCLAIMER.md)

---

## Features

- Modern dark theme GUI interface
- Automatic authentication via personal access token
- Batch repository cloning and updating with real-time progress tracking
- Visual repository list with search and filter capabilities
- Full repository recloning option
- Local repository deletion
- Batch delete all local repositories with progress tracking
- One-click open in browser or local folder
- Persistent configuration storage
- Multi-repository selection for batch operations

## Requirements

- Python 3.8+
- Git
- Forgejo server with API access
- PyQt5

## Installation

There are **two independent ways** to use this application:

- **Run from source** — clone the repo, create a virtual environment, launch manually. Nothing is installed system-wide.
- **Install system-wide** — one command creates a menu entry. Desktop shortcut is opt-in.

Choose one. They are not meant to be combined.

### Option 1 — Run from Source (no system install)

Use this if you just want to try the app or run it manually from a folder.

**Requirements:** Python 3.8+, git.

```bash
# 1. Clone the repository
git clone https://github.com/smartlegionlab/forgejo-sync-manager-gui.git
cd forgejo-sync-manager-gui

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Launch the app
python app.py
```

To run it again later:

```bash
cd forgejo-sync-manager-gui
source venv/bin/activate
python app.py
```

Nothing is installed system-wide. The app runs from this folder.

### Option 2 — Install System-Wide (recommended)

Use this if you want the app in your application menu.

**Requirements:** Python 3.8+, git, curl, Linux desktop with `.desktop` support.

#### One-command install

```bash
curl -fsSL https://raw.githubusercontent.com/smartlegionlab/forgejo-sync-manager-gui/master/install.sh | bash
```

**What the installer does:**

1. Downloads the source code from GitHub.
2. Installs the application to `~/.local/share/forgejo-sync-manager-gui/`.
   No root, no sudo — everything lives inside your home directory.
3. Creates a dedicated Python virtual environment at
   `~/.local/share/forgejo-sync-manager-gui/venv/` and installs dependencies into it.
4. Registers the app in your desktop environment by creating
   `~/.local/share/applications/forgejo-sync-manager-gui.desktop`.
5. Refreshes the desktop database so the menu entry appears without a full re-login on most systems.

**Launch after install:**
- Application menu → **Forgejo Sync Manager**

**Desktop shortcut (opt-in):**

By default, no Desktop shortcut is created. This is intentional — on GNOME
(default on Ubuntu), desktop icons are hidden by default, which would make
a shortcut invisible and confusing.

To also create a Desktop shortcut during install, pass the
`SPM_CREATE_DESKTOP_SHORTCUT=1` environment variable to **bash** — the
second command in the pipeline:

```bash
curl -fsSL https://raw.githubusercontent.com/smartlegionlab/forgejo-sync-manager-gui/master/install.sh | SPM_CREATE_DESKTOP_SHORTCUT=1 bash
```

Or export it first, then run the normal installer:

```bash
export SPM_CREATE_DESKTOP_SHORTCUT=1
curl -fsSL https://raw.githubusercontent.com/smartlegionlab/forgejo-sync-manager-gui/master/install.sh | bash
```

> **Note:** Writing `SPM_CREATE_DESKTOP_SHORTCUT=1 curl ... | bash` does
> **not** work — in a shell pipeline, an environment variable prefix applies
> only to the command on the **left** side of the `|`. The variable never
> reaches `bash`, which is on the right side. Pass it to `bash` directly, or
> `export` it beforehand.

**Notes:**
- On GNOME (default on Ubuntu), desktop icons may be hidden by default. Enable Desktop Icons in GNOME Tweaks to see the shortcut.
- The Desktop shortcut may show an **"Unsecured Application Launcher"** warning. Right-click → **Allow Launching** (one-time action).
- If the menu entry does not appear immediately, log out and back in.

#### Alternative — install from a cloned repo

If you already cloned the repository, you can run the installer locally:

```bash
cd forgejo-sync-manager-gui
./install.sh
```

It works the same way. It ignores any local `venv/` and creates its own under `~/.local/share/forgejo-sync-manager-gui/venv/`.

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/smartlegionlab/forgejo-sync-manager-gui/master/uninstall.sh | bash
```

**What the uninstaller removes:**
- `~/.local/share/forgejo-sync-manager-gui/` — the application and its venv
- `~/.local/share/applications/forgejo-sync-manager-gui.desktop` — the menu entry
- `~/Desktop/forgejo-sync-manager-gui.desktop` — the Desktop shortcut (if present)

**What the uninstaller never touches:**
- `~/forgejo-sync-manager/config.json` — your connection settings.
  It is your data. Only you decide what to do with it.

If you want to remove your configuration as well, run after uninstall:

```bash
rm -rf ~/forgejo-sync-manager
```

### Installation Paths

| Item                       | Path                                                                  |
|----------------------------|-----------------------------------------------------------------------|
| Application files          | `~/.local/share/forgejo-sync-manager-gui/`                            |
| Virtual environment        | `~/.local/share/forgejo-sync-manager-gui/venv/`                       |
| Application menu entry     | `~/.local/share/applications/forgejo-sync-manager-gui.desktop`        |
| Desktop shortcut (opt-in)  | `~/Desktop/forgejo-sync-manager-gui.desktop`                          |
| User data (config)         | `~/forgejo-sync-manager/config.json`                                  |

---

## Desktop Integration (Linux)

> **Note:** If you installed the app via `install.sh`, the application menu
> entry is already created automatically. The in-app option described below
> is useful when you run the app manually from a custom location, or when
> you want to add a Desktop shortcut on demand. It is also the recommended
> way for development: it creates a shortcut pointing to the **currently
> running instance** (your working copy), not to a copy under
> `~/.local/share/`.

**Creating Application Shortcuts:**

The application allows you to create desktop entries directly from the menu:

1. **Go to File → Create Desktop Entry**
2. **Choose locations:**
   - ✓ Application Menu (`~/.local/share/applications/`) - adds to system app menu
   - □ Desktop (`~/Desktop/`) - creates shortcut on desktop
3. **Click "Create Entry"**

**What happens:**
- Creates `.desktop` file(s) with proper configuration
- Sets executable permissions automatically
- Uses application icon if available

**After creation:**
- **Application Menu**: Log out and back in (or restart desktop) for entry to appear
- **Desktop shortcut**: May show "Unsecured Application Launcher" warning
  - Right-click on shortcut → "Allow Launching" or "Trust"
  - This is a one-time security confirmation

**Note:** This feature is only available on Linux systems with desktop environments that support `.desktop` files (GNOME, KDE, XFCE, etc.).

---

## Usage

```bash
python app.py
```

## Configuration

On first run, the setup dialog will guide you through:

1. Server URL (e.g., `http://localhost:3000`)
2. Personal access token with `read:repository` and `read:user` scopes

Configuration is stored in `~/forgejo-sync-manager/config.json`

## GUI Interface

### Main Window Components

- **Top Panel**: Application title and description
- **Info Panel**: Connection status, user info (clickable), server URL (clickable), repository statistics
- **Repository Table**: List of all repositories with columns:
  - `#` - Index number
  - `Repository` - Repository name
  - `Type` - Public or Private
  - `Size` - Repository size in MB
  - `Status` - Local or Remote
- **Search & Filter**: Search by name, filter by Public/Private/Forks/Local/Remote
- **Action Buttons**:
  - `Sync All` - Clone missing repositories and update all local copies
  - `Update Only` - Update only already cloned repositories
  - `Re-clone All` - Delete all local copies and clone again from server
  - `Delete All` - Delete ALL local repository copies with progress tracking

### Context Menu (Right-click on repository)

- `Sync` - Clone if missing, update if exists
- `Re-clone` - Delete local copy and clone again
- `Delete Local` - Remove local repository folder (for local repositories only)
- `Open Local Folder` - Open repository folder in file manager (single selection)
- `Open in Browser` - Open repository on Forgejo web interface (single selection)

### Keyboard Shortcuts

| Shortcut       | Action                            |
|----------------|-----------------------------------|
| `Ctrl+Shift+S` | Sync All Repositories             |
| `Ctrl+Shift+U` | Update Only Existing Repositories |
| `Ctrl+Shift+R` | Re-clone All Repositories         |
| `Ctrl+Shift+D` | Delete All Local Repositories     |
| `Ctrl+Q`       | Exit Application                  |
| `Ctrl+,`       | Open Settings                     |
| `Ctrl+/`       | Show Keyboard Shortcuts           |
| `Ctrl+Shift+A` | Show About Dialog                 |

### Information Dialogs

- **Click on username** - Shows user information dialog with statistics
- **Click on server URL** - Opens Forgejo server in default browser

## Synchronization Dialog

When starting any sync operation, a dialog appears showing:
- Real-time progress bar
- Current repository being processed
- Operation log with timestamps
- Summary statistics upon completion

## Delete All Dialog

When clicking the "Delete All" button, a dialog appears showing:
- Real-time progress bar
- Current repository being deleted
- Operation log with timestamps
- Summary statistics upon completion (deleted/not found/failed)
- Cancel option to stop the operation

## How It Works

1. **Authentication**: Token-based authentication via Forgejo API
2. **Repository Discovery**: Fetches complete repository list with pagination (50 per page)
3. **Sync Operations**: Uses authenticated URLs with embedded token for Git operations
4. **Real-time UI Updates**: Repository status changes immediately after each successful operation

## Screenshots

![forgejo-sync-manager-gui](https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/data/images/logo.png)

---

## Ecosystem

This project is part of the [Repository Management Ecosystem](https://smartlegionlab.github.io/ecosystems/repository-management-ecosystem.html) — a family of applications and libraries for GitHub / Forgejo automation: sync, backup, and SSH management.

### Applications

| Application                                                                                              | Description                                                                                 |
|----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **[Smart Repository Manager GUI](https://github.com/smartlegionlab/smart-repository-manager-gui)**       | GitHub repository management with visual interface, multi-user support, batch operations    |
| **[Smart Repository Manager CLI](https://github.com/smartlegionlab/smart-repository-manager-cli)**       | GitHub repository management from the command line                                          |
| **[Forgejo Sync Manager GUI](https://github.com/smartlegionlab/forgejo-sync-manager-gui)** (this)        | Desktop GUI for batch synchronization of Forgejo repositories                               |
| **[Forgejo Sync Manager CLI](https://github.com/smartlegionlab/forgejo-sync-manager-cli)**               | Command-line Forgejo sync tool                                                              |
| **[GitHub Repos Backup Tools](https://github.com/smartlegionlab/github-repos-backup-tools)**             | Automated backup of GitHub repositories and GISTs                                           |
| **[GitHub SSH Key Manager](https://github.com/smartlegionlab/github-ssh-key)**                           | Manage GitHub SSH keys from the command line                                                |

### Libraries

| Library                                                                                              | Description                                                       |
|------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| **[forgejo-sync-manager-core](https://github.com/smartlegionlab/forgejo-sync-manager-core)**         | Universal core library for Forgejo repository synchronization     |
| **[smart-repository-manager-core](https://github.com/smartlegionlab/smart-repository-manager-core)** | Python library for managing Git repositories with SSH validation  |

### Powered By

This application is built on top of:

| Library                                                                                      | Description                                                   | Version   |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------------|-----------|
| **[forgejo-sync-manager-core](https://github.com/smartlegionlab/forgejo-sync-manager-core)** | Universal core library for Forgejo repository synchronization | v1.0.2    |
| **PyQt5**                                                                                    | Python bindings for Qt5 framework                             | ≥5.15.9   |
| **requests**                                                                                 | HTTP library for Python                                       | ≥2.31.0   |

### Related Projects

| Project                            | Description                                        | Repository                                                                   |
|------------------------------------|----------------------------------------------------|------------------------------------------------------------------------------|
| **forgejo-sync-manager-cli**       | Command-line interface for batch synchronization   | [GitHub](https://github.com/smartlegionlab/forgejo-sync-manager-cli)         |
| **forgejo-sync-manager-core**      | Universal core library                             | [GitHub](https://github.com/smartlegionlab/forgejo-sync-manager-core)        |
| **smart-repository-manager-gui**   | GitHub repository management GUI                   | [GitHub](https://github.com/smartlegionlab/smart-repository-manager-gui)     |
| **smart-repository-manager-cli**   | GitHub repository management CLI                   | [GitHub](https://github.com/smartlegionlab/smart-repository-manager-cli)     |
| **smart-repository-manager-core**  | Python core library for Git repositories           | [GitHub](https://github.com/smartlegionlab/smart-repository-manager-core)    |
| **github-repos-backup-tools**      | Automated backup of GitHub repositories and GISTs  | [GitHub](https://github.com/smartlegionlab/github-repos-backup-tools)        |
| **github-ssh-key**                 | GitHub SSH key manager                             | [GitHub](https://github.com/smartlegionlab/github-ssh-key)                   |

## See Also

- **[forgejo-sync-manager-cli](https://github.com/smartlegionlab/forgejo-sync-manager-cli)** — If you prefer a command-line interface
- **[forgejo-sync-manager-core](https://github.com/smartlegionlab/forgejo-sync-manager-core)** — Core library for custom implementations
- **[Smart Repository Manager GUI](https://github.com/smartlegionlab/smart-repository-manager-gui)** — If you need GitHub (not Forgejo) repository management
- **[GitHub Repos Backup Tools](https://github.com/smartlegionlab/github-repos-backup-tools)** — For backing up all your GitHub repositories and GISTs
- **[Repository Management Ecosystem](https://smartlegionlab.github.io/ecosystems/repository-management-ecosystem.html)** — Full ecosystem overview

---

## License

[BSD 3-Clause License](https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/LICENSE)

Copyright (©) 2026, [Alexander Suvorov](https://github.com/smartlegionlab)
All rights reserved.

