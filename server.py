import select
import socket
import sys
import signal

from utils import *
from datetime import datetime

SERVER_HOST = 'localhost'


class ChatServer(object):
    """ An example chat server using select """

    def __init__(self, port_number, backlog=5):
        self.clients = 0
        self.client_map = {}
        self.chat_rooms = {}
        self.chat_rooms_count = 0
        self.outputs = []  # list output sockets
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port_number))
        self.server.listen(backlog)
        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

        print(f'Server listening to port: {port_number} ...')

    # Used to close the server.
    def sighandler(self, signum, frame):
        """ Clean up client outputs"""
        print('Shutting down server...')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server.close()

    # Gets the name of a specific client.
    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.client_map[client]
        host, client_name = info[0][0], info[1]
        return '@'.join((client_name, host))

    # Sends connected clients to the specific client.
    def send_connected_clients(self, client):
        connected_clients_list = []
        for client_data in self.client_map.values():
            connected_time = datetime.now() - client_data[2]
            connected_client_name = client_data[1]
            time_message = ""

            current_client = '@'.join((client_data[1], client_data[0][0]))
            if current_client == self.get_client_name(client):
                connected_client_name = connected_client_name + " (me)"

            if connected_time.seconds < 1:
                time_message = "now"
            elif connected_time.seconds < 60:
                time_message = str(round(connected_time.seconds)) + " sec ago"
            elif connected_time.seconds < 60*60:
                time_message = str(round(connected_time.seconds/60)) + " min ago"
            else:
                time_message = str(round(connected_time.seconds/(60*60))) + " hour ago"

            connected_clients_list.append(connected_client_name + " (" + time_message + ")")
        send_clients(client, connected_clients_list)  

    # Gets a string with the format hour:minute
    def get_current_time_stamp(self):
        current_time = datetime.now()
        return str(current_time.hour) + ":" + str(current_time.minute)
    
    # Gets the specific socket of a client with the matching name.
    def get_client_socket(self, client_name):
        for client_key in dict.keys(self.client_map):
            if self.client_map[client_key][1] == client_name:
                return client_key

    def run(self):
        inputs = [self.server, sys.stdin]
        self.outputs = []
        running = True
        while running:
            try:
                readable, writeable, exceptional = select.select(inputs, self.outputs, [])
            except select.error as e:
                print(e)
                break

            for sock in readable:
                """
                When a new client connects to the server.
                """
                if sock == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print(f'Chat server: got connection {client.fileno()} from {address}')

                    # Read the login name
                    cname = receive(client).split('NAME: ')[1]
                    time = datetime.now()

                    # Compute client name and send back
                    self.clients += 1
                    inputs.append(client)
                    self.client_map[client] = (address, cname, time)
                    self.outputs.append(client)

                    # Send clients list to all the connected clients.
                    for output in self.outputs:
                        send(output, "CLIENT_LIST") 
                        self.send_connected_clients(output)  
                        send(output, "UPDATE_ROOMS_LIST")
                        send_list(output, list(self.chat_rooms.keys()))

                elif sock == sys.stdin:
                    # handles standard input from terminal.
                    cmd = sys.stdin.readline().strip()
                    if cmd == 'list':
                        print(self.client_map.values())
                    elif cmd == 'quit':
                        running = False
                else:
                    try:
                        # handle all other sockets
                        data = receive(sock)
                        # When a client wants to end their connection.
                        if data == "END":
                            send(sock, "END")
                            print("trying to end the client.")
                        # When a client wants to send a one to one message.
                        elif data == "MESSAGE":
                            username = receive(sock)
                            message = receive(sock)

                            target_sock = self.get_client_socket(username)
                            current_time = self.get_current_time_stamp()

                            # sends the message to the themselves
                            send(sock, "MESSAGE")
                            send(sock, "Me (" + current_time + "): " + message)
                            
                            # sends a message to the target
                            send(target_sock, "MESSAGE")
                            send(target_sock, self.client_map[sock][1] + " (" + current_time + "): " + message)
                        # Creates a new chat room.
                        elif data == "CREATE_ROOM":
                            self.chat_rooms_count = self.chat_rooms_count + 1
                            room_name = "Room" + str(self.chat_rooms_count) + " by " + self.client_map[sock][1]
                            self.chat_rooms[room_name] = {
                                "members": [self.client_map[sock][1]],
                                "message_history": []
                            }

                            # Tell the client that we have created the room.
                            send(sock, "CREATE_ROOM")
                            send(sock, room_name)

                            # Tell everyone to update their rooms lists.
                            for output in self.outputs:
                                send(output, "UPDATE_ROOMS_LIST")
                                send_list(output, list(self.chat_rooms.keys()))
                        # Used to join a specific room.
                        elif data == "JOIN_ROOM":
                            # gets the room name.
                            room_name = receive(sock)
                            send(sock, "JOIN_ROOM")
                            send_list(sock, self.chat_rooms[room_name]["members"])
                        # Used to update the members list in the invite window.
                        elif data == "UPDATE_INVITE_WINDOW":
                            room_name = receive(sock)
                            room_members = self.chat_rooms[room_name]["members"]
                            non_room_members = []
                            for client in self.client_map:
                                client_name = self.get_client_name(client).split('@')[0]
                                if client_name not in room_members:
                                    non_room_members.append(client_name)
                            send(sock, "UPDATE_INVITE_WINDOW")
                            send_list(sock, non_room_members)
                        # Used to invite a new user to a chat room.
                        elif data == "INVITE":
                            room_name = receive(sock)
                            client_name = receive(sock)
                            self.chat_rooms[room_name]["members"].append(client_name)

                            # send to all members in the chat room.
                            for member_name in self.chat_rooms[room_name]["members"]:
                                destination_sock = self.get_client_socket(member_name)
                                send(destination_sock, "INVITED")
                                send_list(destination_sock, self.chat_rooms[room_name]["members"])
                        # When a user goes offline.
                        else:
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)
                            self.client_map.pop(sock)
                            # Update client list for other clients.
                            for output in self.outputs:
                                if output != sock:
                                    send(output, "CLIENT_LIST") 
                                    self.send_connected_clients(output)
                    except socket.error as e:
                        # Remove
                        self.client_map.pop(sock)
                        inputs.remove(sock)
                        self.outputs.remove(sock)

        print("closing")
        self.server.close()


if __name__ == "__main__":
    port = 9988
    name = "server"

    server = ChatServer(port)
    server.run()
