# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QBrush, QColor

from ui.theme import ModernDarkTheme


class RepoTable(QWidget):
    repo_double_clicked = pyqtSignal(dict)
    sync_selected = pyqtSignal(list)
    reclone_selected = pyqtSignal(list)
    delete_selected = pyqtSignal(list)
    open_folder_selected = pyqtSignal(str)
    open_browser_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.repositories = []
        self.filtered_repositories = []
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
        self.search_input.textChanged.connect(self.apply_filters)

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

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Repository", "Type", "Size", "Status"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.on_double_click)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.table)

        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 11px;")

        status_layout.addWidget(self.stats_label)
        status_layout.addStretch()

        layout.addWidget(status_widget)

    def set_repositories(self, repositories: list):
        self.repositories = repositories
        self.apply_filters()

    def apply_filters(self):
        search_text = self.search_input.text().lower()
        filter_type = self.filter_combo.currentText()

        filtered = []
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

        self.filtered_repositories = filtered
        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.filtered_repositories))

        for i, repo in enumerate(self.filtered_repositories):
            num_item = QTableWidgetItem(str(i + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 0, num_item)

            name_item = QTableWidgetItem(repo.get('name', 'Unknown'))
            self.table.setItem(i, 1, name_item)

            is_private = repo.get('private', False)
            type_text = "🔒 Private" if is_private else "🌍 Public"
            type_item = QTableWidgetItem(type_text)
            if is_private:
                type_item.setForeground(QBrush(QColor(ModernDarkTheme.WARNING_COLOR)))
            else:
                type_item.setForeground(QBrush(QColor(ModernDarkTheme.SUCCESS_COLOR)))
            self.table.setItem(i, 2, type_item)

            size_mb = repo.get('size', 0) / 1024
            size_item = QTableWidgetItem(f"{size_mb:.2f} MB")
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table.setItem(i, 3, size_item)

            local_exists = self._check_local_exists(repo.get('name', ''))
            status_text = "📁 Local" if local_exists else "🌐 Remote"
            status_item = QTableWidgetItem(status_text)
            if not local_exists:
                status_item.setForeground(QBrush(QColor(ModernDarkTheme.INFO_COLOR)))
            self.table.setItem(i, 4, status_item)

        total = len(self.filtered_repositories)
        private_count = sum(1 for r in self.filtered_repositories if r.get('private', False))
        local_count = sum(1 for r in self.filtered_repositories
                          if self._check_local_exists(r.get('name', '')))

        self.stats_label.setText(
            f"Total: {total} | Private: {private_count} | Local: {local_count}"
        )

    def _check_local_exists(self, repo_name: str) -> bool:
        return False

    def set_local_checker(self, checker_func):
        self._check_local_exists = checker_func

    def on_double_click(self, index):
        row = index.row()
        if 0 <= row < len(self.filtered_repositories):
            self.repo_double_clicked.emit(self.filtered_repositories[row])

    def get_selected_repositories(self) -> list:
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        return [self.filtered_repositories[row] for row in selected_rows]

    def show_context_menu(self, position):
        selected = self.get_selected_repositories()
        if not selected:
            return

        menu = QMenu(self.table)

        sync_action = QAction(f"🔄 Sync ({len(selected)})", self)
        sync_action.setToolTip("Clone if missing, update if exists")
        sync_action.triggered.connect(lambda checked, repos=selected: self.sync_selected.emit(repos))
        menu.addAction(sync_action)

        reclone_action = QAction(f"⚠️ Re-clone ({len(selected)})", self)
        reclone_action.setToolTip("Delete local copy and clone again")
        reclone_action.triggered.connect(lambda checked, repos=selected: self.reclone_selected.emit(repos))
        menu.addAction(reclone_action)

        local_repos = [r for r in selected if self._check_local_exists(r.get('name', ''))]
        if local_repos:
            delete_action = QAction(f"🗑️ Delete Local ({len(local_repos)})", self)
            delete_action.setToolTip("Remove local repository folder")
            delete_action.triggered.connect(lambda checked, repos=local_repos: self.delete_selected.emit(repos))
            menu.addAction(delete_action)

        menu.addSeparator()

        if len(selected) == 1:
            repo = selected[0]
            repo_name = repo.get('name', 'Unknown')
            local_exists = self._check_local_exists(repo_name)
            repo_url = repo.get('html_url', repo.get('clone_url', ''))

            if local_exists:
                open_folder_action = QAction("📂 Open Local Folder", self)
                open_folder_action.setToolTip("Open repository folder in file manager")
                open_folder_action.triggered.connect(
                    lambda checked, name=repo_name: self.open_folder_selected.emit(name))
                menu.addAction(open_folder_action)

            if repo_url:
                open_browser_action = QAction("🌐 Open in Browser", self)
                open_browser_action.setToolTip("Open repository on Forgejo web interface")
                open_browser_action.triggered.connect(
                    lambda checked, url=repo_url: self.open_browser_selected.emit(url))
                menu.addAction(open_browser_action)
        else:
            stats_action = QAction(f"📊 {len(selected)} repositories selected", self)
            stats_action.setEnabled(False)
            menu.addAction(stats_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def update_stats(self, total: int, private_count: int, local_count: int):
        self.stats_label.setText(f"Total: {total} | Private: {private_count} | Local: {local_count}")

    def update_repo_status(self, repo_name: str, local_exists: bool):
        for i, repo in enumerate(self.filtered_repositories):
            if repo.get('name') == repo_name:
                repo['local_exists'] = local_exists
                status_text = "📁 Local" if local_exists else "🌐 Remote"
                status_item = QTableWidgetItem(status_text)
                if not local_exists:
                    status_item.setForeground(QBrush(QColor(ModernDarkTheme.INFO_COLOR)))
                self.table.setItem(i, 4, status_item)
                break
