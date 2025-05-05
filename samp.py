import customtkinter as ctk
from tkinter import messagebox, Listbox, SINGLE
from tkcalendar import Calendar
import json

# File constants
EVENTS_FILE = "events_gui.json"
USERS_FILE = "users.json"

# Load/save functions
def load_events():
    try:
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_events(events):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=4)

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Registration Window
class RegistrationWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Register")
        self.geometry("400x350")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.configure(fg_color="#a64ca6")  # Purple background

        ctk.CTkLabel(self, text="New Username:").pack(pady=(20, 5))
        self.entry_user = ctk.CTkEntry(self)
        self.entry_user.pack()

        ctk.CTkLabel(self, text="Password:").pack(pady=(15, 5))
        self.entry_pw = ctk.CTkEntry(self, show="*")
        self.entry_pw.pack()

        ctk.CTkLabel(self, text="Confirm Password:").pack(pady=(15, 5))
        self.entry_pw2 = ctk.CTkEntry(self, show="*")
        self.entry_pw2.pack()

        ctk.CTkButton(self, text="Register", command=self.register).pack(pady=20)

    def on_close(self):
        messagebox.showwarning("Registration Required", "You must complete registration before exiting.")

    def register(self):
        uname = self.entry_user.get().strip()
        pw = self.entry_pw.get()
        pw2 = self.entry_pw2.get()

        if not uname or not pw:
            messagebox.showwarning("Error", "Username and password cannot be empty.")
            return
        if pw != pw2:
            messagebox.showwarning("Error", "Passwords do not match.")
            return

        users = load_users()
        if uname in users:
            messagebox.showwarning("Error", "Username already exists.")
            return

        users[uname] = pw
        save_users(users)
        messagebox.showinfo("Success", "Registration complete! Please log in.")
        self.destroy()

# Login Window
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("400x300")
        self.configure(fg_color="#a64ca6")  # Purple background

        ctk.CTkLabel(self, text="Username:").pack(pady=(25, 5))
        self.entry_user = ctk.CTkEntry(self)
        self.entry_user.pack()

        ctk.CTkLabel(self, text="Password:").pack(pady=(15, 5))
        self.entry_pw = ctk.CTkEntry(self, show="*")
        self.entry_pw.pack()

        ctk.CTkButton(self, text="Login", command=self.check_login).pack(pady=(20, 5))
        ctk.CTkButton(self, text="Register", command=self.open_registration).pack()

    def open_registration(self):
        self.withdraw()
        reg_win = RegistrationWindow()
        reg_win.mainloop()
        self.deiconify()

    def check_login(self):
        users = load_users()
        u = self.entry_user.get().strip()
        p = self.entry_pw.get()
        if users.get(u) == p:
            self.destroy()
            CalendarApp().mainloop()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password.")

# Calendar App
class CalendarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📅 Laica's Calendar App")
        self.geometry("950x650")
        self.configure(fg_color="#a64ca6")  # Purple background
        self.events = load_events()

        self.main_frame = ctk.CTkFrame(self, fg_color="#b266b2")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.cal_frame = ctk.CTkFrame(self.main_frame, fg_color="#c17dc1")
        self.cal_frame.pack(side="left", fill="y", padx=(0, 20))

        self.calendar = Calendar(
            self.cal_frame,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            font=("Helvetica", 20),
            showweeknumbers=False
        )
        self.calendar.pack(padx=20, pady=20)

        self.event_frame = ctk.CTkFrame(self.main_frame, fg_color="#d98cd9")
        self.event_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(self.event_frame, text="📌 Event Title", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=10, pady=(30, 5))
        self.text_event = ctk.CTkTextbox(self.event_frame, height=60)
        self.text_event.pack(fill="x", padx=10, pady=(0, 20))

        self.btn_frame = ctk.CTkFrame(self.event_frame, fg_color="transparent")
        self.btn_frame.pack(pady=(0, 20))
        ctk.CTkButton(self.btn_frame, text="Add Event", command=self.add_event).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.btn_frame, text="View Events", command=self.view_events).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.btn_frame, text="Delete Event", command=self.delete_event).grid(row=0, column=2, padx=10)

        self.label_list = ctk.CTkLabel(self.event_frame, text="Events on selected date:")
        self.label_list.pack(anchor="w", padx=10, pady=(0, 5))

        self.listbox = Listbox(self.event_frame, height=10, selectmode=SINGLE)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def safe_widget_call(self, widget, method, *args, **kwargs):
        if widget.winfo_exists():
            return getattr(widget, method)(*args, **kwargs)

    def add_event(self):
        date = self.calendar.get_date()
        title = self.text_event.get("0.0", "end").strip()
        if not title:
            messagebox.showwarning("Error", "Event title cannot be empty.")
            return
        self.events.setdefault(date, []).append(title)
        save_events(self.events)
        messagebox.showinfo("Success", f"Event added for {date}")
        self.text_event.delete("0.0", "end")
        self.view_events()

    def view_events(self):
        if not self.listbox.winfo_exists():
            return
        date = self.calendar.get_date()
        self.safe_widget_call(self.listbox, "delete", 0, "end")
        events = self.events.get(date, [])
        if not events:
            self.safe_widget_call(self.listbox, "insert", "end", "No events on this date.")
        else:
            for evt in events:
                self.safe_widget_call(self.listbox, "insert", "end", evt)

    def delete_event(self):
        if not self.listbox.winfo_exists():
            return
        date = self.calendar.get_date()
        selected_idx = self.listbox.curselection()
        if not selected_idx:
            messagebox.showwarning("Error", "Please select an event to delete.")
            return

        selected_event = self.listbox.get(selected_idx)
        if date in self.events and selected_event in self.events[date]:
            self.events[date].remove(selected_event)
            if not self.events[date]:
                del self.events[date]
            save_events(self.events)
            messagebox.showinfo("Deleted", f"Deleted: {selected_event}")
            self.view_events()
        else:
            messagebox.showerror("Error", "Event not found.")

# Launch the app
if __name__ == "__main__":
    LoginWindow().mainloop()
