import sys
import socket
import select
import threading
from PyQt5.QtWidgets import *
from utils import *

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
        self.menu_window = MenuWindow(self.width, self.height, self.title, self)

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
        self.connect_button.clicked.connect(self.connect_to_server)
        self.cancel_button.clicked.connect(self.close_program)
        
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

    def connect_to_server(self):
        # Connect to server at port
        try:
            """
            self.host = self.ip_address_textbox.text()
            self.port = int(self.port_textbox.text())
            self.name = self.nickname_textbox.text()
            """

            self.host = 'localhost'
            self.port = 9988
            self.name = 'Steve'

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.connected = True

            # Sends the client name
            send(self.sock, 'NAME: ' + self.name)
            data = receive(self.sock)
            
            # Contains client address, set it
            client = data.split('CLIENT: ')[1]

            self.show_menu_window()

            threading.Thread(target=self.run).start()

        except socket.error as e:
            self.show_error_dialog(f'Failed to connect to chat server @ port {self.port}')
        except NameError:
            self.show_error_dialog("There was a name error.")
        except Exception:
            self.show_error_dialog("There was a connection error.")

    def run(self):
        self.menu_window.update_connected_clients(["test user 1", "test user 2"])
        self.menu_window.update_chat_rooms_list(["test chat room 1", "test chat room 2"])
        
        
    """
    Used to show a dialog
    """
    def show_error_dialog(self, message):
        error_dialog = QErrorMessage(self)
        error_dialog.showMessage(message)

    """
    Used to show the menu window after connecting successfully.
    """
    def show_menu_window(self):
        self.menu_window.show()
        self.hide()

    """
    Used to end the program.
    """
    def close_program(self):
        quit()

"""
The window that is shown after successfully connecting.
"""
class MenuWindow(QWidget):
    def __init__(self, width, height, title, prev_window):
        super().__init__()
        self.width = int(width/2)
        self.height = height
        self.title = title
        self.prev_window = prev_window
        self.setup_menu_window()
        self.chat_room_window = ChatRoomWindow(self.width, self.height, self.title, self)
        self.group_chat_room_window = GroupChatRoomWindow(self.width, self.height, self.title, self)

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
    def setup_menu_window(self):
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)   
        self.center_window()

        # Create components
        self.connected_clients_label = QLabel('Connected Clients', self)
        self.chat_rooms_label = QLabel('Chat rooms (Group chat)', self)
        self.connected_clients_list_widget = QListWidget()
        self.chat_rooms_list_widget = QListWidget()
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
        self.connected_clients_layout.addWidget(self.connected_clients_list_widget)
        self.connected_clients_layout.addWidget(self.one_to_one_chat_button)
        self.chat_rooms_layout.addWidget(self.chat_rooms_list_widget)
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
        self.chat_room_window.load_data("Test title", ["Message 1", "Message 2"])
        self.chat_room_window.show()
        self.hide()

    """
    Goes to group chat window.
    """
    def show_group_chat_window(self):
        self.group_chat_room_window.load_data("Test title", ["Message 1", "Message 2"], ["Member 1", "Member 2"])
        self.group_chat_room_window.show()
        self.hide()

    """
    Goes to the previous window.
    """
    def show_connection_window(self):
        self.prev_window.show()
        self.hide()

    """
    Updates the connected clients list widget.
    """
    def update_connected_clients(self, clients_list):
        self.connected_clients_list_widget.clear()
        for i in range(len(clients_list)):
            self.connected_clients_list_widget.insertItem(i, clients_list[i])

    """
    Updates the chat rooms list widget.
    """
    def update_chat_rooms_list(self, chat_rooms_list):
        self.chat_rooms_list_widget.clear()
        for i in range(len(chat_rooms_list)):
            self.chat_rooms_list_widget.insertItem(i, chat_rooms_list[i])


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
        self.close_button.clicked.connect(self.show_menu_window)

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
    def show_menu_window(self):
        self.prev_window.show()
        self.hide()  

    """
    Loads the data for the chat room.
    """
    def load_data(self, title, message_list):
        self.title_label.setText(title)
        self.chat_text_browser.clear()
        for message in message_list:
            self.chat_text_browser.append(message)


"""
The window that is shown after creating or joining a group chat.
"""
class GroupChatRoomWindow(ChatRoomWindow):
    def __init__(self, width, height, title, prev_window):
        super().__init__(width, height, title, prev_window)
        self.invite_window = InviteWindow(self.width, self.height, self.title, self)

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
        self.members_list_widget = QListWidget()
        self.invite_button = QPushButton('Invite')

        # Button functionality
        self.invite_button.clicked.connect(self.show_invite_window)

        # Setup new layouts
        self.members_layout = QVBoxLayout()
        self.group_chat_layout = QHBoxLayout()

        # Add components to layout
        self.members_layout.addWidget(self.members_label)
        self.members_layout.addWidget(self.members_list_widget)
        self.members_layout.addWidget(self.invite_button)
        self.group_chat_layout.addLayout(self.chat_layout)
        self.group_chat_layout.addLayout(self.members_layout)

    """
    Used to show the invite window.
    """
    def show_invite_window(self):
        self.invite_window.show()
        self.hide()

    """
    Loads the data for the chat room.
    """
    def load_data(self, title, message_list, members_list):
        self.title_label.setText(title)
        self.chat_text_browser.clear()
        self.members_list_widget.clear()
        
        for message in message_list:
            self.chat_text_browser.append(message)

        for i in range(len(members_list)):
            self.members_list_widget.insertItem(i, members_list[i])

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
