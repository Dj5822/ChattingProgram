import sys
from PyQt5.QtWidgets import *


class ChatApp(QWidget):

    def __init__(self):
        super().__init__()
        screen = app.primaryScreen()
        size = screen.size()
        self.width = int(size.width()/2)
        self.height = int(size.height()/2)
        self.title = "Chat Application"
        self.setup_connection_window()

    """
    Used to move the window to the center of the screen.
    """
    def center_window(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    """
    Used to setup the GUI.
    """
    def setup_connection_window(self):
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)   
        self.center_window()

        # Create components.
        self.ip_address_label = QLabel('IP Address', self)
        self.port_label = QLabel('Port', self)
        self.nickname_label = QLabel('Nick Name', self)
        self.ip_address_textbox = QLineEdit(self)
        self.port_textbox = QLineEdit(self)
        self.nickname_textbox = QLineEdit(self)
        self.connect_button = QPushButton('Connect')
        self.cancel_button = QPushButton('Cancel')

        # Add button functionality.
        self.connect_button.clicked.connect(self.show_connected_window)
        
        # Add components to grid layout
        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.ip_address_label, 0, 0)
        self.grid_layout.addWidget(self.port_label, 1, 0)
        self.grid_layout.addWidget(self.nickname_label, 2, 0)
        self.grid_layout.addWidget(self.ip_address_textbox, 0, 1)
        self.grid_layout.addWidget(self.port_textbox, 1, 1)
        self.grid_layout.addWidget(self.nickname_textbox, 2, 1)

        # Add buttons to layout.
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.connect_button)
        self.button_layout.addWidget(self.cancel_button)
        
        # Add layouts to the parent layout.
        self.parent_layout = QVBoxLayout()
        self.parent_layout.addLayout(self.grid_layout)
        self.parent_layout.addLayout(self.button_layout)
        self.setLayout(self.parent_layout)

        self.show()

    def show_connected_window(self):
        self.connected_window = ConnectedWindow(self.width, self.height, self.title)
        self.connected_window.show()
        self.hide()

class ConnectedWindow(QWidget):
    def __init__(self, width, height, title):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.setup_connected_window()

    def center_window(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def setup_connected_window(self):
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)   
        self.center_window()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApp()
    sys.exit(app.exec_())
