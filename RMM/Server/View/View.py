import tkinter as tk


class View:
    def __init__(self, controller, root):
        self.controller = controller
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)
        self.root.title('Control Panel')

        self.window_width = 500
        self.window_height = 700

        self.clients_frame = None

        self.root.withdraw()


    def create_main_interface(self) -> None:
        self.root.deiconify()
        self.center(self.root, self.window_width, self.window_height)
        self.root.configure(background="#EAF4F9")

        # --- Top bar ---
        top_bar = tk.Frame(self.root, bg="#EAF4F9", padx=20, pady=10)
        top_bar.pack(fill="x")

        tk.Label(
            top_bar, text="Active Sessions",
            font=("Arial", 14, "bold"), bg="#EAF4F9", fg="#243B4A"
        ).pack()

        container = tk.Frame(self.root, bg="#BFDCEB", padx=10, pady=5)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.clients_frame = tk.Frame(container, bg="#BFDCEB")
        self.clients_frame.pack(fill="both", expand=True)


    def update_clients(self, clients: dict) -> None:
        if not self.clients_frame or not self.root.winfo_exists():
            return

        try:
            for widget in list(self.clients_frame.winfo_children()):
                if widget.winfo_exists():
                    widget.destroy()

            for c_port, c_data in clients.items():
                client_ip = c_data.get("ip_address", "N/A")


                row_frame = tk.Frame(self.clients_frame, bg="#F5F9FC", pady=3)
                row_frame.pack(fill="x", padx=5, pady=5)

                tk.Label(row_frame, text=f"IP: {client_ip}", font=("Arial", 11, "bold"),
                         bg="#F5F9FC", fg="#243B4A", width=10, anchor="w").pack(side="left", padx=3)

                btn_frame = tk.Frame(row_frame, bg="#F5F9FC")
                btn_frame.pack(side="right")

                tk.Button(
                    btn_frame,
                    text="Turn of",
                    bg="#4CAF50",
                    fg="white",
                    activebackground="#45a049",
                    width=8,
                    font=("Arial", 9, "bold"),
                    command=lambda ip=client_ip, port=c_port:  self.controller.shutdown_user_computer(ip, port)
                ).pack(side="right", padx=3)

                tk.Button(
                    btn_frame,
                    text="Powershell",
                    bg="#D0E4F0",
                    activebackground="#BFDCEB",
                    width=8,
                    font=("Arial", 9),
                    command= lambda ip=client_ip, port=c_port: self.controller.powershell_command(ip, port)
                ).pack(side="right", padx=3)

        except tk.TclError:
            print("View: Update attempt failed")


    @staticmethod
    def center(window, width: int, height: int) -> None:
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")


    def start(self):
        self.create_main_interface()