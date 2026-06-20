import os
import psutil
import json
import winreg
import urllib.request
import tkinter as tk
import threading
from datetime import datetime

BLACKLIST = [
    "eulen", "redengine", "lynx", "hornet", "fivex",
    "executor", "injector", "kiddions", "cherax",
    "stand", "midnight", "2take1", "skulled"
]

results = {
    "scan_time": str(datetime.now()),
    "pc_user": os.getlogin(),
    "flagged": [],
    "processes": [],
    "prefetch": [],
    "recent_files": [],
    "last_activity": [],
    "discord": {"installed": False, "version": None, "suspicious_files": []},
    "clean": True
}

def flag(t, name, reason):
    results["flagged"].append({"type": t, "name": name, "reason": reason})
    results["clean"] = False

class ScannerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.geometry("420x340")
        self.root.configure(bg="#0a0a0a")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 210
        y = (self.root.winfo_screenheight() // 2) - 170
        self.root.geometry(f"420x340+{x}+{y}")
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.pin = tk.StringVar()
        self.status = tk.StringVar(value="Enter your PIN to begin")
        self.scanning = False
        self.build_ui()

    def start_move(self, e):
        self._x = e.x
        self._y = e.y

    def do_move(self, e):
        x = self.root.winfo_x() + e.x - self._x
        y = self.root.winfo_y() + e.y - self._y
        self.root.geometry(f"+{x}+{y}")

    def build_ui(self):
        close_btn = tk.Label(self.root, text="X", bg="#0a0a0a", fg="#333",
                             cursor="hand2", font=("Arial", 12))
        close_btn.place(x=395, y=8)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())

        tk.Label(self.root, text="/\\   /\\", bg="#0a0a0a", fg="#f0a500",
                 font=("Courier New", 20, "bold")).pack(pady=(30, 0))
        tk.Label(self.root, text="\\ \\_/ /", bg="#0a0a0a", fg="#f0a500",
                 font=("Courier New", 20, "bold")).pack(pady=(0, 0))
        tk.Label(self.root, text=" \\V/ ", bg="#0a0a0a", fg="#c47f00",
                 font=("Courier New", 18, "bold")).pack(pady=(0, 5))

        tk.Label(self.root, text="STARK  V3", bg="#0a0a0a", fg="#555",
                 font=("Arial", 9, "bold")).pack()

        tk.Label(self.root, text="-" * 45, bg="#0a0a0a",
                 fg="#1a1a1a").pack(pady=8)

        pin_frame = tk.Frame(self.root, bg="#0a0a0a")
        pin_frame.pack(pady=5)

        tk.Label(pin_frame, text="PIN CODE", bg="#0a0a0a", fg="#444",
                 font=("Arial", 8)).pack()

        self.pin_entry = tk.Entry(pin_frame, textvariable=self.pin,
                                  bg="#111", fg="#f0a500",
                                  insertbackground="#f0a500",
                                  font=("Courier New", 18, "bold"),
                                  width=10, justify="center", relief="flat",
                                  highlightthickness=1,
                                  highlightcolor="#f0a500",
                                  highlightbackground="#222")
        self.pin_entry.pack(pady=5)

        self.scan_btn = tk.Button(self.root, text="START SCAN",
                                  bg="#f0a500", fg="#000",
                                  font=("Arial", 10, "bold"),
                                  relief="flat", cursor="hand2",
                                  padx=30, pady=8,
                                  command=self.start_scan)
        self.scan_btn.pack(pady=8)

        self.status_label = tk.Label(self.root, textvariable=self.status,
                                     bg="#0a0a0a", fg="#555",
                                     font=("Arial", 9))
        self.status_label.pack(pady=5)

        self.progress_frame = tk.Frame(self.root, bg="#111",
                                       width=300, height=4)
        self.progress_frame.pack(pady=5)
        self.progress_frame.pack_propagate(False)

        self.progress_bar = tk.Frame(self.progress_frame, bg="#f0a500",
                                     width=0, height=4)
        self.progress_bar.place(x=0, y=0)

    def update_status(self, msg, progress=0):
        self.status.set(msg)
        self.progress_bar.configure(width=int(300 * progress))
        self.root.update()

    def start_scan(self):
        pin_code = self.pin.get().strip().upper()
        if not pin_code:
            self.status.set("Please enter your PIN code")
            return
        self.scanning = True
        self.scan_btn.configure(state="disabled", bg="#333", fg="#666")
        self.pin_entry.configure(state="disabled")
        thread = threading.Thread(target=self.run_scan, args=(pin_code,))
        thread.daemon = True
        thread.start()

    def run_scan(self, pin_code):
        try:
            self.update_status("Scanning processes...", 0.1)
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    name = proc.info['name']
                    results["processes"].append(name)
                    for keyword in BLACKLIST:
                        if keyword in name.lower():
                            flag("Process", name, f"Matched: {keyword}")
                except Exception:
                    pass

            self.update_status("Scanning prefetch...", 0.3)
            try:
                prefetch_path = "C:\\Windows\\Prefetch"
                if os.path.exists(prefetch_path):
                    for file in os.listdir(prefetch_path):
                        results["prefetch"].append(file)
                        for keyword in BLACKLIST:
                            if keyword in file.lower():
                                flag("Prefetch", file, f"Matched: {keyword}")
            except Exception:
                pass

            self.update_status("Scanning Discord...", 0.5)
            discord_paths = [
                os.path.expandvars(r"%APPDATA%\discord"),
                os.path.expandvars(r"%APPDATA%\discordcanary"),
            ]
            for dp in discord_paths:
                if os.path.exists(dp):
                    results["discord"]["installed"] = True
                    try:
                        for folder in os.listdir(dp):
                            if folder.startswith("app-"):
                                results["discord"]["version"] = folder
                    except Exception:
                        pass

            self.update_status("Scanning recent activity...", 0.7)
            try:
                recent_path = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Recent")
                if os.path.exists(recent_path):
                    files_with_time = []
                    for file in os.listdir(recent_path):
                        full_path = os.path.join(recent_path, file)
                        try:
                            mod_time = os.path.getmtime(full_path)
                            files_with_time.append((file, mod_time))
                        except Exception:
                            pass
                    files_with_time.sort(key=lambda x: x[1], reverse=True)
                    for file, mod_time in files_with_time[:20]:
                        time_str = datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                        results["recent_files"].append(file)
                        results["last_activity"].append({"file": file, "time": time_str})
                        for keyword in BLACKLIST:
                            if keyword in file.lower():
                                flag("Recent File", file, f"Matched: {keyword}")
            except Exception:
                pass

            self.update_status("Scanning registry...", 0.85)
            try:
                bam_path = r"SYSTEM\CurrentControlSet\Services\bam\State\UserSettings"
                reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, bam_path)
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(reg, i)
                        i += 1
                    except OSError:
                        break
            except Exception:
                pass

            self.update_status("Done!", 1.0)

        except Exception as e:
            self.update_status(f"Error: {e}", 0)

        finally:
            self.scan_btn.configure(state="normal", bg="#f0a500", fg="#000")
            self.pin_entry.configure(state="normal")
            self.scanning = False

        result_json = json.dumps(results, indent=2)
        try:
            req = urllib.request.Request(
                "https://example.com/submit",
                data=result_json.encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=10)
        except Exception:
            pass

app = ScannerApp()
app.root.mainloop()