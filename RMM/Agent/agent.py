import json
import socket
import threading
import time


def load_config(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)

config = load_config("config.json")
IP = config["IP"]
PORT = config["PORT"]

running = True
connected = False


def receive(client) -> None:
    global running, connected

    buffer = b""

    while running:
        try:
            data = client.recv(1024)
            if not data:
                break

            buffer += data

            while b"\n" in buffer:
                message, buffer = buffer.split(b"\n", 1)

                print(f"CLIENT: Received message: {message}")

                decoded = message.decode("utf-8")

                packet = json.loads(decoded)

                p_type = packet.get("type")
                p_data = packet.get("data")

                if p_type == "init":
                    my_id = p_data["your_id"]
                    print(my_id)

        except Exception as e:
            print(f"Receive error: {e}")
            break
    running = False
    connected = False
    client.close()


def connect() -> None:
    global running, connected
    global IP, PORT

    while running:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((IP, PORT))
            connected = True
            print(f"Connected to {IP}:{PORT}")
            break
        except (ConnectionRefusedError, socket.timeout, OSError):
            connected = False
            if client:
                client.close()
            time.sleep(1)

    if running:
        receive_thread = threading.Thread(
            target=receive,
            args=(client,),
            daemon=True
        )
        receive_thread.start()


def start():
    global running

    running = True
    connect_thread = threading.Thread(
        target=connect,
        daemon=True
    )
    connect_thread.start()

    try:
        while running:
            time.sleep(2)
    except KeyboardInterrupt:
        print("Client shutting down...")
        running = False


start()

