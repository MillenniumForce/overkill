import socket
from overkill.utils.server_messaging_standards import NEW_CONNECTION
from overkill.utils.utils import decode_message, encode_dict


class mockWorker:
    def __init__(self, host, port):
        self.address = (host, port)

    def recieve_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.address))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)
                if not data:
                    raise Exception("No data recieved from master")
                return decode_message(data)

    def connect_to_master(self, master_address):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            connection_message = {"type": NEW_CONNECTION, "name": "test", "address": self.address}
            sock.connect(master_address)
            sock.sendall(encode_dict(connection_message))
            print("Sent: {}".format(connection_message))