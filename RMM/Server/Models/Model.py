import socket
import threading
from Server.Models.ClientData import ClientData

class Model:
    def __init__(self, config, queue):
        self.config = config
        self.queue = queue

        self.server = None
        self.clients = {}
        self.running = False

        self.HOST = config["HOST"]
        self.PORT = config["PORT"]
        self.SQL_SERVER = config["SQL_SERVER"]
        self.SQL_DATABASE = config["SQL_DATABASE"]
        self.CONN_STR = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={self.SQL_SERVER};'
            f'DATABASE={self.SQL_DATABASE};'
            'Trusted_Connection=yes;'
        )


    def handle_client(self, client: ClientData) -> None:
        try:
            while self.running:
                data = client.conn.recv(1024)
                if not data:
                    break

                message = data.decode()
                self.queue.put((client.id, message))

                if message == "stop":
                    self.running = False
        except:
            pass
        finally:
            client.conn.close()
            if client.port in self.clients:
                del self.clients[client.port]


    def accept_clients(self) -> None:
        while self.running:
            try:
                conn, addr = self.server.accept()
                conn.settimeout(5.0)
                print(f"Connection from {addr}")

                client = ClientData(conn, addr[0], addr[1])
                self.clients[client.port] = client

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client,),
                    daemon=True
                )
                thread.start()

            except Exception as e:
                print(f"Accept error: {e}")


    def is_connected(self):
        return bool(self.clients)


    def start(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.HOST, self.PORT))
        self.server.listen()
        self.running = True

        accept_thread = threading.Thread(
            target=self.accept_clients,
            daemon=True
        )
        accept_thread.start()


    def stop(self) -> None:
        self.running = False

        for client  in self.clients.values():
            try:
                client.conn.close()
            except:
                print("Error closing connection with client")
                pass

        try:
            self.server.close()
        except:
            print("Error closing server")
            pass
        self.clients.clear()
        print("Threads closed")