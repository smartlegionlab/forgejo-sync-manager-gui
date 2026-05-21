# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
import os
import subprocess

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QStatusBar, QApplication,
    QDialog, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QKeySequence

from core.config import ConfigManager
from core.auth import ForgejoAuth
from core.api_client import ForgejoAPIClient
from core.sync_manager import SyncManager

from ui.theme import ModernDarkTheme
from ui.widgets.repo_table import RepoTable
from ui.dialogs.setup_dialog import SetupDialog
from ui.dialogs.sync_dialog import SyncDialog
from ui.dialogs.about_dialog import AboutDialog


class LoadWorker(QThread):
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(object, object, list)
    error = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self._is_running = True

    def run(self):
        try:
            self.progress.emit("Connecting to Forgejo...", 20)

            auth = ForgejoAuth(
                token=self.config.get("token"),
                server_url=self.config.get("server_url"),
                username=self.config.get("username")
            )

            client = ForgejoAPIClient(auth)

            self.progress.emit("Getting user info...", 40)
            user_info = client.get_user_info()
            auth.username = user_info.get('login', '')

            self.progress.emit("Loading repositories...", 60)
            repositories = client.get_user_repos()

            self.progress.emit("Creating sync manager...", 80)
            sync_manager = SyncManager(auth)

            self.progress.emit("Checking local copies...", 90)
            for repo in repositories:
                if not self._is_running:
                    return
                repo_name = repo.get('name', '')
                repo_path = sync_manager.repos_dir / repo_name
                repo['local_exists'] = repo_path.exists() and (repo_path / '.git').exists()

            self.progress.emit("Done!", 100)
            self.finished.emit(auth, client, repositories)

        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._is_running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.auth = None
        self.client = None
        self.sync_manager = None
        self.repositories = []
        self.user_info = None
        self.load_worker = None
        self.preloader_dialog = None
        self.animation_timer = None
        self.animation_counter = 0

        self.setWindowTitle(f"{ConfigManager.APP_FULL_NAME} v{ConfigManager.VERSION}")
        self.setMinimumSize(1000, 700)

        self.setup_ui()
        self.setup_menu()
        self.center_on_screen()

        QTimer.singleShot(100, self.initialize)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header = self.create_header()
        main_layout.addWidget(header)

        self.info_panel = self.create_info_panel()
        main_layout.addWidget(self.info_panel)

        self.repo_table = RepoTable()
        self.repo_table.set_local_checker(self.check_local_exists)
        self.repo_table.repo_double_clicked.connect(self.on_repo_double_click)
        self.repo_table.sync_selected.connect(self.sync_selected)
        self.repo_table.reclone_selected.connect(self.reclone_selected)
        self.repo_table.open_folder_selected.connect(self.open_local_folder)
        self.repo_table.open_browser_selected.connect(self.open_in_browser)
        self.repo_table.delete_selected.connect(self.delete_local_repositories)
        main_layout.addWidget(self.repo_table, 1)

        button_bar = self.create_button_bar()
        main_layout.addWidget(button_bar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def delete_local_repositories(self, repositories: list):
        if not repositories:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete local copies of {len(repositories)} repositories?\n\nThis action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        deleted_count = 0
        for repo in repositories:
            repo_name = repo.get('name', '')
            repo_path = self.sync_manager.repos_dir / repo_name

            if repo_path.exists():
                try:
                    import shutil
                    shutil.rmtree(repo_path)
                    deleted_count += 1
                    self.update_repo_status_in_table(repo_name, False)
                except Exception as e:
                    print(f"Error deleting {repo_name}: {e}")

        if deleted_count > 0:
            QMessageBox.information(self, "Success", f"Deleted {deleted_count} local copies")

    def open_in_browser(self, url: str):
        import webbrowser
        if url:
            webbrowser.open(url)

    def create_header(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        title = QLabel(ConfigManager.APP_FULL_NAME)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Forgejo Repository Synchronization Tool")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return widget

    def create_info_panel(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {ModernDarkTheme.CARD_BG};
            }}
        """)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(30)

        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        self.status_icon = QLabel("⚫")
        self.status_icon.setStyleSheet(f"color: {ModernDarkTheme.ERROR_COLOR}; font-size: 14px;")
        left_layout.addWidget(self.status_icon)

        self.user_label = QLabel("👤 Not connected")
        self.user_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernDarkTheme.PRIMARY_COLOR};
                font-weight: bold;
                font-size: 13px;
            }}
            QLabel:hover {{
                color: #1a75ff;
            }}
        """)
        self.user_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_label.mousePressEvent = self.on_user_click
        left_layout.addWidget(self.user_label)

        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        server_icon = QLabel("🌐")
        server_icon.setStyleSheet("font-size: 12px;")
        center_layout.addWidget(server_icon)

        self.server_label = QLabel("")
        self.server_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernDarkTheme.PRIMARY_COLOR};
                font-size: 12px;
            }}
            QLabel:hover {{
                color: #1a75ff;
            }}
        """)
        self.server_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.server_label.mousePressEvent = self.on_server_click
        center_layout.addWidget(self.server_label)

        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 11px;")

        layout.addWidget(left_widget)
        layout.addWidget(center_widget)
        layout.addStretch()
        layout.addWidget(self.stats_label)

        return widget

    def on_user_click(self, event):
        self.show_user_info_dialog()

    def on_server_click(self, event):
        import webbrowser
        if self.auth and self.auth.server_url:
            webbrowser.open(self.auth.server_url)

    def show_user_info_dialog(self):
        if not self.auth:
            QMessageBox.warning(self, "Warning", "No user information available")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("User Information")
        dialog.setMinimumSize(400, 250)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        name_label = QLabel(self.auth.username)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        layout.addWidget(name_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {ModernDarkTheme.BORDER_COLOR};")
        layout.addWidget(separator)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        server_info = QLabel(f"🌐 Server: {self.auth.server_url}")
        server_info.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-size: 12px;")
        info_layout.addWidget(server_info)

        repos_count = QLabel(f"📚 Repositories: {len(self.repositories)}")
        repos_count.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-size: 12px;")
        info_layout.addWidget(repos_count)

        private_count = sum(1 for r in self.repositories if r.get('private', False))
        private_info = QLabel(f"🔒 Private: {private_count}")
        private_info.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-size: 12px;")
        info_layout.addWidget(private_info)

        local_count = sum(1 for r in self.repositories if r.get('local_exists', False))
        local_info = QLabel(f"📁 Local: {local_count}")
        local_info.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-size: 12px;")
        info_layout.addWidget(local_info)

        layout.addLayout(info_layout)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(35)
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernDarkTheme.PRIMARY_COLOR};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #1a75ff;
            }}
        """)
        layout.addWidget(close_btn)

        dialog.exec()

    def create_button_bar(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)

        self.sync_btn = QPushButton("🔄 Sync All")
        self.sync_btn.clicked.connect(self.sync_all)
        self.sync_btn.setEnabled(False)
        self.sync_btn.setToolTip("Clone missing repositories and update all local copies")

        self.update_btn = QPushButton("📥 Update Only")
        self.update_btn.clicked.connect(self.update_only)
        self.update_btn.setEnabled(False)
        self.update_btn.setToolTip("Update only already cloned repositories (no new clones)")

        self.reclone_btn = QPushButton("⚠️ Re-clone All")
        self.reclone_btn.clicked.connect(self.reclone_all)
        self.reclone_btn.setEnabled(False)
        self.reclone_btn.setToolTip("Delete all local copies and clone again from server")

        layout.addWidget(self.sync_btn)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.reclone_btn)
        layout.addStretch()

        return widget

    def setup_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        sync_action = QAction("&Sync All", self)
        sync_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        sync_action.triggered.connect(self.sync_all)
        file_menu.addAction(sync_action)

        update_action = QAction("&Update Only", self)
        update_action.setShortcut(QKeySequence("Ctrl+Shift+U"))
        update_action.triggered.connect(self.update_only)
        file_menu.addAction(update_action)

        reclone_action = QAction("&Re-clone All", self)
        reclone_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        reclone_action.triggered.connect(self.reclone_all)
        file_menu.addAction(reclone_action)

        file_menu.addSeparator()

        desktop_action = QAction("Create Desktop Entry...", self)
        desktop_action.triggered.connect(self.create_desktop_entry)
        file_menu.addAction(desktop_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)

        help_menu = menubar.addMenu("&Help")

        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence("Ctrl+/"))
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)

        help_menu.addSeparator()

        about_action = QAction("&About", self)
        about_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def initialize(self):
        config = self.config_manager.load()

        if config and config.get("token"):
            self.show_preloader("Initializing...")
            self.start_load_worker(config)
        else:
            self.open_setup()

    def show_shortcuts_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Keyboard Shortcuts")
        dialog.setMinimumSize(500, 450)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Keyboard Shortcuts")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        layout.addWidget(title)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {ModernDarkTheme.BORDER_COLOR};")
        layout.addWidget(separator)

        shortcuts = [
            ("File Operations", ""),
            ("Ctrl+Shift+S", "Sync All Repositories"),
            ("Ctrl+Shift+U", "Update Only Existing Repositories"),
            ("Ctrl+Shift+R", "Re-clone All Repositories"),
            ("Ctrl+Q", "Exit Application"),
            ("", ""),
            ("Tools", ""),
            ("Ctrl+,", "Open Settings"),
            ("", ""),
            ("Help", ""),
            ("Ctrl+/", "Show Keyboard Shortcuts"),
            ("Ctrl+Shift+A", "Show About Dialog"),
        ]

        for key, desc in shortcuts:
            if not key and not desc:
                layout.addSpacing(10)
                continue

            if desc == "":
                category = QLabel(key)
                category_font = QFont()
                category_font.setBold(True)
                category.setFont(category_font)
                category.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; margin-top: 10px;")
                layout.addWidget(category)
            else:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(20, 5, 20, 5)

                key_label = QLabel(key)
                key_label.setStyleSheet(f"""
                    color: {ModernDarkTheme.PRIMARY_COLOR};
                    font-family: monospace;
                    font-size: 12px;
                    font-weight: bold;
                """)
                key_label.setMinimumWidth(140)

                desc_label = QLabel(desc)
                desc_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 12px;")

                item_layout.addWidget(key_label)
                item_layout.addWidget(desc_label)
                item_layout.addStretch()

                layout.addWidget(item_widget)

        layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(35)
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernDarkTheme.PRIMARY_COLOR};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: #1a75ff;
            }}
        """)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()

    def start_load_worker(self, config):
        self.load_worker = LoadWorker(config)
        self.load_worker.progress.connect(self.on_load_progress)
        self.load_worker.finished.connect(self.on_load_finished)
        self.load_worker.error.connect(self.on_load_error)
        self.load_worker.start()

    def on_load_progress(self, message: str, percent: int):
        self.update_preloader_message(message, percent)

    def on_load_finished(self, auth, client, repositories):
        self.auth = auth
        self.client = client
        self.repositories = repositories
        self.user_info = {"login": auth.username}
        self.sync_manager = SyncManager(auth)

        self.repo_table.set_repositories(self.repositories)

        self.update_info_panel()
        self.update_repo_stats()

        self.sync_btn.setEnabled(True)
        self.update_btn.setEnabled(True)
        self.reclone_btn.setEnabled(True)

        self.hide_preloader()
        self.status_label.setText(f"Ready - {len(self.repositories)} repositories loaded")

    def on_load_error(self, error_msg: str):
        self.hide_preloader()
        QMessageBox.critical(self, "Error", f"Failed to connect: {error_msg}")
        self.open_setup()

    def update_repo_stats(self):
        total = len(self.repositories)
        private_count = sum(1 for r in self.repositories if r.get('private', False))
        local_count = sum(1 for r in self.repositories if r.get('local_exists', False))
        self.stats_label.setText(f"📊 Total: {total} | 🔒 Private: {private_count} | 📁 Local: {local_count}")
        self.repo_table.update_stats(total, private_count, local_count)

    def update_info_panel(self):
        self.user_label.setText(f"👤 @{self.auth.username}")
        self.server_label.setText(self.auth.server_url)
        self.status_icon.setText("🟢")
        self.status_icon.setStyleSheet(f"color: {ModernDarkTheme.SUCCESS_COLOR}; font-size: 14px;")

    def check_local_exists(self, repo_name: str) -> bool:
        if not self.sync_manager:
            return False
        return self.sync_manager.repo_exists_locally(repo_name)

    def update_repo_status_in_table(self, repo_name: str, local_exists: bool):
        for repo in self.repositories:
            if repo.get('name') == repo_name:
                repo['local_exists'] = local_exists
                break
        self.repo_table.update_repo_status(repo_name, local_exists)
        self.update_repo_stats()

    def sync_all(self):
        if not self.sync_manager or not self.repositories:
            return

        dialog = SyncDialog(self.sync_manager, self.repositories, "sync", self)
        dialog.repo_status_updated.connect(self.update_repo_status_in_table)
        dialog.exec()

    def update_only(self):
        if not self.sync_manager or not self.repositories:
            return

        repos_to_update = [
            r for r in self.repositories
            if self.check_local_exists(r.get('name', ''))
        ]

        if not repos_to_update:
            QMessageBox.information(self, "Info", "No local repositories to update")
            return

        dialog = SyncDialog(self.sync_manager, repos_to_update, "sync", self)
        dialog.repo_status_updated.connect(self.update_repo_status_in_table)
        dialog.exec()

    def sync_selected(self, repositories: list):
        if not repositories:
            return
        dialog = SyncDialog(self.sync_manager, repositories, "sync", self)
        dialog.repo_status_updated.connect(self.update_repo_status_in_table)
        dialog.exec()

    def reclone_selected(self, repositories: list):
        if not repositories:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Re-clone",
            f"Re-clone {len(repositories)} repositories?\n\n"
            f"This will DELETE local copies and clone again.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            dialog = SyncDialog(self.sync_manager, repositories, "reclone", self)
            dialog.repo_status_updated.connect(self.update_repo_status_in_table)
            dialog.exec()

    def reclone_all(self):
        if not self.repositories:
            return

        reply = QMessageBox.warning(
            self,
            "Confirm Re-clone All",
            f"Re-clone ALL {len(self.repositories)} repositories?\n\n"
            f"This will DELETE all local copies and clone them again.\n"
            f"This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            dialog = SyncDialog(self.sync_manager, self.repositories, "reclone", self)
            dialog.repo_status_updated.connect(self.update_repo_status_in_table)
            dialog.exec()

    def open_local_folder(self, repo_name: str):
        if not self.sync_manager:
            return

        repo_path = self.sync_manager.repos_dir / repo_name

        if not repo_path.exists():
            QMessageBox.warning(self, "Not Found", f"Local folder not found: {repo_name}")
            return

        try:
            if os.name == 'nt':
                os.startfile(str(repo_path))
            elif os.name == 'posix':
                subprocess.run(['xdg-open', str(repo_path)], check=False)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Cannot open folder: {str(e)}")

    def on_repo_double_click(self, repo: dict):
        repo_name = repo.get('name', 'Unknown')
        local_exists = self.check_local_exists(repo_name)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Repository: {repo_name}")
        dialog.setMinimumSize(450, 350)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        name_label = QLabel(repo_name)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        layout.addWidget(name_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {ModernDarkTheme.BORDER_COLOR};")
        layout.addWidget(separator)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        size_mb = repo.get('size', 0) / 1024
        is_private = repo.get('private', False)
        is_fork = repo.get('fork', False)

        info_items = [
            ("Full Name:", repo.get('full_name', 'N/A')),
            ("Type:", 'Private' if is_private else 'Public'),
            ("Fork:", 'Yes' if is_fork else 'No'),
            ("Size:", f"{size_mb:.2f} MB"),
            ("Local Copy:", 'Yes' if local_exists else 'No'),
        ]

        for label_text, value in info_items:
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 2, 0, 2)

            label = QLabel(label_text)
            label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 12px;")
            label.setFixedWidth(100)

            value_label = QLabel(str(value))
            value_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-size: 12px; font-weight: 500;")

            item_layout.addWidget(label)
            item_layout.addWidget(value_label)
            item_layout.addStretch()
            info_layout.addWidget(item_widget)

        if repo.get('description'):
            desc_label = QLabel("Description:")
            desc_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 12px; margin-top: 8px;")
            info_layout.addWidget(desc_label)

            desc_text = QLabel(repo.get('description', "..."))
            desc_text.setWordWrap(True)
            desc_text.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-size: 11px;")
            info_layout.addWidget(desc_text)

        layout.addLayout(info_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(32)
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)

        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        dialog.exec()

    def open_setup(self):
        dialog = SetupDialog(self.config_manager, self)
        if dialog.exec():
            self.initialize()

    def open_settings(self):
        self.open_setup()

    def show_about(self):
        AboutDialog(self).exec()

    def center_on_screen(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def show_preloader(self, message: str = "Loading..."):
        self.preloader_dialog = QDialog(self)
        self.preloader_dialog.setWindowTitle("Please Wait")
        self.preloader_dialog.setFixedSize(400, 180)
        self.preloader_dialog.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.preloader_dialog.setModal(True)
        self.preloader_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {ModernDarkTheme.CARD_BG};
                border: 1px solid {ModernDarkTheme.BORDER_COLOR};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self.preloader_dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        self.loading_label = QLabel("⏳")
        self.loading_label.setStyleSheet("font-size: 40px;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet(f"""
            color: {ModernDarkTheme.TEXT_PRIMARY};
            font-size: 14px;
            font-weight: 500;
        """)
        layout.addWidget(self.message_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {ModernDarkTheme.BORDER_COLOR};
                border-radius: 4px;
                background-color: {ModernDarkTheme.DARK_BG};
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {ModernDarkTheme.PRIMARY_COLOR};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        self.animation_counter = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_loading)
        self.animation_timer.start(200)

        self.preloader_dialog.show()
        QApplication.processEvents()

    def animate_loading(self):
        frames = ["⏳", "⌛", "⏳", "⌛"]
        self.animation_counter = (self.animation_counter + 1) % len(frames)
        if hasattr(self, 'loading_label') and self.loading_label:
            self.loading_label.setText(frames[self.animation_counter])

    def update_preloader_message(self, message: str, percent: int = None):
        if hasattr(self, 'message_label') and self.message_label:
            self.message_label.setText(message)
        if percent is not None and hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setValue(percent)

    def hide_preloader(self):
        if hasattr(self, 'animation_timer') and self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
        if hasattr(self, 'preloader_dialog') and self.preloader_dialog:
            self.preloader_dialog.accept()
            self.preloader_dialog = None

    def create_desktop_entry(self):
        from ui.dialogs.desktop_entry_dialog import DesktopEntryDialog
        dialog = DesktopEntryDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        if self.load_worker and self.load_worker.isRunning():
            self.load_worker.stop()
            self.load_worker.wait()

        if self.animation_timer:
            self.animation_timer.stop()

        reply = QMessageBox.question(
            self,
            "Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
