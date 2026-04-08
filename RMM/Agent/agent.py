import json
import os
import platform
import socket
import sys
import threading
import time
import winreg as reg

def load_config(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)

config = load_config("config.json")
IP = config["IP"]
PORT = config["PORT"]

running = True
connected = False


def add_to_startup(name="agent"):
    path = os.path.realpath(sys.argv[0])

    if path.endswith(".py"):
        executable = sys.executable
        address = f'"{executable}" "{path}"'
    else:
        address = f'"{path}"'

    try:
        key = reg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        with reg.OpenKey(key, key_path, 0, reg.KEY_WRITE) as registry_key:
            reg.SetValueEx(registry_key, name, 0, reg.REG_SZ, address)
            print(f"File was successfully added to startup: {name}")
    except Exception as e:
        print(f"Error adding to the registry: {e}")


def remove_from_startup(name="agent"):
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE) as registry_key:
        reg.DeleteValue(registry_key, name)


def shutdown_computer():
    current_os = platform.system().lower()

    if "windows" in current_os:
        os.system("shutdown /s /t 1")
    elif "linux" in current_os or "darwin" in current_os:
        os.system("sudo shutdown -h now")
    else:
        print("ОS not supported")


def receive(client) -> None:
    global running, connected

    buffer = b""
    try:
        while running:
            try:
                data = client.recv(1024)
                if not data:
                    break

                buffer += data

                while b"\n" in buffer:
                    message, buffer = buffer.split(b"\n", 1)
                    decoded = message.decode("utf-8")

                    print(f"AGENT: Received message: {message}")

                    packet = json.loads(decoded)

                    p_type = packet.get("type")

                    if p_type == "command":
                        if packet.get("command") == "shutdown":
                            print("Shutting down...")
                            # shutdown_computer()
                        elif packet.get("command") == "powershell":
                            print("Opening Powershell...")
                            os.system("start powershell")

            except socket.timeout:
                continue
            except (ConnectionResetError, ConnectionAbortedError):
                print(f"DEBUG: Agent connection reset.")
                break
    except Exception as e:
        print(f"Agent error: {e}")
    finally:
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
        print("Agent shutting down...")
        running = False


if __name__ == "__main__":
    # remove_from_startup()
    if platform.system().lower() == "windows":
        add_to_startup()

    try:
        start()
    except KeyboardInterrupt:
        running = False
        print("Agent stopped manually")


