import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox

import obsws_python as obs
import psutil
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ScoreTracker:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.log_file_path = os.path.join(output_path, "processed_files.txt")
        self.high_scores = {}
        self.processed_files = set()
        os.makedirs(output_path, exist_ok=True)
        self.load_processed_files()
        self.load_high_scores()

    def load_processed_files(self):
        if os.path.exists(self.log_file_path):
            with open(self.log_file_path, "r") as log_file:
                self.processed_files = set(log_file.read().splitlines())

    def load_high_scores(self):
        for file_name in os.listdir(self.output_path):
            if file_name.endswith(".csv"):
                scenario_name = file_name[:-4]
                file_path = os.path.join(self.output_path, file_name)
                try:
                    with open(file_path, "r") as f:
                        lines = f.readlines()

                        for line in lines:
                            if "score=" in line.lower():
                                score = float(line.split("=")[1].strip())
                                self.high_scores[scenario_name] = score
                                break

                except Exception as e:
                    print(f"Error loading high score for {scenario_name}: {e}")

    def process_new_score_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                lines = file.readlines()
                scenario_name = None
                new_score = None

                for line in lines:
                    if "Scenario:," in line:
                        scenario_name = line.split(",")[1].strip()

                    elif "Score:," in line:
                        new_score = float(line.split(",")[1].strip())

                    elif "Scenario=" in line:
                        scenario_name = line.split("=")[1].strip()

                    elif "score=" in line:
                        new_score = float(line.split("=")[1].strip())

                if scenario_name and new_score is not None:
                    current_high_score = self.high_scores.get(scenario_name, 0)

                    if new_score > current_high_score:
                        self.high_scores[scenario_name] = new_score
                        self.save_high_score(scenario_name, new_score)
                        return True, scenario_name, new_score
            return False, scenario_name, new_score

        except Exception as e:
            print(f"Error processing score file {file_path}: {e}")
            return False, None, None

    def save_high_score(self, scenario_name, score):
        output_file = os.path.join(self.output_path, f"{scenario_name}.csv")
        output_content = f"Scenario= {scenario_name}\nscore= {score}\n"

        with open(output_file, "w") as file:
            file.write(output_content)

    def log_processed_file(self, file_name):
        if file_name not in self.processed_files:
            self.processed_files.add(file_name)

            with open(self.log_file_path, "a") as log_file:
                log_file.write(file_name + "\n")


class AutoClipper:
    def __init__(self):
        self.user = getpass.getuser()
        self.stats_dir = r"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
        self.parsed_stats_dir = os.path.join(self.stats_dir, "parsed_scens")
        self.scenarios = set()
        self.observer = None
        self.running = False
        self.obs_client = None
        self.score_tracker = ScoreTracker(self.stats_dir, self.parsed_stats_dir)
        self.config_file = "auto_clipper_config.json"
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.scenarios = set(config.get("scenarios", []))
                    self.stats_dir = config.get("stats_dir", self.stats_dir)

        except Exception as e:
            print(f"Error loading config: {e}")

    def save_config(self):
        config = {"scenarios": list(self.scenarios), "stats_dir": self.stats_dir}

        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def connect_obs(self, host="localhost", port=4455, password=""):
        try:
            self.obs_client = obs.ReqClient(host=host, port=port, password=password)
            self.start_replay_buffer()
            return True

        except Exception as e:
            messagebox.showerror(
                "OBS Connection Error", f"Failed to connect to OBS: {str(e)}"
            )
            self.stop_replay_buffer()
            terminate_process()
            return False

    def start_replay_buffer(self):
        try:
            if self.obs_client:
                try:
                    self.obs_client.start_replay_buffer()

                except Exception as e:
                    messagebox.showerror(
                        "Replay Buffer Error",
                        f"Failed to start Replay Buffer: {str(e)}",
                    )
                    return False
                return True

        except Exception as e:
            messagebox.showerror(
                "Replay Buffer Error", f"Failed to start Replay Buffer: {str(e)}"
            )
            return False

    def stop_replay_buffer(self):
        try:
            if self.obs_client:
                try:
                    self.obs_client.stop_replay_buffer()
                    print("Replay buffer stopped")
                except Exception as e:
                    print(f"Error stopping replay buffer: {e}")

        except Exception as e:
            print(f"Error stopping replay buffer: {e}")

    def start_monitoring(self):
        if not self.running:
            self.running = True
            event_handler = ScoreEventHandler(self, self.score_tracker)
            self.observer = Observer()
            self.observer.schedule(event_handler, self.stats_dir, recursive=False)
            self.observer.start()

    def stop_monitoring(self):
        if self.running:
            self.running = False

            if self.observer:
                self.observer.stop()
                self.observer.join()
            self.stop_replay_buffer()

    def trigger_clip(self, scenario, score):
        try:
            if self.obs_client:
                try:
                    self.obs_client.save_replay_buffer()
                except:
                    try:
                        self.obs_client.trigger_media_input_action(
                            input_name="ReplayBuffer", action_name="ReplayBuffer.Save"
                        )

                    except Exception as e:
                        print(f"Error triggering clip (alternative method): {e}")

        except Exception as e:
            print(f"Error triggering clip: {e}")
        time.sleep(0.5)
        save_obs_replay(scenario, score)

    def add_scenario(self, scenario_name):
        self.scenarios.add(scenario_name)
        self.save_config()

    def add_scenarios_from_playlist(self, playlist_path):
        try:
            with open(playlist_path, "r") as f:
                playlist_data = json.load(f)

                for scenario in playlist_data["scenarioList"]:
                    self.scenarios.add(scenario["scenario_name"])
            self.save_config()

        except Exception as e:
            print(f"Error loading playlist: {e}")


class ScoreEventHandler(FileSystemEventHandler):
    def __init__(self, clipper, score_tracker):
        self.clipper = clipper
        self.score_tracker = score_tracker
        super().__init__()

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".csv"):
            print(event.is_directory)
            return
        time.sleep(0.1)
        self.process_score_file(event.src_path)

    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(".csv"):
            return
        time.sleep(0.1)
        self.process_score_file(event.src_path)

    def process_score_file(self, file_path):
        file_name = os.path.basename(file_path)
        scenario_name = os.path.splitext(file_name)[0]
        print(f"Processing file: {file_name}, Scenario name: {scenario_name}")

        if scenario_name not in self.clipper.scenarios:
            print(
                f"Scenario {scenario_name} not in monitored scenarios: {self.clipper.scenarios}"
            )
            return
        print(f"schizo{scenario_name}")
        is_new_high_score, scenario, score = self.score_tracker.process_new_score_file(
            file_path
        )

        if is_new_high_score and scenario in self.clipper.scenarios:
            print(f"New high score for {scenario}: {score}")
            self.clipper.trigger_clip(scenario, score)


class ConfigWindow:
    def __init__(self, root, colors, clipper):
        self.window = tk.Toplevel(root)
        self.window.title("Configure Scenarios")
        self.window.configure(bg=colors["Background"])
        self.window.geometry("400x400")
        self.clipper = clipper
        self.colors = colors
        self.create_gui()

    def terminate_process1(self):
        self.clipper.stop_replay_buffer()
        if self.clipper.stop_replay_buffer():
            print("replay buffer stopped")
        terminate_process()

    def create_gui(self):
        scenario_frame = tk.LabelFrame(
            self.window,
            text="Add Individual Scenarios",
            bg=self.colors["Secondary"],
            fg="white",
        )
        scenario_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Button(
            scenario_frame,
            text="Select Scenario File",
            command=self.add_scenario,
            bg=self.colors["Primary"],
            fg="white",
        ).pack(pady=5)
        playlist_frame = tk.LabelFrame(
            self.window,
            text="Add Scenarios from Playlist",
            bg=self.colors["Secondary"],
            fg="white",
        )
        playlist_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Button(
            playlist_frame,
            text="Select Playlist File",
            command=self.add_playlist,
            bg=self.colors["Primary"],
            fg="white",
        ).pack(pady=5)
        scenarios_frame = tk.LabelFrame(
            self.window,
            text="Current Scenarios",
            bg=self.colors["Secondary"],
            fg="white",
        )
        scenarios_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.scenario_listbox = tk.Listbox(
            scenarios_frame,
            bg=self.colors["Background"],
            fg="white",
            selectmode=tk.MULTIPLE,
        )
        self.scenario_listbox.pack(pady=5, fill=tk.BOTH, expand=True)

        for scenario in self.clipper.scenarios:
            self.scenario_listbox.insert(tk.END, scenario)
        control_frame = tk.Frame(self.window, bg=self.colors["Background"])
        control_frame.pack(pady=5, fill=tk.X)
        control_frame = tk.Frame(self.window, bg=self.colors["Background"])
        control_frame.pack(pady=5, fill=tk.X)
        remove_button = tk.Button(
            control_frame,
            text="Remove Selected",
            command=self.remove_scenarios,
            bg=self.colors["Primary"],
            fg="white",
        )
        remove_button.grid(row=0, column=0, padx=5)
        back_button = tk.Button(
            control_frame,
            text="Back",
            command=lambda: self.terminate_process1(),
            bg=self.colors["Primary"],
            fg="white",
        )
        back_button.grid(row=0, column=1, padx=5)
        done_button = tk.Button(
            control_frame,
            text="Done",
            command=self.window.destroy,
            bg=self.colors["Primary"],
            fg="white",
        )
        done_button.grid(row=0, column=2, padx=5)
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        control_frame.grid_columnconfigure(2, weight=1)

    def add_scenario(self):
        from Kovaaks_Tool import get_scenario_directory

        scenario_path = get_scenario_directory()
        scenario = filedialog.askopenfilename(
            title="Select Scenario",
            filetypes=[("Scenario files", "*.sce")],
            initialdir=scenario_path,
        )

        if scenario:
            scenario_name = os.path.basename(scenario).replace(".sce", "")
            self.clipper.add_scenario(scenario_name)
            self.scenario_listbox.insert(tk.END, scenario_name)

    def add_playlist(self):
        from Kovaaks_Tool import create_playlist_folder

        playlist_path = create_playlist_folder()
        playlist = filedialog.askopenfilename(
            title="Select Playlist",
            filetypes=[("JSON files", "*.json")],
            initialdir=playlist_path,
        )

        if playlist:
            self.clipper.add_scenarios_from_playlist(playlist)
            self.scenario_listbox.delete(0, tk.END)

            for scenario in self.clipper.scenarios:
                self.scenario_listbox.insert(tk.END, scenario)

    def remove_scenarios(self):
        selection = self.scenario_listbox.curselection()

        for index in reversed(selection):
            scenario = self.scenario_listbox.get(index)
            self.clipper.scenarios.remove(scenario)
            self.scenario_listbox.delete(index)
        self.clipper.save_config()


class ObsWindow:
    def __init__(self, root, colors, clipper):
        self.window = tk.Toplevel(root)
        self.window.title("OBS Connection")
        self.window.configure(bg=colors["Background"])
        self.window.geometry("400x400")
        self.clipper = clipper
        self.colors = colors
        self.create_gui()

    def terminate_process1(self):
        self.clipper.stop_replay_buffer()
        if self.clipper.stop_replay_buffer():
            print("replay buffer stopped")
        terminate_process()

    def create_gui(self):
        settings_frame = tk.LabelFrame(
            self.window,
            text="OBS Connection Settings",
            bg=self.colors["Secondary"],
            fg="white",
        )
        settings_frame.pack(padx=10, pady=5, fill=tk.X)
        tk.Label(
            settings_frame, text="Host:", bg=self.colors["Secondary"], fg="white"
        ).pack(pady=2)
        self.host_entry = tk.Entry(settings_frame)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(pady=2)
        tk.Label(
            settings_frame, text="Port:", bg=self.colors["Secondary"], fg="white"
        ).pack(pady=2)
        self.port_entry = tk.Entry(settings_frame)
        self.port_entry.insert(0, "1111")
        self.port_entry.pack(pady=2)
        tk.Label(
            settings_frame, text="Password:", bg=self.colors["Secondary"], fg="white"
        ).pack(pady=2)
        self.password_entry = tk.Entry(settings_frame, show="*")
        self.password_entry.pack(pady=2)
        tk.Button(
            settings_frame,
            text="Connect",
            command=lambda: self.connect_obs(root),
            bg=self.colors["Primary"],
            fg="white",
        ).pack(pady=5, side=tk.RIGHT, padx=(80, 0))
        tk.Button(
            settings_frame,
            text="Back",
            command=main,
            bg=self.colors["Primary"],
            fg="white",
        ).pack(pady=5, side=tk.LEFT, padx=(0, 80))

    def connect_obs(self, root):
        if self.clipper.connect_obs(
            host=self.host_entry.get(),
            port=int(self.port_entry.get()),
            password=self.password_entry.get(),
        ):
            messagebox.showinfo(
                "Success", "Connected to OBS and started Replay Buffer!"
            )
            clear_window()
            self.autoclipping_stop(root)
        else:
            messagebox.showerror("Error", "Failed to connect to OBS")

    def autoclipping_stop(self, root):
        self.frame = tk.Toplevel(root)
        self.frame.title("OBS Connection")
        self.frame.geometry("190x60")
        self.frame.configure(bg=colors["Background"])
        self.clipper = clipper
        self.colors = colors
        tk.Button(
            self.frame,
            text="Stop Autoclipping &\n return to Main menu",
            bg=self.colors["Primary"],
            font=("Helvetica", 14),
            command=self.terminate_process1,
            relief="flat",
            fg="white",
        ).pack(fill="y")


def save_obs_replay(scenario, score):
    dest_dir = rf"{clip_path}\Auto_clip"
    try:
        mp4_files = [f for f in os.listdir(clip_path) if f.endswith(".mp4")]

        if not mp4_files:
            print("No .mp4 files found in the source directory.")
            return None
        latest_file = max(
            (os.path.join(clip_path, f) for f in mp4_files), key=os.path.getmtime
        )
        os.makedirs(dest_dir, exist_ok=True)
        new_file_name = f"AutoClip_{scenario}_{score}.mp4"
        dest_path = os.path.join(dest_dir, new_file_name)
        shutil.move(latest_file, dest_path)
        print(f"File renamed and moved to: {dest_path}")
        return dest_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_basic_ini_path():
    location_file = "basic_ini.txt"

    if os.path.exists(location_file):
        with open(location_file, "r") as file:
            basic_ini_path = file.read().strip()
    else:
        user = os.getlogin()
        basic_ini_path = filedialog.askopenfilename(
            title="Select basic.ini File",
            filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")],
            initialdir=os.path.expanduser(
                rf"C:/Users/{user}/AppData/Roaming/obs-studio/basic/profiles"
            ),
        )

        if basic_ini_path:
            with open(location_file, "w") as file:
                file.write(basic_ini_path)
        else:
            messagebox.showwarning(
                "No basic.ini File", "Please select a valid basic.ini file."
            )
            return None

    if os.path.exists(basic_ini_path):
        return basic_ini_path
    else:
        messagebox.showerror("Error", "Selected basic.ini file not found.")
        return None


def get_rec_file_path():
    file_path = get_basic_ini_path()

    if not file_path:
        return None
    try:
        with open(file_path, "r") as file:
            content = file.read()
        pattern = r"RecFilePath\s*=\s*(.+)"
        match = re.search(pattern, content)

        if match:
            rec_file_path = match.group(1).strip()
            return rec_file_path
        else:
            messagebox.showwarning(
                "Not Found", "RecFilePath not found in the basic.ini file."
            )
            return None

    except FileNotFoundError:
        messagebox.showerror("File Not Found", f"File not found: {file_path}")
        return None

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return None


def main():
    clear_window()

    if len(sys.argv) != 3:
        print("Usage: python Autoclipping.py <root> <colors_json>")
        sys.exit(1)
    colors = json.loads(sys.argv[2])
    clipper = AutoClipper()
    config_window = ConfigWindow(root, colors, clipper)
    config_window.window.wait_window()
    obs_window = ObsWindow(root, colors, clipper)
    obs_window.window.wait_window()
    clipper.start_monitoring()
    try:
        while True:
            root.update()
            time.sleep(0.1)

    except tk.TclError:
        clipper.stop_monitoring()
        sys.exit(0)


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def terminate_process(script_name="Autoclipping.py", root_argument="root"):
    clear_window()
    try:
        cmd_list_processes = "wmic process where \"Name like '%python.exe%' and CommandLine like '%{}%' and CommandLine like '%{}%'\" get ProcessId /value".format(
            script_name, root_argument
        )
        result = subprocess.run(
            cmd_list_processes, stdout=subprocess.PIPE, text=True, shell=True
        )
        output = result.stdout.strip()

        for line in output.splitlines():
            if "ProcessId=" in line:
                pid = line.split("=")[1].strip()
                cmd_terminate = f"taskkill /PID {pid} /F"
                subprocess.run(cmd_terminate, shell=True)
                print(
                    f"Terminated process: {script_name} with argument '{root_argument}' (PID: {pid})"
                )
                return
        print(
            f"No matching process found for {script_name} with argument '{root_argument}'."
        )

    except Exception as e:
        print(f"An error occurred: {e}")


def start_obs_if_not_running():
    if not any(proc.name() == "obs64.exe" for proc in psutil.process_iter()):
        print("Starting OBS...")
        subprocess.Popen(
            r"C:\Program Files\obs-studio\bin\64bit\obs64.exe",
            cwd=os.path.dirname(r"C:\Program Files\obs-studio\bin\64bit\obs64.exe"),
        )
        time.sleep(5)
    else:
        print("OBS is already open")


def get_websocket_config():
    ini_file_path = get_basic_ini_path()
    base_dir = os.path.join(
        os.path.dirname(ini_file_path).split("basic")[0],
        "plugin_config",
        "obs-websocket",
    )
    config_json_path = os.path.join(base_dir, "config.json")
    return config_json_path


def edit_websocket_config():
    flag_path = "Config.flag"
    try:
        config_path = get_websocket_config()

        if not os.path.exists("custom_config.json"):
            with open(config_path, "w") as file:
                file.write("")
        else:
            with open("custom_config.json", "r") as file:
                config = json.load(file)

            with open(config_path, "w") as file:
                json.dump(config, file)
            print(f"WebSocket port updated to {config} in {config_path}")

            if any(proc.name() == "obs64.exe" for proc in psutil.process_iter()):
                messagebox.showerror(
                    "Restart OBS",
                    "Please restart OBS to use the Auto Clipping function!",
                )
            else:
                with open(flag_path, "w") as flag_file:
                    flag_file.write(f"Config edited: server_port={config}\n")

    except FileNotFoundError as e:
        print(f"Error: {e}")

    except json.JSONDecodeError:
        print("Error: Failed to parse the WebSocket configuration file.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    stats_dir = r"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats"
    parsed_stats_dir = os.path.join(stats_dir, "parsed_scens")
    score_tracker = ScoreTracker(stats_dir, parsed_stats_dir)
    start_obs_if_not_running()
    user = getpass.getuser()
    clip_path = get_rec_file_path()

    if not os.path.exists("Config.flag"):
        edit_websocket_config()

    class StatsEventHandler(FileSystemEventHandler):
        def __init__(self, score_tracker):
            self.score_tracker = score_tracker
            super().__init__()

        def on_created(self, event):
            if event.is_directory or not event.src_path.endswith(".csv"):
                return
            time.sleep(0.1)
            self.score_tracker.process_new_score_file(event.src_path)

        def on_modified(self, event):
            if event.is_directory or not event.src_path.endswith(".csv"):
                return
            time.sleep(0.1)
            self.score_tracker.process_new_score_file(event.src_path)

    observer = Observer()
    event_handler = StatsEventHandler(score_tracker)
    observer.schedule(event_handler, stats_dir, recursive=False)
    observer.start()
    print("here")

    for file_name in os.listdir(stats_dir):
        if (
            file_name.endswith(".csv")
            and file_name not in score_tracker.processed_files
        ):
            file_path = os.path.join(stats_dir, file_name)
            score_tracker.process_new_score_file(file_path)
            score_tracker.log_processed_file(file_name)
            print("here2")
    try:
        print("here3")

        if len(sys.argv) == 3:
            colors = json.loads(sys.argv[2])
            clipper = AutoClipper()
            config_window = ConfigWindow(root, colors, clipper)
            config_window.window.wait_window()
            obs_window = ObsWindow(root, colors, clipper)
            obs_window.window.wait_window()
            clipper.start_monitoring()
            root.mainloop()
            while True:
                root.update()
                time.sleep(0.1)
        else:
            while True:
                time.sleep(1)

    except (KeyboardInterrupt, SystemExit, tk.TclError):
        observer.stop()

        if "clipper" in locals():
            clipper.stop_monitoring()
    finally:
        observer.join()
        sys.exit(0)
