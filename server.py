import select
import socket
import sys
import signal
import argparse

from utils import *

SERVER_HOST = 'localhost'


class ChatServer(object):
    """ An example chat server using select """

    def __init__(self, port, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = []  # list output sockets
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((SERVER_HOST, port))
        self.server.listen(backlog)
        # Catch keyboard interrupts
        signal.signal(signal.SIGINT, self.sighandler)

        print(f'Server listening to port: {port} ...')

    def sighandler(self, signum, frame):
        """ Clean up client outputs"""
        print('Shutting down server...')

        # Close existing client sockets
        for output in self.outputs:
            output.close()

        self.server.close()

    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))

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
                sys.stdout.flush()
                if sock == self.server:
                    # handle the server socket
                    client, address = self.server.accept()
                    print(
                        f'Chat server: got connection {client.fileno()} from {address}')
                    # Read the login name
                    cname = receive(client).split('NAME: ')[1]

                    # Compute client name and send back
                    self.clients += 1
                    send(client, f'CLIENT: {str(address[0])}')
                    inputs.append(client)

                    self.clientmap[client] = (address, cname)
                    # Send joining information to other clients
                    msg = f'\n(Connected: New client ({self.clients}) from {self.get_client_name(client)})'
                    for output in self.outputs:
                        send(output, msg)
                    self.outputs.append(client)

                elif sock == sys.stdin:
                    # didn't test sys.stdin on windows system
                    # handle standard input
                    cmd = sys.stdin.readline().strip()
                    if cmd == 'list':
                        print(self.clientmap.values())
                    elif cmd == 'quit':
                        running = False
                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data == "GET_ALL_CLIENTS":
                            print("sending a list of clients to '{}'".format(self.get_client_name(sock)))
                            client_name_list = []
                            for client_data in self.clientmap.values():
                                client_name_list.append(client_data[1])
                            send_clients(sock, client_name_list)
                        elif data:
                            # Send as new client's message...
                            msg = f'\n#[{self.get_client_name(sock)}]>> {data}'

                            # Send data to all except ourself
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                        else:
                            print(f'Chat server: {sock.fileno()} hung up')
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)
                            # Sending client leaving information to others
                            msg = f'\n(Now hung up: Client from {self.get_client_name(sock)})'
                            self.clientmap.pop(sock)

                            for output in self.outputs:
                                send(output, msg)
                    except socket.error as e:
                        # Remove
                        inputs.remove(sock)
                        self.outputs.remove(sock)

        print("closing")
        self.server.close()


if __name__ == "__main__":
    port = 9988
    name = "server"

    server = ChatServer(port)
    server.run()
