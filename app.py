# Copyright (©) 2026, Alexander Suvorov. All rights reserved.
import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow
from ui.theme import ModernDarkTheme


def main():
    app = QApplication(sys.argv)
    ModernDarkTheme.apply(app)

    icon_path = Path(__file__).parent / "data" / "icons" / "icon.jpeg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
