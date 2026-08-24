# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from forgejo_sync_manager_core.core.config import ConfigManager
from ui.theme import ModernDarkTheme


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(450, 400)
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3a3a;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)

        content_widget = QWidget()
        content_widget.setStyleSheet(f"background-color: {ModernDarkTheme.CARD_BG};")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        title = QLabel(ConfigManager.APP_FULL_NAME)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        layout.addWidget(title)

        version = QLabel("Version v1.0.3")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(version)

        layout.addSpacing(10)

        desc = QLabel(
            "Desktop GUI application for batch synchronization\n"
            "of Forgejo repositories to local machine."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-size: 12px;")
        layout.addWidget(desc)

        layout.addSpacing(15)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {ModernDarkTheme.BORDER_COLOR};")
        layout.addWidget(separator)

        layout.addSpacing(10)

        links_layout = QVBoxLayout()
        links_layout.setSpacing(6)

        links = [
            ("Website", "https://smartlegionlab.com"),
            ("GitHub Repository", "https://github.com/smartlegionlab/forgejo-sync-manager-gui"),
            ("Core Library", "https://github.com/smartlegionlab/forgejo-sync-manager-core"),
            ("Disclaimer", "https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/DISCLAIMER.md"),
            ("License (BSD 3-Clause)", "https://github.com/smartlegionlab/forgejo-sync-manager-gui/blob/master/LICENSE"),
        ]

        for text, url in links:
            link_label = QLabel(f'<a href="{url}" style="color: {ModernDarkTheme.PRIMARY_COLOR}; text-decoration: none;">{text}</a>')
            link_label.setOpenExternalLinks(True)
            link_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            link_label.setStyleSheet("font-size: 12px;")
            links_layout.addWidget(link_label)

        layout.addLayout(links_layout)

        layout.addSpacing(10)

        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet(f"background-color: {ModernDarkTheme.BORDER_COLOR};")
        layout.addWidget(separator2)

        layout.addSpacing(10)

        copyright_label = QLabel("Copyright (c) 2026, Alexander Suvorov")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 10px;")
        layout.addWidget(copyright_label)

        layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 15)

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(32)
        close_btn.setMinimumWidth(80)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ModernDarkTheme.PRIMARY_COLOR};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #1a75ff;
            }}
        """)

        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)
