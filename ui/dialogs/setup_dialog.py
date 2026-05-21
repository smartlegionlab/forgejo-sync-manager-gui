# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

import requests
from core.auth import ForgejoAuth
from core.api_client import ForgejoAPIClient
from ui.theme import ModernDarkTheme


class ConnectionTestWorker(QThread):
    finished_signal = pyqtSignal(bool, str, object, object)

    def __init__(self, server_url: str, token: str):
        super().__init__()
        self.server_url = server_url
        self.token = token

    def run(self):
        try:
            test_auth = ForgejoAuth(server_url=self.server_url)
            test_client = ForgejoAPIClient(test_auth)
            test_client.test_connection()

            auth = ForgejoAuth(server_url=self.server_url, token=self.token)
            client = ForgejoAPIClient(auth)
            user_info = client.get_user_info()
            auth.username = user_info.get('login', '')

            self.finished_signal.emit(True, f"Connected as: @{auth.username}", auth, user_info)

        except requests.exceptions.ConnectionError:
            self.finished_signal.emit(False, f"Cannot connect to {self.server_url}", None, None)
        except requests.exceptions.HTTPError:
            self.finished_signal.emit(False, "Invalid token", None, None)
        except Exception as e:
            self.finished_signal.emit(False, str(e), None, None)


class SetupDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.test_worker = None

        self.setWindowTitle("Forgejo Setup")
        self.setMinimumSize(550, 400)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title = QLabel("Welcome to Forgejo Sync Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        main_layout.addWidget(title)

        subtitle = QLabel("Please configure your Forgejo connection")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: transparent;")
        scroll_area.setMinimumHeight(250)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)

        server_label = QLabel("Forgejo Server URL")
        server_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-weight: bold;")
        content_layout.addWidget(server_label)

        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("http://localhost:3000")
        self.server_input.setMinimumHeight(35)
        self.server_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ModernDarkTheme.CARD_BG};
                border: 1px solid {ModernDarkTheme.BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                color: {ModernDarkTheme.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {ModernDarkTheme.PRIMARY_COLOR};
            }}
        """)
        content_layout.addWidget(self.server_input)

        token_label = QLabel("Access Token")
        token_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-weight: bold; margin-top: 10px;")
        content_layout.addWidget(token_label)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Personal Access Token")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setMinimumHeight(35)
        self.token_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ModernDarkTheme.CARD_BG};
                border: 1px solid {ModernDarkTheme.BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                color: {ModernDarkTheme.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {ModernDarkTheme.PRIMARY_COLOR};
            }}
        """)
        content_layout.addWidget(self.token_input)

        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()

        self.save_btn = QPushButton("Save and Continue")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setMinimumWidth(150)
        self.save_btn.clicked.connect(self.save_and_test)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernDarkTheme.PRIMARY_COLOR};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                background-color: #1a75ff;
            }}
            QPushButton:disabled {{
                background-color: #5a6268;
                color: #adb5bd;
            }}
        """)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(cancel_btn)

        main_layout.addLayout(button_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 12px; margin-top: 10px;")
        main_layout.addWidget(self.status_label)

    def save_and_test(self):
        server_url = self.server_input.text().strip()
        token = self.token_input.text().strip()

        if not server_url:
            self.show_status("Please enter server URL", ModernDarkTheme.ERROR_COLOR)
            return

        if not token:
            self.show_status("Please enter access token", ModernDarkTheme.ERROR_COLOR)
            return

        self.save_btn.setEnabled(False)
        self.save_btn.setText("Checking...")
        self.show_status("Testing connection...", ModernDarkTheme.INFO_COLOR)

        self.test_worker = ConnectionTestWorker(server_url, token)
        self.test_worker.finished_signal.connect(self.on_test_finished)
        self.test_worker.start()

    def on_test_finished(self, success: bool, message: str, auth, user_info):
        self.save_btn.setEnabled(True)
        self.save_btn.setText("Save and Continue")

        if success:
            config = {
                "token": auth.token,
                "server_url": auth.server_url,
                "username": auth.username
            }
            self.config_manager.save(config)

            reply = QMessageBox.question(
                self,
                "Save this configuration?",
                f"Save this configuration?\n\n"
                f"Connected as: @{auth.username}\n\n"
                f"Restart application to load your repositories?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.restart_application()
            else:
                self.reject()
        else:
            self.show_status(f"Error: {message}", ModernDarkTheme.ERROR_COLOR)

    def show_status(self, message: str, color: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"font-size: 12px; margin-top: 10px; color: {color};")

    def restart_application(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def closeEvent(self, event):
        if self.test_worker and self.test_worker.isRunning():
            self.test_worker.terminate()
            self.test_worker.wait()
        event.accept()
