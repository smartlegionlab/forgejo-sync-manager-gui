# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
import webbrowser
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.config import ConfigManager
from ui.theme import ModernDarkTheme


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setMinimumSize(550, 450)
        self.setModal(True)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        title = QLabel(ConfigManager.APP_FULL_NAME)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        layout.addWidget(title)

        version = QLabel(f"Version {ConfigManager.VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY};")
        layout.addWidget(version)

        layout.addSpacing(20)

        desc = QLabel(
            "Desktop GUI application for batch synchronization of Forgejo repositories.\n\n"
            "Features:\n"
            "• Modern dark theme interface\n"
            "• Automatic authentication via personal access token\n"
            "• Batch repository cloning and updating with real-time progress\n"
            "• Search and filter capabilities\n"
            "• Full repository recloning option\n"
            "• Local repository deletion\n"
            "• Persistent configuration storage"
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY};")
        layout.addWidget(desc)

        layout.addSpacing(20)

        links_layout = QVBoxLayout()
        links_layout.setSpacing(8)

        repo_link = QLabel('<a href="https://github.com/smartlegionlab/forgejo-sync-manager-gui">GitHub Repository</a>')
        repo_link.setOpenExternalLinks(True)
        repo_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        repo_link.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR}; font-size: 12px;")
        links_layout.addWidget(repo_link)

        disclaimer_link = QLabel('<a href="https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/DISCLAIMER.md">Disclaimer</a>')
        disclaimer_link.setOpenExternalLinks(True)
        disclaimer_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disclaimer_link.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR}; font-size: 12px;")
        links_layout.addWidget(disclaimer_link)

        license_link = QLabel('<a href="https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/LICENSE">License (BSD 3-Clause)</a>')
        license_link.setOpenExternalLinks(True)
        license_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        license_link.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR}; font-size: 12px;")
        links_layout.addWidget(license_link)

        layout.addLayout(links_layout)

        layout.addSpacing(20)

        copyright_label = QLabel("Copyright (©) 2026, Alexander Suvorov")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(copyright_label)

        layout.addSpacing(10)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(35)
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
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

        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
