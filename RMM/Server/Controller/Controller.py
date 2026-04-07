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

        self.current_sessions = {}


    def poll_queue(self) -> None:
        while not self.queue.empty():
            packet = self.queue.get()
            print(f"CONTROLLER: Received a packet: {packet}")
            p_type = packet.get("type")
            p_data = packet.get("data")

            if p_type == "init":
                pass

            elif p_type == "update":
                self.current_sessions = p_data.get("sessions", {})

                if self.current_sessions is not None and self.view.root.winfo_exists() and self.view.root.winfo_viewable():
                    self.view.update_sessions(self.current_sessions)

            elif p_type == "error":
                print(f"Server Error: {packet.get('message')}")

        self.root.after(100, self.poll_queue)


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
