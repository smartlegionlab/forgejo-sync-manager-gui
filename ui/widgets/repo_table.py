# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
from PyQt5.QtWidgets import (
    QTableView, QAbstractItemView, QHeaderView,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QColor, QBrush

from ui.icons import icon, Icons
from ui.theme import ModernDarkTheme


class RepoTableModel(QAbstractTableModel):
    HEADERS = ["#", "Repository", "Type", "Size", "Status"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._repos = []
        self._color_private = QColor(ModernDarkTheme.WARNING_COLOR)
        self._color_public = QColor(ModernDarkTheme.SUCCESS_COLOR)
        self._color_info = QColor(ModernDarkTheme.INFO_COLOR)

    def set_repositories(self, repos):
        self.beginResetModel()
        self._repos = repos
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._repos)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return 5

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        repo = self._repos[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return str(index.row() + 1)
            elif col == 1:
                return repo.get('name', 'Unknown')
            elif col == 2:
                return "Private" if repo.get('private', False) else "Public"
            elif col == 3:
                size_mb = repo.get('size', 0) / 1024
                return f"{size_mb:.2f} MB"
            elif col == 4:
                return "Local" if repo.get('local_exists', False) else "Remote"

        elif role == Qt.DecorationRole:
            if col == 2:
                return icon(Icons.PRIVATE if repo.get('private', False) else Icons.PUBLIC)
            if col == 4:
                return icon(Icons.LOCAL if repo.get('local_exists', False) else Icons.REMOTE)

        elif role == Qt.TextAlignmentRole:
            if col in (0, 3):
                return Qt.AlignCenter | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        elif role == Qt.ForegroundRole:
            if col == 2:
                return QBrush(self._color_private if repo.get('private', False) else self._color_public)
            if col == 4 and not repo.get('local_exists', False):
                return QBrush(self._color_info)

        return None

    def get_repo(self, row):
        if 0 <= row < len(self._repos):
            return self._repos[row]
        return None

    def update_row(self, row):
        if 0 <= row < len(self._repos):
            left = self.index(row, 0)
            right = self.index(row, 4)
            self.dataChanged.emit(left, right)


class RepoTable(QWidget):
    repo_double_clicked = pyqtSignal(dict)
    sync_selected = pyqtSignal(list)
    reclone_selected = pyqtSignal(list)
    delete_selected = pyqtSignal(list)
    open_folder_selected = pyqtSignal(str)
    open_browser_selected = pyqtSignal(str)
    open_repos_root = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.repositories = []
        self.filtered_repositories = []
        self._updating = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(5, 5, 5, 5)
        control_layout.setSpacing(10)

        search_label = QLabel("Search:")
        search_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 11px;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name...")
        self.search_input.setMinimumWidth(200)

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(150)
        self._search_timer.timeout.connect(self.apply_filters)
        self.search_input.textChanged.connect(lambda _: self._search_timer.start())

        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 11px;")

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Public", "Private", "Forks", "Local", "Remote"])
        self.filter_combo.currentTextChanged.connect(self.apply_filters)

        control_layout.addWidget(search_label)
        control_layout.addWidget(self.search_input)
        control_layout.addWidget(filter_label)
        control_layout.addWidget(self.filter_combo)
        control_layout.addStretch()

        layout.addWidget(control_widget)

        self.model = RepoTableModel(self)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(f"""
            QTableView {{
                background-color: {ModernDarkTheme.CARD_BG};
                alternate-background-color: {ModernDarkTheme.ROW_ODD};
                gridline-color: {ModernDarkTheme.BORDER_COLOR};
                color: {ModernDarkTheme.TEXT_PRIMARY};
                selection-background-color: {ModernDarkTheme.ROW_SELECTED};
                selection-color: {ModernDarkTheme.TEXT_PRIMARY};
            }}
            QTableView::item {{
                padding: 4px 6px;
            }}
            QHeaderView::section {{
                background-color: {ModernDarkTheme.CARD_BG};
                color: {ModernDarkTheme.TEXT_PRIMARY};
                border: none;
                border-bottom: 1px solid {ModernDarkTheme.BORDER_COLOR};
                padding: 6px;
            }}
        """)
        self.table.doubleClicked.connect(self.on_double_click)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)
        status_layout.setSpacing(6)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 11px;")

        self.local_link = QLabel("")
        self.local_link.setStyleSheet(f"""
            QLabel {{
                color: {ModernDarkTheme.PRIMARY_COLOR};
                font-size: 11px;
                font-weight: bold;
            }}
            QLabel:hover {{
                color: #1a75ff;
            }}
        """)
        self.local_link.setCursor(Qt.PointingHandCursor)
        self.local_link.mousePressEvent = self.on_local_link_click

        status_layout.addWidget(self.stats_label)
        status_layout.addWidget(self.local_link)
        status_layout.addStretch()

        layout.addWidget(status_widget)

    def on_local_link_click(self, event):
        self.open_repos_root.emit()

    def set_repositories(self, repositories: list):
        self.repositories = repositories
        self.apply_filters()

    def apply_filters(self):
        if self._updating:
            return
        self._updating = True
        try:
            search_text = self.search_input.text().strip().lower()
            filter_type = self.filter_combo.currentText()

            filtered = []
            private_count = 0
            local_count = 0

            for repo in self.repositories:
                if search_text and search_text not in repo.get('name', '').lower():
                    continue
                if filter_type == "Public" and repo.get('private', False):
                    continue
                elif filter_type == "Private" and not repo.get('private', False):
                    continue
                elif filter_type == "Forks" and not repo.get('fork', False):
                    continue
                elif filter_type == "Local" and not repo.get('local_exists', False):
                    continue
                elif filter_type == "Remote" and repo.get('local_exists', False):
                    continue

                filtered.append(repo)
                if repo.get('private', False):
                    private_count += 1
                if repo.get('local_exists', False):
                    local_count += 1

            self.filtered_repositories = filtered
            self.model.set_repositories(filtered)

            self.stats_label.setText(
                f"Total: {len(filtered)} | Private: {private_count} | "
            )
            self.local_link.setText(f"Local: {local_count}")
        finally:
            self._updating = False

    def on_double_click(self, index):
        repo = self.model.get_repo(index.row())
        if repo is not None:
            self.repo_double_clicked.emit(repo)

    def get_selected_repositories(self) -> list:
        rows = sorted({idx.row() for idx in self.table.selectionModel().selectedRows()})
        result = []
        for row in rows:
            repo = self.model.get_repo(row)
            if repo is not None:
                result.append(repo)
        return result

    def show_context_menu(self, position):
        selected = self.get_selected_repositories()
        if not selected:
            return

        menu = QMenu(self.table)

        sync_action = QAction(icon(Icons.SYNC), f"Sync ({len(selected)})", self)
        sync_action.setToolTip("Clone if missing, update if exists")
        sync_action.triggered.connect(lambda checked, repos=selected: self.sync_selected.emit(repos))
        menu.addAction(sync_action)

        reclone_action = QAction(icon(Icons.RECLONE), f"Re-clone ({len(selected)})", self)
        reclone_action.setToolTip("Delete local copy and clone again")
        reclone_action.triggered.connect(lambda checked, repos=selected: self.reclone_selected.emit(repos))
        menu.addAction(reclone_action)

        local_repos = [r for r in selected if r.get('local_exists', False)]
        if local_repos:
            delete_action = QAction(icon(Icons.DELETE), f"Delete Local ({len(local_repos)})", self)
            delete_action.setToolTip("Remove local repository folder")
            delete_action.triggered.connect(lambda checked, repos=local_repos: self.delete_selected.emit(repos))
            menu.addAction(delete_action)

        menu.addSeparator()

        if len(selected) == 1:
            repo = selected[0]
            repo_name = repo.get('name', 'Unknown')
            local_exists = bool(repo.get('local_exists', False))
            repo_url = repo.get('html_url', repo.get('clone_url', ''))

            if local_exists:
                open_folder_action = QAction(icon(Icons.FOLDER_OPEN), "Open Local Folder", self)
                open_folder_action.setToolTip("Open repository folder in file manager")
                open_folder_action.triggered.connect(
                    lambda checked, name=repo_name: self.open_folder_selected.emit(name))
                menu.addAction(open_folder_action)

            if repo_url:
                open_browser_action = QAction(icon(Icons.EXTERNAL), "Open in Browser", self)
                open_browser_action.setToolTip("Open repository on Forgejo web interface")
                open_browser_action.triggered.connect(
                    lambda checked, url=repo_url: self.open_browser_selected.emit(url))
                menu.addAction(open_browser_action)
        else:
            stats_action = QAction(icon(Icons.LIST), f" {len(selected)} repositories selected", self)
            stats_action.setEnabled(False)
            menu.addAction(stats_action)

        menu.exec_(self.table.viewport().mapToGlobal(position))

    def update_stats(self, total: int, private_count: int, local_count: int):
        self.stats_label.setText(f"Total: {total} | Private: {private_count} | ")
        self.local_link.setText(f"Local: {local_count}")

    def update_repo_status(self, repo_name: str, local_exists: bool):
        for row, repo in enumerate(self.filtered_repositories):
            if repo.get('name') == repo_name:
                repo['local_exists'] = local_exists
                self.model.update_row(row)
                break
