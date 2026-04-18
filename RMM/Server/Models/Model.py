import hashlib
import socket
import threading
import json

from Server.Models.ClientData import ClientData

class Model:
    def __init__(self, config, queue):
        self.config = config
        self.queue = queue

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

        self.server = None
        self.clients = {}
        self.running = False
        self.last_clients_hash = {}
        self.session_data_sender = None
        self.stop_event = None


    def handle_client(self, client: ClientData) -> None:
        try:
            self.clients[client.ip_address].online_status = True
            buffer = b""

            while self.running:
                data = client.conn.recv(4096)
                if not data:
                    break

                buffer += data
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    packet = json.loads(line.decode('utf-8'))

                    if packet.get("type") == "response":
                        if packet.get("command") == "files":
                            file_names = packet.get("data")
                            client.file_list = file_names
                            print(f"Files from {client.ip_address}: {file_names}")

                            self.queue.put({
                                "type": "file_list",
                                "ip": client.ip_address,
                                "data": file_names
                            })

                    elif packet.get("type") == "error":
                        self.queue.put({
                            "type": "error",
                            "ip": client.ip_address,
                            "message": packet.get("message")
                        })
        except:
            pass
        finally:
            client.conn.close()
            if client.ip_address in self.clients:
                self.clients[client.ip_address].online_status = False


    def update_sessions(self):
        while not self.stop_event.is_set():
            try:
                serializable_sessions = {
                    c_port: c_obj.to_dict() for c_port, c_obj in list(self.clients.items())
                }

                full_data = {"clients": serializable_sessions}

                current_data_str = json.dumps(full_data, sort_keys=True)
                current_hash = hashlib.md5(current_data_str.encode()).hexdigest()

                if current_hash == self.last_clients_hash:
                    pass
                else:
                    print(f"Sending update with {len(serializable_sessions)} clients")
                    self.last_clients_hash = current_hash
                    packet = {
                        "type": "update",
                        "data": full_data
                    }
                    self.queue.put(packet)

            except Exception as e:
                print(f"Failed to send update to admin: {e}")

            stopped = self.stop_event.wait(timeout=2)
            if stopped:
                break


    def shutdown_user_computer(self, ip, port):
        packet = {
            "type": "command",
            "command": "shutdown",
        }

        packet_bytes = json.dumps(packet).encode('utf-8')
        self.clients[ip].conn.sendall(packet_bytes + b"\n")


    def powershell_command(self, ip, port, command):
        packet = {
            "type": "command",
            "command": "powershell",
            "data": command,
        }

        packet_bytes = json.dumps(packet).encode('utf-8')
        self.clients[ip].conn.sendall(packet_bytes + b"\n")


    def open_user_files(self, ip, port):
        packet = {
            "type": "request",
            "command": "files",
        }
        packet_bytes = json.dumps(packet).encode('utf-8')
        self.clients[ip].conn.sendall(packet_bytes + b"\n")


    def request_subfolder(self, ip, port, path):
        packet = {
            "type": "request",
            "command": "files",
            "path": path
        }
        try:
            packet_bytes = json.dumps(packet).encode('utf-8')
            self.clients[ip].conn.sendall(packet_bytes + b"\n")
        except Exception as e:
            print(f"Error sending subfolder request: {e}")


    def is_connected(self):
        return bool(self.clients)


    def accept_clients(self) -> None:
        while self.running:
            try:
                conn, addr = self.server.accept()
                print(f"Connection from {addr}")

                client = ClientData(conn, addr[0], addr[1])

                self.clients[client.ip_address] = client

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client,),
                    daemon=True
                )
                thread.start()

            except Exception as e:
                print(f"Accept error: {e}")


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

        self.stop_event = threading.Event()
        self.session_data_sender = threading.Thread(target=self.update_sessions, daemon=True)
        self.session_data_sender.start()


    def stop(self) -> None:
        self.running = False

        for client  in self.clients.values():
            try:
                client.conn.close()
            except:
                print("Error closing connection with client")
                pass

        self.stop_event.set()
        self.session_data_sender.join(timeout=3)

        try:
            self.server.close()
        except:
            print("Error closing server")
            pass
        self.clients.clear()
        print("Threads closed")