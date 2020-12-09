import socket
import threading
import errno

# Connection Data
host = '192.168.1.62.'
port = 55500

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []


def close():
    server.close()


# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)


# Récupère les messages pour ensuite les broadcast
def handle(client):
    while True:
        try:
            nickname = nicknames[clients.index(client)]
            # Broadcasting Messages
            msg = message = client.recv(1024)
            broadcast(message)
        except:
            if client in clients:
                # Removing And Closing Clients
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast('{} a quitté la salle !\n'.format(nickname).encode())
                nicknames.remove(nickname)
                break


# Receiving / Listening Function
def receive():
    global server
    while True:
        try:
            # Accept Connection
            client, address = server.accept()
            print("Connecté avec : {}".format(str(address)))

            # Request And Store Nickname
            client.send('NICK'.encode())
            nickname = client.recv(1024).decode()

            if nickname == 'admin':
                client.send('PASS'.encode())
                password = client.recv(1024).decode()
                if password != 'adminpass':
                    client.send('REFUSE'.encode())
                    client.close()
                    continue

            nicknames.append(nickname)
            clients.append(client)

            # Print And Broadcast Nickname
            print("Pseudo : {}".format(nickname))
            broadcast("{} a rejoint !\n".format(nickname).encode())

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except OSError as ex:
            if ex.errno in (errno.EBADF, errno.EINVAL):
                break
            raise
        except KeyboardInterrupt:
            close()
            print('Le serveur a fermé')


def write():
    while True:
        message = input('')
        if message == 'print clients':
            print(clients)


receive()
