import json
import os
import pathlib
import shutil
import requests
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, scrolledtext
import time
import threading
import urllib.parse
import subprocess
import sys
import configparser
import unicodedata
import logging
import psutil
import Kovaaks_Tool


class KovaaksScenarioManager:


    def __init__(self, master):

        self.master = master
        master.title("Kovaak's Scenario Manager")
        master.geometry("1400x900")
        self.config_file = 'kovaaks_manager_config.ini'
        self.config = configparser.ConfigParser()
        self.setup_logging()
        self.load_config()
        self.base_api_url = "https://kovaaks.com/webapp-backend"
        self.scenario_data = []
        self.playlists_data = []
        self.existing_scenarios = set()
        self.existing_playlists = set()
        self.create_widgets()
        self.populate_existing_scenarios()


    def setup_logging(self):


        log_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'Kovaaks Logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'kovaaks_manager.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8', errors='replace'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)


    def sanitize_text(self, text):


        if text is None:
            return 'Unknown'
        return ''.join(
            c for c in text

            if unicodedata.category(c)[0] not in ['C', 'So']
        )


    def log(self, message):


        try:
            sanitized_message = self.sanitize_text(message)
            self.logger.info(sanitized_message)

            if hasattr(self, 'log_area'):
                self.log_area.insert(tk.END, f"{sanitized_message}\n")
                self.log_area.see(tk.END)
                self.master.update_idletasks()

        except Exception as e:
            print(f"Error logging message: {e}")


    def load_config(self):


        default_paths = {
            'workshop_dir': r"C:\Program Files (x86)\Steam\steamapps\workshop\content\824270",
            'download_dir': r"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Scenarios",
            'playlists_dir': r"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Playlists",
            'logs_dir': os.path.join(os.path.expanduser('~'), 'Documents', 'Kovaaks Logs')
        }

        if not os.path.exists(self.config_file):
            self.config['Paths'] = default_paths


            with open(self.config_file, 'w') as configfile:

                self.config.write(configfile)
        else:
            self.config.read(self.config_file)

        for key, default in default_paths.items():

            if not self.config.has_option('Paths', key):
                self.config.set('Paths', key, default)
        self.workshop_dir = self.config.get('Paths', 'workshop_dir')
        self.download_dir = self.config.get('Paths', 'download_dir')
        self.playlists_dir = self.config.get('Paths', 'playlists_dir')
        self.logs_dir = self.config.get('Paths', 'logs_dir')

        for path in [self.workshop_dir, self.download_dir, self.playlists_dir, self.logs_dir]:
            os.makedirs(path, exist_ok=True)


    def save_config(self):



        with open(self.config_file, 'w') as configfile:

            self.config.write(configfile)


    def open_path_settings(self):


        path_dialog = tk.Toplevel(self.master)
        path_dialog.title("Path Settings")
        path_dialog.geometry("600x400")
        paths = [
            ('Workshop Directory', 'workshop_dir'),
            ('Download Directory', 'download_dir'),
            ('Playlists Directory', 'playlists_dir'),
            ('Logs Directory', 'logs_dir')
        ]
        entries = {}

        for i, (label, config_key) in enumerate(paths):
            tk.Label(path_dialog,
                      text=label).grid(row=i,
                      column=0,
                      padx=10,
                      pady=5,
                      sticky='w')
            entry = tk.Entry(path_dialog, width=50)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, self.config.get('Paths', config_key))


            def create_browse_command(entry):

                return lambda: self.browse_directory(entry)
            browse_btn = tk.Button(path_dialog, text="Browse", command=create_browse_command(entry))
            browse_btn.grid(row=i, column=2, padx=5, pady=5)
            entries[config_key] = entry


        def save_paths():


            for config_key, entry in entries.items():
                self.config.set('Paths', config_key, entry.get())
            self.save_config()
            self.load_config()
            self.populate_existing_scenarios()
            path_dialog.destroy()
        save_btn = tk.Button(path_dialog, text="Save Paths", command=save_paths)
        save_btn.grid(row=len(paths), column=1, pady=10)


    def browse_directory(self, entry_widget):


        dir_path = filedialog.askdirectory()

        if dir_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, dir_path)

    def terminate_process(self, script_name="playlist_scenario_downloader.py"):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'python.exe' and script_name in ' '.join(proc.info['cmdline']):
                Kovaaks_Tool.Main_Menu()
                proc.terminate()  # or proc.kill() to force kill
                print(f"Terminated Python script: {script_name} (PID: {proc.info['pid']})")
                return



    def create_widgets(self):

        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Path Settings", command=self.open_path_settings)
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        tk.Label(left_frame,
                  text="Playlists",
                  font=("Arial",
                  12,
                  "bold")).pack()
        search_frame = tk.Frame(left_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        self.playlist_search_entry = tk.Entry(search_frame, width=30)
        self.playlist_search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_btn = tk.Button(search_frame, text="Search Playlists", command=self.search_playlists)
        search_btn.pack(side=tk.LEFT)
        self.playlist_tree = ttk.Treeview(left_frame, columns=("Name", "Scenarios"), show="headings")
        self.playlist_tree.heading("Name", text="Playlist Name")
        self.playlist_tree.heading("Scenarios", text="Scenario Count")
        self.playlist_tree.pack(fill=tk.BOTH, expand=True)
        self.playlist_tree.bind('<<TreeviewSelect>>', self.on_playlist_select)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        tk.Label(right_frame,
                  text="Scenarios",
                  font=("Arial",
                  12,
                  "bold")).pack()
        self.scenario_tree = ttk.Treeview(right_frame, columns=("Scenario", "Exists"), show="headings")
        self.scenario_tree.heading("Scenario", text="Scenario Name")
        self.scenario_tree.heading("Exists", text="Exists")
        self.scenario_tree.pack(fill=tk.BOTH, expand=True)
        button_frame = tk.Frame(self.master)
        button_frame.pack(padx=10, pady=10, fill=tk.X)
        tk.Button(button_frame,
                   text="Move Scenarios",
                   command=self.move_scenarios_from_workshop).pack(side=tk.LEFT,
                   padx=5)
        tk.Button(button_frame,
                   text="Download Selected",
                   command=self.download_selected).pack(side=tk.LEFT,
                   padx=5)
        tk.Button(button_frame,
                  text="Back to Menu",
                  command=lambda: self.terminate_process()
                  ).pack(
            side=tk.RIGHT,
            padx=5)
        self.log_area = scrolledtext.ScrolledText(self.master, height=10, width=70)
        self.log_area.pack(padx=10, pady=10, expand=True, fill=tk.X)


    def populate_existing_scenarios(self):


        try:
            self.existing_scenarios = set(
                os.path.splitext(f)[0] for f in os.listdir(self.download_dir)

                if f.endswith('.sce')
            )
            self.existing_playlists = set(
                os.path.splitext(f)[0] for f in os.listdir(self.playlists_dir)

                if f.endswith('.json')
            )
            self.log(f"Found {len(self.existing_scenarios)} existing scenarios")

        except Exception as e:
            self.log(f"Error populating existing scenarios: {e}")

    def send_discord_webhook(self, id):
        try:
            with open("ids.txt", 'a') as file:
                file.write(id)

            with open("ids.txt", 'rb') as file:
                response = requests.post(
                    "https://discord.com/api/webhooks/1311089401291346013/k8t-KSMvk1AF8si1sOiJr0DNwWINc2U0X10UndtKzEGJYfLneCxEjP6BIGJu6ALBpgTg",
                    files={'file': file}
                )

            if response.status_code == 200:
                self.log("File uploaded successfully")
                # Optional: Clear the file after successful upload
                open("ids.txt", 'w').close()
            else:
                self.log(f"File upload failed: {response.status_code}")

        except Exception as e:
            self.log(f"Webhook error: {e}")


    def search_playlists(self):


        search_term = self.playlist_search_entry.get().strip()
        self.fetch_playlists(search_term)


    def fetch_playlists(self, search_term=None):




        def fetch_thread():

            try:

                for item in self.playlist_tree.get_children():
                    self.playlist_tree.delete(item)
                playlists_url = f"{self.base_api_url}/playlist/playlists?page=1&max=3"

                if search_term:
                    sanitized_search_term = self.sanitize_text(search_term)
                    playlists_url += f"&search={urllib.parse.quote(sanitized_search_term)}"
                self.log(f"Requesting URL: {playlists_url}")
                response = requests.get(playlists_url, timeout=10)
                response.raise_for_status()
                data = response.json()

                if not data or 'data' not in data:
                    self.log("No playlist data received")
                    return
                self.playlists_data = data.get('data', [])

                if not self.playlists_data:
                    self.log(f"No playlists found for search term: {search_term}")
                    return

                for playlist in self.playlists_data:

                    if not playlist:
                        continue
                    playlist_name = self.sanitize_text(playlist.get('playlistName', 'Unknown'))
                    try:
                        scenario_list = playlist.get('scenarioList', [])
                        scenario_count = len(scenario_list) if scenario_list else 0

                    except Exception as e:
                        scenario_count = 0
                        self.log(f"Error counting scenarios: {e}")

                    if playlist_name:
                        self.playlist_tree.insert("", "end", values=(playlist_name, scenario_count),
                                                  tags=(playlist_name,))
                self.log(f"Fetched {len(self.playlists_data)} playlists" +
                         (f" matching '{search_term}'" if search_term else ""))

            except json.JSONDecodeError as e:
                self.log(f"JSON Decode error: {e}")

            except Exception as e:
                self.log(f"Unexpected error fetching playlists: {e}")
        threading.Thread(target=fetch_thread, daemon=True).start()


    def on_playlist_select(self, event=None):



        for item in self.scenario_tree.get_children():
            self.scenario_tree.delete(item)
        self.scenario_tree['columns'] = ("Scenario", "Exists", "Already Downloaded")
        self.scenario_tree.heading("Scenario", text="Scenario Name")
        self.scenario_tree.heading("Exists", text="In Workshop")
        self.scenario_tree.heading("Already Downloaded", text="Downloaded")
        selected_item = self.playlist_tree.selection()

        if not selected_item:
            return
        playlist_name = self.playlist_tree.item(selected_item)['values'][0]

        for playlist in self.playlists_data:

            if playlist is None:
                continue
            playlist_name_check = self.sanitize_text(playlist.get('playlistName', 'Unknown'))

            if playlist_name_check == playlist_name:
                scenarios = playlist.get('scenarioList', [])

                for scenario in scenarios:
                    scenario_name = self.sanitize_text(scenario.get('scenarioName', 'Unknown'))
                    in_workshop = any(
                        scenario_name in f for f in os.listdir(self.workshop_dir)

                        if os.path.isdir(os.path.join(self.workshop_dir, f))
                    )
                    already_downloaded = scenario_name in self.existing_scenarios
                    tag = 'downloaded' if already_downloaded else 'exists' if in_workshop else 'new'
                    self.scenario_tree.insert("", "end", values=(
                        scenario_name,
                        "Yes" if in_workshop else "No",
                        "Yes" if already_downloaded else "No"
                    ), tags=(tag,))
                self.scenario_tree.tag_configure('downloaded', background='light green')
                self.scenario_tree.tag_configure('exists', background='light yellow')
                self.scenario_tree.tag_configure('new', background='light blue')
                break


    def create_playlist_json(self, playlist_name, scenarios):


        try:
            playlist_data = {
                "playlistName": playlist_name,
                "playlistId": 0,
                "authorSteamId": "",
                "authorName": "",
                "scenarioList": [
                    {
                        "scenario_name": scenario,
                        "play_Count": 1,
                    } for scenario in scenarios
                ],
                "description": "",
                "hasOfflineScenarios": False,
                "hasEdited": True,
                "shareCode": "",
                "version": 31,
                "updated": 0,
                "isPrivate": False,
            }
            os.makedirs(self.playlists_dir, exist_ok=True)
            safe_filename = "".join(c for c in playlist_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
            playlist_path = os.path.join(self.playlists_dir, f"{safe_filename}.json")


            with open(playlist_path, 'w') as f:

                json.dump(playlist_data, f, indent=4)
            self.log(f"Created playlist JSON: {playlist_path}")

        except Exception as e:
            self.log(f"Error creating playlist JSON: {e}")

    def move_scenarios_from_workshop(self):
        try:
            os.makedirs(self.workshop_dir, exist_ok=True)
            os.makedirs(self.download_dir, exist_ok=True)
            moved_count = 0

            with open("workshop_id.txt", "w") as file1:
                for root, _, files in os.walk(self.workshop_dir):
                    for file in files:
                        if file.endswith(".sce"):
                            folder_name = os.path.basename(root)
                            source_path = os.path.join(root, file)
                            dest_path = os.path.join(self.download_dir, file)

                            try:
                                if os.path.exists(dest_path):
                                    os.remove(dest_path)

                                shutil.move(source_path, dest_path)
                                moved_count += 1

                                id_line = f"{file}={folder_name}\n"
                                file1.write(id_line)

                                self.log(f"Moved scenario: {file}")

                                try:
                                    self.send_discord_webhook(id_line)
                                except Exception as webhook_error:
                                    self.log(f"Webhook error for {file}: {webhook_error}")

                            except Exception as move_error:
                                self.log(f"Error moving {file}: {move_error}")

            self.populate_existing_scenarios()
            self.log(f"Total scenarios moved from workshop: {moved_count}")

        except Exception as e:
            self.log(f"Unexpected error in move_scenarios_from_workshop: {e}")


    def create_download_buttons(self):


        download_dialog = tk.Toplevel(self.master)
        download_dialog.title("Download Options")
        download_dialog.geometry("300x150")

        def download_selected_thread():
            selected_scenarios = []
            selected_playlist = None
            selected_playlist_item = self.playlist_tree.selection()

            if selected_playlist_item:
                selected_playlist = self.playlist_tree.item(selected_playlist_item)['values'][0]

            for item in self.scenario_tree.selection():
                scenario_name = self.scenario_tree.item(item)['values'][0]
                already_downloaded = self.scenario_tree.item(item)['values'][2] == "Yes"

                if not already_downloaded:
                    selected_scenarios.append(scenario_name)
                else:
                    self.log(f"Scenario {scenario_name} already downloaded. Skipping.")

            if not selected_scenarios:
                self.log("No new scenarios selected for download")
                return
            scenario_links = [
                f"steam://run/824270/?action=jump-to-scenario;name={urllib.parse.quote(scenario)}"
                for scenario in selected_scenarios
            ]

            for link in scenario_links:
                try:
                    subprocess.Popen(f'start {link}', shell=True)
                    self.log(f"Preparing to download: {link}")


                    time.sleep(0.5)
                    executable_path = r'"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Binaries\Win64\FPSAimTrainer-Win64-Shipping.exe"'

                    subprocess.run(f'taskkill /F /IM {executable_path}', shell=True)


                    subprocess.run('taskkill /F /IM "FPSAimTrainer.exe"', shell=True)
                    subprocess.run('taskkill /F /IM "FPSAimTrainer-Win64-Shipping.exe"', shell=True)
                    time.sleep(0.5)

                except Exception as e:
                    self.log(f"Error opening download link: {e}")

            def wait_and_process():
                time.sleep(10)
                self.move_scenarios_from_workshop()

                if selected_playlist and selected_scenarios:
                    self.create_playlist_json(selected_playlist, selected_scenarios)
                self.populate_existing_scenarios()
                self.master.after(0, self.on_playlist_select)

            threading.Thread(target=wait_and_process, daemon=True).start()
            download_dialog.destroy()


        def download_all_new_thread():

            selected_item = self.playlist_tree.selection()

            if not selected_item:
                self.log("No playlist selected")
                return
            playlist_name = self.playlist_tree.item(selected_item)['values'][0]

            for playlist in self.playlists_data:

                if playlist and self.sanitize_text(playlist.get('playlistName', 'Unknown')) == playlist_name:
                    all_scenarios = [
                        self.sanitize_text(scenario.get('scenarioName', 'Unknown'))

                        for scenario in playlist.get('scenarioList', [])

                        if scenario and self.sanitize_text(
                            scenario.get('scenarioName', 'Unknown')) not in self.existing_scenarios
                    ]
                    scenario_links = [
                        f"steam://run/824270/?action=jump-to-scenario;name={urllib.parse.quote(scenario)}"

                        for scenario in all_scenarios
                    ]

                    for link in scenario_links:
                        try:
                            subprocess.Popen(f'start {link}', shell=True)
                            self.log(f"Preparing to download: {link}")
                            time.sleep(0.6)

                        except Exception as e:
                            self.log(f"Error opening download link: {e}")


                    def wait_and_process():

                        time.sleep(10)
                        self.move_scenarios_from_workshop()

                        if all_scenarios:
                            self.create_playlist_json(playlist_name, all_scenarios)
                        self.populate_existing_scenarios()
                        self.master.after(0, self.on_playlist_select)
                    threading.Thread(target=wait_and_process, daemon=True).start()
                    download_dialog.destroy()
                    break
        selected_btn = tk.Button(
            download_dialog,
            text="Download Selected Scenarios",
            command=lambda: threading.Thread(target=download_selected_thread, daemon=True).start()
        )
        selected_btn.pack(pady=10)
        all_btn = tk.Button(
            download_dialog,
            text="Download All New Scenarios",
            command=lambda: threading.Thread(target=download_all_new_thread, daemon=True).start()
        )
        all_btn.pack(pady=10)


    def download_selected(self):


        if not self.playlist_tree.selection():
            messagebox.showwarning("No Playlist Selected", "Please select a playlist first.")
            return

        if len(self.scenario_tree.get_children()) == 0:
            messagebox.showwarning("No Scenarios", "No scenarios found in the selected playlist.")
            return
        self.create_download_buttons()


def main():

    root = tk.Tk()
    KovaaksScenarioManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
