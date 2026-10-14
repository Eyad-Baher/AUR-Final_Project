import sys

from PySide6.QtWidgets import QApplication

from .main import RobotConsole


def main():
    app = QApplication(sys.argv)
    window = RobotConsole()
    window.show()
    window.setFocus()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

