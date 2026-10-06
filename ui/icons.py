# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
from pathlib import Path

from PyQt5.QtGui import QIcon


_ICONS_DIR = Path(__file__).parent.parent / "data" / "icons"


def icon(name: str) -> QIcon:
    path = _ICONS_DIR / name
    if path.exists():
        return QIcon(str(path))
    return QIcon()


class Icons:
    SYNC = "sync.svg"
    UPDATE = "update.svg"
    RECLONE = "reclone.svg"
    DELETE = "delete.svg"
    LOCAL = "local.svg"
    REMOTE = "remote.svg"
    PRIVATE = "private.svg"
    PUBLIC = "public.svg"
    SERVER = "server.svg"
    USER = "user.svg"
    FOLDER_OPEN = "folder-open.svg"
    EXTERNAL = "external.svg"
    REPOS = "repos.svg"
    LIST = "list.svg"
