import os
import tkinter as tk
from Server.View.View import View


class Controller:
    def __init__(self, model, queue):
        self.model = model
        self.queue = queue

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.view = View(self, self.root)

        self.current_clients = {}


    def poll_queue(self) -> None:
        while not self.queue.empty():
            packet = self.queue.get()
            print(f"CONTROLLER: Received a packet: {packet}")
            p_type = packet.get("type")
            p_data = packet.get("data")

            if p_type == "update":
                self.current_clients = p_data.get("clients", {})

                if self.current_clients is not None and self.view.root.winfo_exists() and self.view.root.winfo_viewable():
                    self.view.update_clients(self.current_clients)

            elif p_type == "file_list":
                if self.current_clients is not None and self.view.root.winfo_exists() and self.view.root.winfo_viewable():
                    self.view.update_file_list(packet.get("ip"), packet.get("data"))

            elif p_type == "error":
                print(f"Server Error: {packet.get('message')}")

        self.root.after(100, self.poll_queue)


    def shutdown_user_computer(self, ip, port):
        self.model.shutdown_user_computer(ip, port)


    def powershell_command(self, ip, port, command):
        self.model.powershell_command(ip, port, command)


    def open_user_files(self, ip, port):
        self.model.open_user_files(ip, port)


    def request_subfolder(self, ip, port, path):
        self.model.request_subfolder(ip, port, path)


    def upload_file(self, ip, file_path):
        self.model.send_file_to_client(ip, file_path)


    def start(self):
        self.model.start()
        self.view.start()
        self.poll_queue()
        self.root.mainloop()


    def on_closing(self):
        print("Closing client...")
        self.model.stop()

        try:
            self.model.socket.close()
        except:
            pass

        self.root.destroy()

        os._exit(0)
