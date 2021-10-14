import sys
from PyQt5.QtWidgets import *

"""
The first window that is shown at the start of the application.
"""
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

    """
    Used to show the connected window after connecting successfully.
    """
    def show_connected_window(self):
        self.connected_window = ConnectedWindow(self.width, self.height, self.title, self)
        self.connected_window.show()
        self.hide()

"""
The window that is shown after successfully connecting.
"""
class ConnectedWindow(QWidget):
    def __init__(self, width, height, title, prev_window):
        super().__init__()
        self.width = int(width/2)
        self.height = height
        self.title = title
        self.prev_window = prev_window
        self.setup_connected_window()

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
    def setup_connected_window(self):
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)   
        self.center_window()

        # Create components
        self.connected_clients_label = QLabel('Connected Clients', self)
        self.chat_rooms_label = QLabel('Chat rooms (Group chat)', self)
        self.connected_clients_text_browser = QTextBrowser()
        self.chat_rooms_text_browser = QTextBrowser()
        self.one_to_one_chat_button = QPushButton('1:1 chat')
        self.create_button = QPushButton('Create')
        self.join_button = QPushButton('Join')
        self.close_button = QPushButton('Close')

        # Add button functionality.
        self.one_to_one_chat_button.clicked.connect(self.show_chat_window)
        self.create_button.clicked.connect(self.show_group_chat_window)
        self.join_button.clicked.connect(self.show_group_chat_window)
        self.close_button.clicked.connect(self.show_connection_window)

        # Create layouts
        self.connected_clients_layout = QHBoxLayout()
        self.chat_rooms_layout = QHBoxLayout()
        self.chat_rooms_button_layout = QVBoxLayout()
        self.parent_layout = QVBoxLayout()

        # Add components to layouts
        self.connected_clients_layout.addWidget(self.connected_clients_text_browser)
        self.connected_clients_layout.addWidget(self.one_to_one_chat_button)
        self.chat_rooms_layout.addWidget(self.chat_rooms_text_browser)
        self.chat_rooms_button_layout.addWidget(self.create_button)
        self.chat_rooms_button_layout.addWidget(self.join_button)
        self.chat_rooms_layout.addLayout(self.chat_rooms_button_layout)
        self.parent_layout.addWidget(self.connected_clients_label)
        self.parent_layout.addLayout(self.connected_clients_layout)
        self.parent_layout.addWidget(self.chat_rooms_label)
        self.parent_layout.addLayout(self.chat_rooms_layout)
        self.parent_layout.addWidget(self.close_button)
        self.setLayout(self.parent_layout)

    """
    Goes to the one to one chat window.
    """
    def show_chat_window(self):
        self.chat_room_window = ChatRoomWindow(self.width, self.height, self.title, self)
        self.chat_room_window.show()
        self.hide()

    """
    Goes to group chat window.
    """
    def show_group_chat_window(self):
        self.chat_room_window = GroupChatRoomWindow(self.width, self.height, self.title, self)
        self.chat_room_window.show()
        self.hide()

    """
    Goes to the previous window.
    """
    def show_connection_window(self):
        self.prev_window.show()
        self.hide()

"""
The window that is shown after pressing 1:1 chat button.
"""
class ChatRoomWindow(QWidget):
    def __init__(self, width, height, title, prev_window):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.prev_window = prev_window
        self.setup_chat_room_window()

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
    def setup_chat_room_window(self):
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)   
        self.center_window()
        self.setup_chat_room_layout()
        self.setLayout(self.chat_layout)

    """
    Used to setup the main layout.
    """
    def setup_chat_room_layout(self):
        # Create components.
        self.title_label = QLabel('Chat Title')
        self.chat_text_browser = QTextBrowser()
        self.chat_input = QLineEdit()
        self.send_button = QPushButton('Send')
        self.close_button = QPushButton('Close')

        # Button functionality
        self.close_button.clicked.connect(self.show_connected_window)

        # Create layouts
        self.chat_input_layout = QHBoxLayout()
        self.chat_layout = QVBoxLayout()

        # Add components to layouts
        self.chat_layout.addWidget(self.title_label)
        self.chat_layout.addWidget(self.chat_text_browser)
        self.chat_input_layout.addWidget(self.chat_input)
        self.chat_input_layout.addWidget(self.send_button)
        self.chat_layout.addLayout(self.chat_input_layout)
        self.chat_layout.addWidget(self.close_button)

    """
    Goes to the previous window.
    """
    def show_connected_window(self):
        self.prev_window.show()
        self.hide()  

"""
The window that is shown after creating or joining a group chat.
"""
class GroupChatRoomWindow(ChatRoomWindow):
    def __init__(self, width, height, title, prev_window):
        super().__init__(width, height, title, prev_window)

    """
    Used to move the window to the center of the screen.
    """
    def setup_chat_room_window(self):
        self.width = int(self.width * 1.5)
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)   
        self.center_window()
        self.setup_group_chat_room_layout()
        self.setLayout(self.group_chat_layout)

    """
    Used to setup the main layout.
    """
    def setup_group_chat_room_layout(self):
        self.setup_chat_room_layout()

        # Create components
        self.members_label = QLabel('Members', self)
        self.members_text_browser = QTextBrowser()
        self.invite_button = QPushButton('Invite')

        # Button functionality
        self.invite_button.clicked.connect(self.show_invite_window)

        # Setup new layouts
        self.members_layout = QVBoxLayout()
        self.group_chat_layout = QHBoxLayout()

        # Add components to layout
        self.members_layout.addWidget(self.members_label)
        self.members_layout.addWidget(self.members_text_browser)
        self.members_layout.addWidget(self.invite_button)
        self.group_chat_layout.addLayout(self.chat_layout)
        self.group_chat_layout.addLayout(self.members_layout)

    """
    Used to show the invite window.
    """
    def show_invite_window(self):
        self.invite_window = InviteWindow(self.width, self.height, self.title, self)
        self.invite_window.show()
        self.hide()

"""
The window that is shown after pressing the invite button.
"""
class InviteWindow(QWidget):
    def __init__(self, width, height, title, prev_window):
        super().__init__()
        self.width = int(width / 3)
        self.height = height
        self.title = title
        self.prev_window = prev_window
        self.setup_invite_window()

    """
    Used to move the window to the center of the screen.
    """
    def center_window(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    """
    Used to setup the GUI
    """
    def setup_invite_window(self):
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)   
        self.center_window()

        # Create components
        self.connected_clients_label = QLabel("Connected Clients", self)
        self.clients_text_browser = QTextBrowser()
        self.invite_button = QPushButton("Invite")
        self.cancel_button = QPushButton("Cancel")

        # Button functionality
        self.cancel_button.clicked.connect(self.show_group_chat_window)

        # Create layouts
        self.parent_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        # Add components to layout
        self.parent_layout.addWidget(self.connected_clients_label)
        self.parent_layout.addWidget(self.clients_text_browser)
        self.button_layout.addWidget(self.invite_button)
        self.button_layout.addWidget(self.cancel_button)
        self.parent_layout.addLayout(self.button_layout)
        self.setLayout(self.parent_layout)

    """
    Go to previous window.
    """
    def show_group_chat_window(self):
        self.prev_window.show()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApp()
    sys.exit(app.exec_())
