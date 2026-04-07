import tkinter as tk


class View:
    def __init__(self, controller, root):
        self.controller = controller
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.controller.on_closing)
        self.root.title('Control Panel')

        self.window_width = 500
        self.window_height = 700

        self.sessions_frame = None

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

        self.sessions_frame = tk.Frame(container, bg="#BFDCEB")
        self.sessions_frame.pack(fill="both", expand=True)


    def update_sessions(self, sessions: dict) -> None:
        if not self.sessions_frame or not self.root.winfo_exists():
            return

        try:
            for widget in list(self.sessions_frame.winfo_children()):
                if widget.winfo_exists():
                    widget.destroy()

            for s_id, s_data in sessions.items():
                # sessions{ "1": {"session_id": 1, "players": {...}, "state": "active"}, ... }
                session_id = s_data.get("session_id", s_id)
                player_count = len(s_data.get("players", {}))
                state = s_data.get("state", "inactive")
                btn_state = "normal"
                status_text = None
                status_color = None
                btn_text = None
                btn_bg = None
                btn_active = None
                btn_command = None

                if state == "active":
                    status_text = "Active"
                    status_color = "#28a745"

                    btn_text = "Stop"
                    btn_bg = "#FF5F5F"
                    btn_active = "#E14B4B"
                    btn_command = lambda sid=session_id: self.controller.pause_session(sid)

                elif state == "inactive":
                    status_text = "Inactive"
                    status_color = "#9e263a"

                    btn_text = "Inactive"
                    btn_state = "disabled"
                    btn_bg = "#FF5F5F"
                    btn_command = lambda sid=session_id: self.controller.pause_session(sid)

                row_frame = tk.Frame(self.sessions_frame, bg="#F5F9FC", pady=3)
                row_frame.pack(fill="x", padx=5, pady=5)

                tk.Label(row_frame, text=f"ID: {session_id}", font=("Arial", 11, "bold"),
                         bg="#F5F9FC", fg="#243B4A", width=10, anchor="w").pack(side="left", padx=3)

                tk.Label(row_frame, text=f"Players: {player_count}/2", font=("Arial", 10),
                         bg="#F5F9FC", fg="#555", width=12).pack(side="left", padx=3)

                tk.Label(row_frame, text=status_text, font=("Arial", 10, "italic"),
                         bg="#F5F9FC", fg=status_color, width=10).pack(side="left", padx=3)

                btn_frame = tk.Frame(row_frame, bg="#F5F9FC")
                btn_frame.pack(side="right")

                tk.Button(
                    btn_frame,
                    text=btn_text,
                    bg=btn_bg,
                    state=btn_state,
                    fg="white",
                    activebackground=btn_active,
                    width=8,
                    font=("Arial", 9, "bold"),
                    command=btn_command
                ).pack(side="right", padx=3)

                tk.Button(
                    btn_frame,
                    text="Details",
                    bg="#D0E4F0",
                    activebackground="#BFDCEB",
                    width=8,
                    font=("Arial", 9),
                    command=lambda sid=session_id: self.controller.show_details(sid)
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