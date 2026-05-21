# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
import os
import sys

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ui.theme import ModernDarkTheme


class DesktopEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Create Desktop Entry")
        self.setMinimumWidth(500)
        self.setModal(True)

        self.app_name = "Forgejo Sync Manager"
        self.app_executable = sys.executable
        self.app_path = os.path.abspath(sys.argv[0])
        self.icon_path = self.find_icon_path()

        self.setup_ui()
        self.center_dialog()

    def find_icon_path(self):
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        icon_path = project_root / "data" / "icons" / "icon.jpeg"
        return str(icon_path) if icon_path.exists() else ""

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Create Desktop Entry")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        layout.addWidget(title_label)

        info_group = QGroupBox("Application Information")
        info_layout = QVBoxLayout(info_group)

        info_text = QLabel(
            f"<b>Name:</b> {self.app_name}<br>"
            f"<b>Application Path:</b> {self.app_path}<br>"
            f"<b>Icon:</b> {self.icon_path if self.icon_path else 'Not found'}"
        )
        info_text.setTextFormat(Qt.TextFormat.RichText)
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)

        layout.addWidget(info_group)

        options_group = QGroupBox("Create shortcuts in:")
        options_layout = QVBoxLayout(options_group)

        self.app_menu_checkbox = QCheckBox("Application Menu (~/.local/share/applications/)")
        self.app_menu_checkbox.setChecked(True)
        options_layout.addWidget(self.app_menu_checkbox)

        self.desktop_checkbox = QCheckBox("Desktop (~/Desktop/)")
        self.desktop_checkbox.setChecked(False)
        options_layout.addWidget(self.desktop_checkbox)

        layout.addWidget(options_group)

        note_label = QLabel(
            "Note: After creation, you may need to log out and back in "
            "or restart your desktop for the entry to appear in the menu."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 11px; padding: 8px;")
        layout.addWidget(note_label)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.create_btn = QPushButton("Create Entry")
        self.create_btn.setMinimumHeight(35)
        self.create_btn.clicked.connect(self.create_desktop_entry)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def center_dialog(self):
        if self.parent:
            x = self.parent.x() + (self.parent.width() - self.width()) // 2
            y = self.parent.y() + (self.parent.height() - self.height()) // 2
            self.move(x, y)

    def create_desktop_entry(self):
        created_files = []
        errors = []

        if self.app_menu_checkbox.isChecked():
            success, message = self.create_app_menu_entry()
            if success:
                created_files.append(message)
            else:
                errors.append(message)

        if self.desktop_checkbox.isChecked():
            success, message = self.create_desktop_shortcut()
            if success:
                created_files.append(message)
            else:
                errors.append(message)

        if created_files and not errors:
            QMessageBox.information(
                self,
                "Success",
                f"Desktop entry created successfully!\n\nCreated:\n" + "\n".join(f"• {f}" for f in created_files)
            )
            self.accept()
        elif created_files and errors:
            QMessageBox.warning(
                self,
                "Partial Success",
                f"Some entries were created with issues:\n\n"
                f"Created:\n" + "\n".join(f"• {f}" for f in created_files) +
                f"\n\nErrors:\n" + "\n".join(f"• {e}" for e in errors)
            )
            self.accept()
        elif errors:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create desktop entries:\n\n" + "\n".join(f"• {e}" for e in errors)
            )

    def create_app_menu_entry(self):
        try:
            desktop_dir = os.path.expanduser("~/.local/share/applications")
            os.makedirs(desktop_dir, exist_ok=True)

            desktop_file = os.path.join(desktop_dir, "forgejo-sync-manager.desktop")

            content = self.generate_desktop_content()

            with open(desktop_file, 'w', encoding='utf-8') as f:
                f.write(content)

            os.chmod(desktop_file, 0o755)

            return True, desktop_file
        except Exception as e:
            return False, str(e)

    def create_desktop_shortcut(self):
        try:
            desktop_dir = os.path.expanduser("~/Desktop")
            os.makedirs(desktop_dir, exist_ok=True)

            desktop_file = os.path.join(desktop_dir, "forgejo-sync-manager.desktop")

            content = self.generate_desktop_content()

            with open(desktop_file, 'w', encoding='utf-8') as f:
                f.write(content)

            os.chmod(desktop_file, 0o755)

            return True, desktop_file
        except Exception as e:
            return False, str(e)

    def generate_desktop_content(self):
        from core.config import ConfigManager
        python_exec = sys.executable

        exec_line = f'"{python_exec}" "{self.app_path}"'

        content = f"""[Desktop Entry]
Version={ConfigManager.VERSION}
Type=Application
Name={self.app_name}
Comment=A powerful desktop application for managing Forgejo repositories with intelligent synchronization
Exec={exec_line}
Icon={self.icon_path if self.icon_path else 'system-run'}
Terminal=false
Categories=Utility;Development;
StartupNotify=true
Keywords=forgejo;git;repository;sync;manager;
"""
        return content
