import select
import socket
import sys
import signal
import argparse

from utils import *
from datetime import datetime

SERVER_HOST = 'localhost'


class ChatServer(object):
    """ An example chat server using select """

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.chatroom_map = {}
        self.outputs = []  # list output sockets
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        self.server.listen(backlog)
        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

        print(f'Server listening to port: {port} ...')

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
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

    # Sends connected clients to the specific client.
    def send_connected_clients(self, client):
        connected_clients_list = []
        for client_data in self.clientmap.values():
            connected_time = datetime.now() - client_data[2]
            connected_client_name = client_data[1]
            time_message = ""

            if client_data[1] == self.get_client_name(client):
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
                    self.clientmap[client] = (address, cname, time)
                    self.outputs.append(client)

                    # Send clients list to all the connected clients.
                    for output in self.outputs:
                        send(output, "CLIENT_LIST") 
                        self.send_connected_clients(output)              

                elif sock == sys.stdin:
                    # handles standard input from terminal.
                    cmd = sys.stdin.readline().strip()
                    if cmd == 'list':
                        print(self.clientmap.values())
                    elif cmd == 'quit':
                        running = False
                else:
                    try:
                        # handle all other sockets
                        data = receive(sock)
                        if data == "END":
                            send(sock, "END")
                            print("trying to end the client.")
                        else:
                            # When a user goes offline.
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)
                            self.clientmap.pop(sock)
                    except socket.error as e:
                        # Remove
                        self.clientmap.pop(sock)
                        inputs.remove(sock)
                        self.outputs.remove(sock)

        print("closing")
        self.server.close()


if __name__ == "__main__":
    port = 9988
    name = "server"

    server = ChatServer(port)
    server.run()
