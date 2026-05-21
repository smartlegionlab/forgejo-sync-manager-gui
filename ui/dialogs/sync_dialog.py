# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
from datetime import datetime
from typing import List, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QWidget, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from core.sync_manager_gui import GUISyncManager
from ui.theme import ModernDarkTheme


class SyncWorker(QThread):
    progress = pyqtSignal(int, int, str, str)
    finished_signal = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, sync_manager: GUISyncManager, repositories: List[dict], operation: str = "sync"):
        super().__init__()
        self.sync_manager = sync_manager
        self.repositories = repositories
        self.operation = operation
        self._is_running = True

    def run(self):
        results = {"cloned": 0, "updated": 0, "recloned": 0, "failed": 0}
        total = len(self.repositories)

        for i, repo in enumerate(self.repositories, 1):
            if not self._is_running:
                break

            repo_name = repo.get('name', 'Unknown')

            try:
                if self.operation == "sync":
                    status = self.sync_manager.sync_repository(repo)
                elif self.operation == "reclone":
                    status = self.sync_manager.reclone_repository(repo)
                else:
                    status = "FAILED"

                if status == "CLONED":
                    results["cloned"] += 1
                elif status == "UPDATED":
                    results["updated"] += 1
                elif status == "RECLONED":
                    results["recloned"] += 1
                else:
                    results["failed"] += 1

                self.progress.emit(i, total, repo_name, status)

            except Exception as e:
                results["failed"] += 1
                self.progress.emit(i, total, repo_name, f"ERROR: {str(e)}")

        self.finished_signal.emit(results)

    def stop(self):
        self._is_running = False


class SyncDialog(QDialog):
    repo_status_updated = pyqtSignal(str, bool)

    def __init__(self, sync_manager: GUISyncManager, repositories: List[dict], operation: str = "sync", parent=None):
        super().__init__(parent)
        self.sync_manager = sync_manager
        self.repositories = repositories
        self.operation = operation
        self.worker = None

        self.setWindowTitle("Synchronization")
        self.setMinimumSize(700, 500)
        self.setModal(True)

        self.setup_ui()

        QTimer.singleShot(100, self.start_sync)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel(f"{self.operation.upper()}ING REPOSITORIES")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {ModernDarkTheme.PRIMARY_COLOR};")
        layout.addWidget(title)

        info_label = QLabel(f"Repositories to process: {len(self.repositories)}")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY};")
        layout.addWidget(info_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(self.repositories))
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.current_label = QLabel("Preparing...")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(self.current_label)

        log_label = QLabel("Log")
        log_label.setStyleSheet(f"color: {ModernDarkTheme.TEXT_PRIMARY}; font-weight: bold;")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernDarkTheme.CARD_BG};
                border: 1px solid {ModernDarkTheme.BORDER_COLOR};
                border-radius: 4px;
                color: {ModernDarkTheme.TEXT_SECONDARY};
                font-family: monospace;
                font-size: 11px;
            }}
        """)
        layout.addWidget(self.log_text)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_sync)

        self.close_btn = QPushButton("Close")
        self.close_btn.setEnabled(False)
        self.close_btn.clicked.connect(self.accept)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(button_layout)

    def start_sync(self):
        self.sync_manager.ensure_directories()

        self.worker = SyncWorker(self.sync_manager, self.repositories, self.operation)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, current: int, total: int, repo_name: str, status: str):
        self.progress_bar.setValue(current)
        self.current_label.setText(f"Processing: {repo_name}")

        status_icon = {
            "CLONED": "✅",
            "UPDATED": "🔄",
            "RECLONED": "⚠️",
            "FAILED": "❌"
        }.get(status, "❓")

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {status_icon} {repo_name}: {status}")

        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        QApplication.processEvents()

        if status in ["CLONED", "UPDATED", "RECLONED"]:
            self.repo_status_updated.emit(repo_name, True)

    def on_finished(self, results: dict):
        self.current_label.setText("Synchronization completed!")
        self.cancel_btn.setEnabled(False)
        self.close_btn.setEnabled(True)

        self.log_text.append("\n" + "=" * 50)
        self.log_text.append("SUMMARY:")
        self.log_text.append(f"  ✅ Cloned: {results['cloned']}")
        self.log_text.append(f"  🔄 Updated: {results['updated']}")
        self.log_text.append(f"  ⚠️ Recloned: {results['recloned']}")
        self.log_text.append(f"  ❌ Failed: {results['failed']}")
        self.log_text.append("=" * 50)

    def on_error(self, error_msg: str):
        self.log_text.append(f"\n❌ ERROR: {error_msg}")

    def cancel_sync(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        self.current_label.setText("Cancelled by user")
        self.cancel_btn.setEnabled(False)
        self.close_btn.setEnabled(True)