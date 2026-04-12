import tkinter as tk
from tkinter import messagebox


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
                    command= lambda ip=client_ip, port=c_port: self.open_powershell_window(ip, port)
                ).pack(side="right", padx=3)

        except tk.TclError:
            print("View: Update attempt failed")


    def open_powershell_window(self, ip: str, port: int) -> None:
        ps_window = tk.Toplevel(self.root)
        ps_window.title(f"PowerShell - {ip}")
        ps_window.geometry("400x150")
        ps_window.configure(bg="#F5F9FC")
        ps_window.resizable(False, False)
        ps_window.grab_set()

        self.center(ps_window, 400, 150)

        tk.Label(
            ps_window, text=f"Enter command for {ip}:",
            font=("Arial", 10), bg="#F5F9FC", fg="#243B4A"
        ).pack(pady=(15, 5))

        entry = tk.Entry(ps_window, font=("Consolas", 11), width=40)
        entry.pack(pady=5, padx=20)
        entry.focus_set()

        def send_command():
            command = entry.get()
            if command.strip():
                self.controller.powershell_command(ip, port, command)
                ps_window.destroy()
            else:
                messagebox.showwarning("Warning", "Command cannot be empty")

        btn_ok = tk.Button(
            ps_window, text="Execute", width=10,
            bg="#4CAF50", fg="white", font=("Arial", 9, "bold"),
            command=send_command
        )
        btn_ok.pack(pady=10)

        ps_window.bind('<Return>', lambda event: send_command())


    @staticmethod
    def center(window, width: int, height: int) -> None:
        window.update_idletasks()
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")


    def start(self):
        self.create_main_interface()