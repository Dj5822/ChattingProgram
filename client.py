import sys
from PyQt5.QtWidgets import *


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        screen = app.primaryScreen()
        size = screen.size()
        self.width = size.width()
        self.height = size.height()
        self.setupConnectionWindow("Chat Application")

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
    def setupConnectionWindow(self, title):
        self.setWindowTitle(title)
        self.resize(self.width/2, self.height/2)   
        self.center_window()

        # Create components.
        ipAddressLabel = QLabel('IP Address', self)
        portLabel = QLabel('Port', self)
        nicknameLabel = QLabel('Nick Name', self)
        ipAddressTextBox = QLineEdit(self)
        portTextBox = QLineEdit(self)
        nicknameTextBox = QLineEdit(self)
        connectButton = QPushButton('Connect')
        cancelButton = QPushButton('Cancel')
        
        # Add components to grid layout
        gridLayout = QGridLayout()
        gridLayout.addWidget(ipAddressLabel, 0, 0)
        gridLayout.addWidget(portLabel, 1, 0)
        gridLayout.addWidget(nicknameLabel, 2, 0)
        gridLayout.addWidget(ipAddressTextBox, 0, 1)
        gridLayout.addWidget(portTextBox, 1, 1)
        gridLayout.addWidget(nicknameTextBox, 2, 1)

        # Add buttons to layout.
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(connectButton)
        buttonLayout.addWidget(cancelButton)
        
        # Add layouts to the parent layout.
        parentLayout = QVBoxLayout()
        parentLayout.addLayout(gridLayout)
        parentLayout.addLayout(buttonLayout)
        self.setLayout(parentLayout)

        self.show()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())
