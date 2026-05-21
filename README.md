# forgejo-sync-manager-gui <sup>v1.0.1</sup>

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
- One-click open in browser or local folder
- Persistent configuration storage
- Multi-repository selection for batch operations

## Requirements

- Python 3.8+
- Git
- Forgejo server with API access
- PyQt6

## Installation

```bash
git clone https://github.com/smartlegionlab/forgejo-sync-manager-gui.git
cd forgejo-sync-manager-gui
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

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
  - `Type` - Public 🔒 or Private 🌍
  - `Size` - Repository size in MB
  - `Status` - Local 📁 or Remote 🌐
- **Search & Filter**: Search by name, filter by Public/Private/Forks/Local/Remote
- **Action Buttons**:
  - `Sync All` - Clone missing repositories and update all local copies
  - `Update Only` - Update only already cloned repositories
  - `Re-clone All` - Delete all local copies and clone again from server

### Context Menu (Right-click on repository)

- `Sync` - Clone if missing, update if exists
- `Re-clone` - Delete local copy and clone again
- `Delete Local` - Remove local repository folder (for local repositories only)
- `Open Local Folder` - Open repository folder in file manager (single selection)
- `Open in Browser` - Open repository on Forgejo web interface (single selection)

### Keyboard Shortcuts

### Keyboard Shortcuts

| Shortcut       | Action                            |
|----------------|-----------------------------------|
| `Ctrl+Shift+S` | Sync All Repositories             |
| `Ctrl+Shift+U` | Update Only Existing Repositories |
| `Ctrl+Shift+R` | Re-clone All Repositories         |
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

## How It Works

1. **Authentication**: Token-based authentication via Forgejo API
2. **Repository Discovery**: Fetches complete repository list with pagination (50 per page)
3. **Sync Operations**: Uses authenticated URLs with embedded token for Git operations
4. **Real-time UI Updates**: Repository status changes immediately after each successful operation

## Screenshots

![forgejo-sync-manager-gui](https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/data/images/logo.png)

## License

[BSD 3-Clause License](https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/LICENSE)

Copyright (©) 2026, [Alexander Suvorov](https://github.com/smartlegionlab)
All rights reserved.

---

## Powered By

This application is built on top of:

| Library                                                                                      | Description                                                   | Version |
|----------------------------------------------------------------------------------------------|---------------------------------------------------------------|---------|
| **[forgejo-sync-manager-core](https://github.com/smartlegionlab/forgejo-sync-manager-core)** | Universal core library for Forgejo repository synchronization | v1.0.0  |
| **PyQt6**                                                                                    | Python bindings for Qt6 framework                             | ≥6.5.0  |
| **requests**                                                                                 | HTTP library for Python                                       | ≥2.31.0 |

## Related Projects

| Project                       | Description                                      | Repository                                                            |
|-------------------------------|--------------------------------------------------|-----------------------------------------------------------------------|
| **forgejo-sync-manager-cli**  | Command-line interface for batch synchronization | [GitHub](https://github.com/smartlegionlab/forgejo-sync-manager-cli)  |
| **forgejo-sync-manager-core** | Universal core library                           | [GitHub](https://github.com/smartlegionlab/forgejo-sync-manager-core) |

## See Also

- **[forgejo-sync-manager-cli](https://github.com/smartlegionlab/forgejo-sync-manager-cli)** - If you prefer command-line interface
- **[forgejo-sync-manager-core](https://github.com/smartlegionlab/forgejo-sync-manager-core)** - Core library for custom implementations
