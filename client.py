import sys
import socket
import select
import time
import typing
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from utils import *


def close_program():
    """
    Used to end the program.
    """
    quit()


class ChatApp(QWidget):
    """
    The first window that is shown at the start of the application.
    """

    def __init__(self):
        super().__init__()
        screen = app.primaryScreen()
        size = screen.size()
        self.width = int(size.width() / 2)
        self.height = int(size.height() / 2)
        self.title = "Chat Application"

        # Create components.
        self.ip_address_label = QLabel('IP Address', self)
        self.port_label = QLabel('Port', self)
        self.nickname_label = QLabel('Nick Name', self)
        self.ip_address_textbox = QLineEdit(self)
        self.port_textbox = QLineEdit(self)
        self.nickname_textbox = QLineEdit(self)
        self.connect_button = QPushButton('Connect')
        self.cancel_button = QPushButton('Cancel')
        self.grid_layout = QGridLayout()
        self.button_layout = QHBoxLayout()
        self.parent_layout = QVBoxLayout()
        self.setup_connection_window()

        self.host = ''
        self.port = None
        self.name = ''
        self.sock = None
        self.menu_window = None

    def setup_connection_window(self):
        """
        Used to setup the GUI.
        """
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        # Add button functionality.
        self.connect_button.clicked.connect(self.connect_to_server)
        self.cancel_button.clicked.connect(close_program)

        # Add components to grid layout
        self.grid_layout.addWidget(self.ip_address_label, 0, 0)
        self.grid_layout.addWidget(self.port_label, 1, 0)
        self.grid_layout.addWidget(self.nickname_label, 2, 0)
        self.grid_layout.addWidget(self.ip_address_textbox, 0, 1)
        self.grid_layout.addWidget(self.port_textbox, 1, 1)
        self.grid_layout.addWidget(self.nickname_textbox, 2, 1)

        # Add buttons to layout.
        self.button_layout.addWidget(self.connect_button)
        self.button_layout.addWidget(self.cancel_button)

        # Add layouts to the parent layout.
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
            self.name = self.nickname_textbox.text()

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.menu_window = MenuWindow(self.width, self.height, self.title, self)
            self.show_menu_window()

        except socket.error as e:
            self.show_error_dialog(f'Failed to connect to chat server @ port {self.port}')
        except NameError:
            self.show_error_dialog("There was a name error.")
        except Exception as e:
            print(e)
            self.show_error_dialog("There was a connection error.")

    def show_error_dialog(self, message):
        """
        Used to show a dialog
        """
        error_dialog = QErrorMessage(self)
        error_dialog.showMessage(message)

    def show_menu_window(self):
        """
        Used to show the menu window after connecting successfully.
        """
        self.menu_window.show()
        self.hide()


class ConnectedClientsWorker(QObject):
    """
    The worker used to handle server output.
    """
    finished = pyqtSignal()
    show_error_message = pyqtSignal()

    def __init__(self, sock, invite_window, chat_window, group_chat_window, menu_window, parent=None):
        super().__init__(parent=parent)
        self.sock = sock
        self.invite_window = invite_window
        self.chat_window = chat_window
        self.group_chat_window = group_chat_window
        self.menu_window = menu_window
        self.connected = True

    def run(self):
        """Long-running task."""
        while self.connected:
            readable, writeable, exceptional = select.select([self.sock], [], [])
            for sock in readable:
                if sock == self.sock:
                    data = receive(self.sock)
                    # If the server shuts down
                    if not data:
                        print('Client shutting down.')
                        self.connected = False
                        break
                    elif data == "CLIENT_LIST":
                        clients_list = receive_clients(self.sock)
                        self.menu_window.update_connected_clients(clients_list)
                    elif data == "MESSAGE":
                        message = receive(self.sock)
                        self.chat_window.add_message(message)
                    elif data == "CREATE_ROOM":
                        self.group_chat_window.room_title = receive(self.sock)
                        self.group_chat_window.load_group_chat([self.menu_window.client_name + " (Host)"])
                    elif data == "UPDATE_ROOMS_LIST":
                        room_list = receive_list(self.sock)
                        self.menu_window.update_chat_rooms_list(room_list)
                    elif data == "JOIN_ROOM":
                        # get all the members of the chat room.
                        members_list = list(receive_list(self.sock))

                        invited = False
                        for member_name in members_list:
                            if member_name == self.menu_window.client_name:
                                invited = True

                        if invited:
                            self.group_chat_window.load_group_chat(members_list)
                            self.menu_window.show_group_chat_window()
                        else:
                            self.show_error_message.emit()
                    elif data == "UPDATE_INVITE_WINDOW":
                        invitable_clients_list = receive_list(self.sock)
                        self.invite_window.update_clients_list(invitable_clients_list)
                    elif data == "INVITED":
                        room_name = receive(self.sock)
                        chat_room_members = receive_list(self.sock)
                        if self.group_chat_window.room_title == room_name:
                            self.group_chat_window.update_members(chat_room_members)
                    elif data == "END":
                        print("terminating connection.")
                        break
        self.sock.close()
        self.finished.emit()

    def stop(self):
        self.connected = False
        send(self.sock, "END")


class MenuWindow(QWidget):
    """
    The window that is shown after successfully connecting.
    """

    def __init__(self, width, height, title, prev_window):
        super().__init__()
        self.width = int(width / 2)
        self.height = height
        self.title = title
        self.prev_window = prev_window
        self.sock = prev_window.sock
        self.client_name = prev_window.name

        self.room_title = ""
        self.members_list = []

        # Create components
        self.connected_clients_label = QLabel('Connected Clients', self)
        self.chat_rooms_label = QLabel('Chat rooms (Group chat)', self)
        self.connected_clients_list_widget = QListWidget()
        self.chat_rooms_list_widget = QListWidget()
        self.one_to_one_chat_button = QPushButton('1:1 chat')
        self.create_button = QPushButton('Create')
        self.join_button = QPushButton('Join')
        self.close_button = QPushButton('Close')

        # Create layouts
        self.connected_clients_layout = QHBoxLayout()
        self.chat_rooms_layout = QHBoxLayout()
        self.chat_rooms_button_layout = QVBoxLayout()
        self.parent_layout = QVBoxLayout()

        self.setup_menu_window()

        # Get initial clients list.
        send(self.sock, 'NAME: ' + self.prev_window.name)
        receive(self.sock)
        clients_list = receive_clients(self.sock)

        self.update_connected_clients(clients_list)

        self.chat_room_window = ChatRoomWindow(self.width, self.height, self.title, self)
        self.group_chat_room_window = GroupChatRoomWindow(self.width, self.height, self.title, self)

        self.update_thread = QThread()
        self.update_worker = ConnectedClientsWorker(self.sock, self.group_chat_room_window.invite_window,
                                                    self.chat_room_window, self.group_chat_room_window, self)
        self.update_worker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_worker.stop)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.update_worker.show_error_message.connect(lambda: self.show_error_dialog("You need to be invited "
                                                                                     "to join the room."))
        self.update_thread.start()

    def setup_menu_window(self):
        """
        Used to setup the GUI.
        """
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        # Add button functionality.
        self.one_to_one_chat_button.clicked.connect(self.show_chat_window)
        self.create_button.clicked.connect(self.create_button_clicked)
        self.join_button.clicked.connect(self.join_button_clicked)
        self.close_button.clicked.connect(self.show_connection_window)

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

    def show_chat_window(self):
        """
        Goes to the one to one chat window.
        """
        selected_users = self.connected_clients_list_widget.selectedItems()
        if len(selected_users) != 1:
            self.show_error_dialog("Please selected a user from the list.")
        elif selected_users[0].text().split("(")[1] == "me) ":
            self.show_error_dialog("Please select a user other than yourself from the list.")
        else:
            target_user = selected_users[0].text().split(" (")[0]
            self.chat_room_window.load_data(target_user)
            self.chat_room_window.show()
            self.hide()

    def create_button_clicked(self):
        send(self.sock, "CREATE_ROOM")
        self.show_group_chat_window()

    def join_button_clicked(self):
        selected_chatroom = self.chat_rooms_list_widget.selectedItems()
        if len(selected_chatroom) != 1:
            self.show_error_dialog("Please selected a chat room from the list.")
        else:
            # If the user is invited, then they can join the room.
            send(self.sock, "JOIN_ROOM")
            # Sends the room name.
            send(self.sock, str(selected_chatroom[0].text()))
            self.group_chat_room_window.room_title = str(selected_chatroom[0].text())

    def show_error_dialog(self, message):
        """
        Used to show a dialog
        """
        error_dialog = QErrorMessage(self)
        error_dialog.showMessage(message)

    def show_group_chat_window(self):
        """
        Goes to group chat window.
        """
        self.group_chat_room_window.show()
        self.hide()

    def show_connection_window(self):
        """
        Goes to the previous window.
        """
        self.update_worker.stop()
        self.prev_window.show()
        self.hide()

    def update_connected_clients(self, clients_list):
        """
        Updates the connected clients list widget.
        """
        self.connected_clients_list_widget.clear()
        for i in range(len(clients_list)):
            self.connected_clients_list_widget.insertItem(i, clients_list[i])

    def update_chat_rooms_list(self, chat_rooms_list):
        """
        Updates the chat rooms list widget.
        """
        self.chat_rooms_list_widget.clear()
        for i in range(len(chat_rooms_list)):
            self.chat_rooms_list_widget.insertItem(i, chat_rooms_list[i])


class ChatRoomWindow(QWidget):
    """
    The window that is shown after pressing 1:1 chat button.
    """

    def __init__(self, width, height, title, prev_window):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.sock = prev_window.sock
        self.target_username = None
        self.prev_window = prev_window

        # Create components.
        self.title_label = QLabel('Chat Title')
        self.chat_text_browser = QTextBrowser()
        self.chat_input = QLineEdit()
        self.send_button = QPushButton('Send')
        self.close_button = QPushButton('Close')

        # Create layouts
        self.chat_input_layout = QHBoxLayout()
        self.chat_layout = QVBoxLayout()

        self.setup_chat_room_window()

    def setup_chat_room_window(self):
        """
        Used to setup the GUI.
        """
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)
        self.setup_chat_room_layout()
        self.setLayout(self.chat_layout)

    def setup_chat_room_layout(self):
        # Button functionality
        self.send_button.clicked.connect(self.send_message)
        self.close_button.clicked.connect(self.show_menu_window)

        # Add components to layouts
        self.chat_layout.addWidget(self.title_label)
        self.chat_layout.addWidget(self.chat_text_browser)
        self.chat_input_layout.addWidget(self.chat_input)
        self.chat_input_layout.addWidget(self.send_button)
        self.chat_layout.addLayout(self.chat_input_layout)
        self.chat_layout.addWidget(self.close_button)

    def show_menu_window(self):
        """
        Goes to the previous window.
        """
        self.prev_window.show()
        self.hide()

    def send_message(self):
        """
        Sends the one to one message to the server
        and clears the input field.
        """
        send(self.sock, "MESSAGE")
        send(self.sock, self.target_username)
        send(self.sock, self.chat_input.text())
        self.chat_input.clear()

    def load_data(self, username):
        """
        Loads the data for the chat room.
        """
        self.title_label.setText("Chat with " + username)
        self.target_username = username
        self.chat_text_browser.clear()
        """
        Currently does nothing but can call saved data
        from the server later.
        """
        message_list = []
        for message in message_list:
            self.chat_text_browser.append(message)

    def add_message(self, message):
        """
        Adds a new message the text browser.
        """
        message_origin = message.split(" (")[0]
        if message_origin == "Me":
            self.chat_text_browser.append(message)
        try:
            if message_origin == self.target_username:
                self.chat_text_browser.append(message)
        except AttributeError as e:
            print("hasn't joined the chat room yet.")


class GroupChatRoomWindow(ChatRoomWindow):
    """
    The window that is shown after creating or joining a group chat.
    """

    def __init__(self, width, height, title, prev_window):
        super().__init__(width, height, title, prev_window)
        # Create components
        self.members_label = QLabel('Members', self)
        self.members_list_widget = QListWidget()
        self.invite_button = QPushButton('Invite')

        # Setup new layouts
        self.members_layout = QVBoxLayout()
        self.group_chat_layout = QHBoxLayout()

        self.setup_group_chat_room_layout()
        self.setLayout(self.group_chat_layout)

        self.room_title = "No Title"
        self.client_name = prev_window.client_name
        self.invite_window = InviteWindow(self.width, self.height, self.title, self)

    def setup_chat_room_window(self):
        self.width = int(self.width * 1.5)
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

    def setup_group_chat_room_layout(self):
        """
        Used to setup the main layout.
        """
        self.setup_chat_room_layout()

        # Button functionality
        self.invite_button.clicked.connect(self.show_invite_window)

        # Add components to layout
        self.members_layout.addWidget(self.members_label)
        self.members_layout.addWidget(self.members_list_widget)
        self.members_layout.addWidget(self.invite_button)
        self.group_chat_layout.addLayout(self.chat_layout)
        self.group_chat_layout.addLayout(self.members_layout)

    def show_invite_window(self):
        """
        Used to show the invite window.
        """
        send(self.sock, "UPDATE_INVITE_WINDOW")
        send(self.sock, self.room_title)
        self.invite_window.show()
        self.hide()

    def load_group_chat(self, members_list):
        """
        Loads the data for the chat room.
        """
        self.title_label.setText(self.room_title)
        self.members_list_widget.clear()
        for i in range(len(members_list)):
            self.members_list_widget.insertItem(i, members_list[i])

    def update_messages(self, message_list):
        self.chat_text_browser.clear()
        for message in message_list:
            self.chat_text_browser.append(message)

    def update_members(self, members_list):
        self.members_list_widget.clear()
        for i in range(len(members_list)):
            self.members_list_widget.insertItem(i, members_list[i])


class InviteWindow(QWidget):
    """
    The window that is shown after pressing the invite button.
    """

    def __init__(self, width, height, title, prev_window):
        super().__init__()
        self.width = int(width / 3)
        self.height = height
        self.title = title
        self.prev_window = prev_window

        self.sock = prev_window.sock

        # Create components
        self.connected_clients_label = QLabel("Connected Clients", self)
        self.clients_list_widget = QListWidget()
        self.invite_button = QPushButton("Invite")
        self.cancel_button = QPushButton("Cancel")

        # Create layouts
        self.parent_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.setup_invite_window()

    def show_error_dialog(self, message):
        """
        Used to show a dialog
        """
        error_dialog = QErrorMessage(self)
        error_dialog.showMessage(message)

    def setup_invite_window(self):
        """
        Used to setup the GUI
        """
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        # Button functionality
        self.invite_button.clicked.connect(self.invite_button_pressed)
        self.cancel_button.clicked.connect(self.show_group_chat_window)

        # Add components to layout
        self.parent_layout.addWidget(self.connected_clients_label)
        self.parent_layout.addWidget(self.clients_list_widget)
        self.button_layout.addWidget(self.invite_button)
        self.button_layout.addWidget(self.cancel_button)
        self.parent_layout.addLayout(self.button_layout)
        self.setLayout(self.parent_layout)

    def show_group_chat_window(self):
        """
        Go to previous window.
        """
        self.prev_window.show()
        self.hide()

    def invite_button_pressed(self):
        selected_client = self.clients_list_widget.selectedItems()
        if len(selected_client) != 1:
            self.show_error_dialog("Please select a client from the list.")
        else:
            send(self.sock, "INVITE")
            send(self.sock, self.prev_window.room_title)
            send(self.sock, str(selected_client[0].text()))

    def update_clients_list(self, clients_list):
        self.clients_list_widget.clear()
        for i in range(len(clients_list)):
            self.clients_list_widget.insertItem(i, clients_list[i])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ChatApp()
    sys.exit(app.exec_())
