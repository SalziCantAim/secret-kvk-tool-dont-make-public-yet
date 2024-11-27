import time
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import re
import subprocess
import os
import json
import getpass
import Autoclipping

DEFAULT_BACKGROUND_COLOR = "#36323b"
DEFAULT_PRIMARY_COLOR = "#ff5722"
DEFAULT_SECONDARY_COLOR = "#4e4a54"
TEXT_COLOR = "white"
user = getpass.getuser()
colors = {
    "Background": DEFAULT_BACKGROUND_COLOR,
    "Primary": DEFAULT_PRIMARY_COLOR,
    "Secondary": DEFAULT_SECONDARY_COLOR,
}


def ask_palette_choice():
    def use_custom_palette():
        choice_window.destroy()
        get_palette_directory(use_default=False)

    def use_default_palette():
        choice_window.destroy()
        get_palette_directory(use_default=True)

    choice_window = tk.Tk()
    choice_window.title("Palette Choice")
    choice_window.geometry("400x200")
    choice_window.configure(bg=DEFAULT_BACKGROUND_COLOR)
    label = tk.Label(
        choice_window,
        text="Do you want to use your own Palette Colors,\nor do you want to use the Default ones?",
        bg=DEFAULT_BACKGROUND_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14),
        wraplength=350,
        justify="center",
    )
    label.pack(pady=20)
    custom_button = tk.Button(
        choice_window,
        text="My Own",
        bg=DEFAULT_PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12),
        relief="flat",
        command=use_custom_palette,
    )
    custom_button.pack(pady=5)
    default_button = tk.Button(
        choice_window,
        text="Default",
        bg=DEFAULT_SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12),
        relief="flat",
        command=use_default_palette,
    )
    default_button.pack(pady=5)
    choice_window.mainloop()


def get_palette_directory(use_default):
    global colors
    location_file = "palette_file_location.txt"

    if use_default:
        messagebox.showinfo("Default Palette", "Using default palette colors.")

        with open(location_file, "w") as file:
            file.write("")

        return
    location_file = "palette_file_location.txt"

    if os.path.exists(location_file):
        with open(location_file, "r") as file:
            palette_file_path = file.read().strip()
    else:
        palette_file_path = filedialog.askopenfilename(
            title="Select Palette.ini File",
            filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")],
            initialdir=os.path.expanduser(
                f"C:/Users/{user}/AppData/Local/FPSAimTrainer/Saved/Config/WindowsNoEditor"
            ),
        )

        if palette_file_path:
            with open(location_file, "w") as file:
                file.write(palette_file_path)
        else:
            messagebox.showwarning(
                "No Palette File", "Please select a valid Palette.ini file."
            )
            return

    if os.path.exists(palette_file_path):
        colors = extract_palette_colors(palette_file_path)
    else:
        messagebox.showerror("Error", "Selected Palette.ini file not found.")


def extract_palette_colors(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    pattern = (
        r"\((?P<name>[^,]+), \(\s*B=(?P<B>\d+),G=(?P<G>\d+),R=(?P<R>\d+),A=\d+\)\)"
    )
    matches = re.finditer(pattern, content)
    extracted_colors = {}

    for match in matches:
        name = match.group("name").strip()
        B = int(match.group("B"))
        G = int(match.group("G"))
        R = int(match.group("R"))
        extracted_colors[name] = f"#{R:02x}{G:02x}{B:02x}"
    return extracted_colors


BACKGROUND_COLOR = colors.get("Background", DEFAULT_BACKGROUND_COLOR)
PRIMARY_COLOR = colors.get("Primary", DEFAULT_PRIMARY_COLOR)
SECONDARY_COLOR = colors.get("Secondary", DEFAULT_SECONDARY_COLOR)


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


character_profiles = []
background_color = colors.get("Background", "#222222")
primary_color = colors.get("Primary", "#ff5722")
secondary_color = colors.get("Secondary", "#555555")
BACKGROUND_COLOR = background_color
PRIMARY_COLOR = primary_color
SECONDARY_COLOR = secondary_color
TEXT_COLOR = "white"
header_color = "#1b191f"


def Main_Menu():
    root.title("Kovaak's Menu")
    root.geometry("1200x1000")
    root.configure(bg=BACKGROUND_COLOR)

    def open_profile_changer():
        clear_window()
        try:
            Profile_Changer()

        except FileNotFoundError:
            messagebox.showerror(
                "Error", "Profile Changer.py not found in the current directory."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Profile Changer.py.\n{e}")

    def on_button_click(action):
        if action == "Edit Scenario":
            open_profile_changer()

        elif action == "Create Playlist":
            create_playlist()

        elif action == "Auto Clipper":
            AutoClipperGUI(colors)

        elif action == "Find Playlists":
            subprocess.run(["python", "playlist_scenario_downloader.py"], check=True)

        elif action == "Change Playlist folder":
            change_playlist_folder()

        elif action == "Change Scenario folder":
            change_scenario_folder()

        elif action == "Change Palette folder":
            ask_palette_choice()

    try:
        logo_path = "assets/kovaak_image.jpg"
        img = Image.open(logo_path)
        root.logo_image = ImageTk.PhotoImage(img)
        logo_label = tk.Label(root, image=root.logo_image, bg=BACKGROUND_COLOR)
        logo_label.pack(pady=20)

    except Exception as e:
        print(f"Error loading image: {e}")
        fallback_label = tk.Label(
            root,
            text="Kovaak's Menu",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 24, "bold"),
        )
        fallback_label.pack(pady=20)
    button_style = {
        "width": 30,
        "height": 2,
        "bg": primary_color,
        "fg": "white",
        "font": ("Arial", 14),
        "relief": "flat",
        "bd": 0,
    }
    buttons = [
        ("Edit Scenario", "Edit Scenario"),
        ("Create Playlist", "Create Playlist"),
        ("Find Playlists", "Find Playlists"),
        ("Download Scenarios", "Download Scenarios"),
        ("Change Scenario folder", "Change Scenario folder"),
        ("Change Playlist folder", "Change Playlist folder"),
        ("Change Palette folder", "Change Palette folder"),
        ("Auto Clipper", "Auto Clipper"),
    ]
    frame = tk.Frame(root, bg=background_color)
    frame.pack(pady=50)

    for button_text, action in buttons:
        button = tk.Button(
            frame,
            text=button_text,
            command=lambda a=action: on_button_click(a),
            **button_style,
        )
        button.pack(pady=10)
    root.mainloop()


def change_playlist_folder():
    location_file = "playlist_folder_location.txt"
    Folder_directory = create_playlist_folder()

    with open(location_file, "r") as file:
        Folder_directory = file.read().strip()
    Folder_directory = filedialog.askdirectory(title="Select Playlist Folder")

    if Folder_directory:
        with open(location_file, "w") as file:
            file.write(Folder_directory)
        clear_window()
        Main_Menu()
    else:
        messagebox.showwarning("No Playlists", "Please select a valid Playlist folder.")
        clear_window()
        Main_Menu()
        return None
    return Folder_directory


def create_playlist_folder():
    location_file = "playlist_folder_location.txt"

    if os.path.exists(location_file):
        with open(location_file, "r") as file:
            Folder_directory = file.read().strip()
    else:
        Folder_directory = filedialog.askdirectory(title="Select Playlist Folder")

        if Folder_directory:
            with open(location_file, "w") as file:
                file.write(Folder_directory)
            Main_Menu()
        else:
            messagebox.showwarning(
                "No Playlists", "Please select a valid Playlist folder."
            )
            get_scenario_directory()
            return None
    return Folder_directory


def change_scenario_folder():
    location_file = "Scenario_folder_location.txt"
    Folder_directory = get_scenario_directory()

    with open(location_file, "r") as file:
        Folder_directory = file.read().strip()
    Folder_directory = filedialog.askdirectory(title="Select Scenario Folder")

    if Folder_directory:
        with open(location_file, "w") as file:
            file.write(Folder_directory)
        clear_window()
        Main_Menu()
    else:
        messagebox.showwarning(
            "No Scenarios", "Please select a valid Scenarios folder."
        )
        clear_window()
        Main_Menu()
        return None
    return Folder_directory


def get_scenario_directory():
    location_file = "Scenario_folder_location.txt"

    if os.path.exists(location_file):
        with open(location_file, "r") as file:
            Folder_directory = file.read().strip()
    else:
        Folder_directory = filedialog.askdirectory(title="Select Scenario Folder")

        if Folder_directory:
            with open(location_file, "w") as file:
                file.write(Folder_directory)
            Main_Menu()
        else:
            messagebox.showwarning(
                "No scenarios", "Please select a valid Scenario folder."
            )
            get_scenario_directory()
            return None
    return Folder_directory


def AutoClipperGUI(colors):
    try:
        subprocess.run(
            ["python", "Autoclipping.py", "root", json.dumps(colors)], check=True
        )

    except subprocess.CalledProcessError:
        pass


def Profile_Changer():
    BACKGROUND_COLOR = background_color
    PRIMARY_COLOR = primary_color
    SECONDARY_COLOR = secondary_color
    TEXT_COLOR = "white"
    SCENARIO_DIR = get_scenario_directory()
    print(SCENARIO_DIR)

    def open_main_Menu():
        clear_window()
        try:
            Main_Menu()

        except FileNotFoundError:
            messagebox.showerror(
                "Error", "Profile Changer.py not found in the current directory."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Profile Changer.py.\n{e}")

    from tkinter import ttk

    def open_Profile_Changer(scenario):
        print(scenario)
        subprocess.run(
            ["python", "ProfileChangeHandlerTest.py", main_menu, scenario], check=True
        )

    def list_scenarios():
        headline = tk.Label(
            editor_frame,
            text="Choose a Scenario",
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            pady=10,
        )
        headline.pack(anchor="n", pady=10)
        search_frame = tk.Frame(editor_frame, bg=SECONDARY_COLOR)
        search_frame.pack(anchor="nw", padx=10, pady=12)
        search_label = tk.Label(
            search_frame,
            text="Search:",
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 12, "bold"),
        )
        search_label.pack(side="left", padx=5)
        search_entry = tk.Entry(
            search_frame,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 18),
            relief="flat",
            width=20,
        )
        search_entry.pack(side="left", padx=5)
        canvas = tk.Canvas(editor_frame, bg=SECONDARY_COLOR, highlightthickness=0)
        style = ttk.Style()
        style.configure(
            "Custom.Vertical.TScrollbar",
            background=BACKGROUND_COLOR,
            troughcolor=SECONDARY_COLOR,
            bordercolor=SECONDARY_COLOR,
            arrowcolor=TEXT_COLOR,
            relief="flat",
        )
        style.map(
            "Custom.Vertical.TScrollbar",
            background=[("active", BACKGROUND_COLOR)],
            troughcolor=[("pressed", PRIMARY_COLOR)],
        )
        scrollbar = ttk.Scrollbar(
            editor_frame,
            orient="vertical",
            command=canvas.yview,
            style="Custom.Vertical.TScrollbar",
        )
        scrollable_frame = tk.Frame(canvas, bg=SECONDARY_COLOR)
        canvas_window = canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="n"
        )
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        fixed_width = 600
        scrollable_frame.config(width=fixed_width)
        fixed_width_back = 65
        root.config(width=fixed_width_back)

        def center_canvas_content(event):
            canvas_width = canvas.winfo_width()
            x_offset = max((canvas_width - fixed_width) // 2, 0)
            canvas.coords(canvas_window, x_offset + fixed_width_back, 0)

        canvas.bind("<Configure>", center_canvas_content)

        def on_mouse_wheel(event):
            """Handle mouse wheel scroll."""
            canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))
        all_scenario_files = [f for f in os.listdir(SCENARIO_DIR) if f.endswith(".sce")]

        def update_scenario_list(search_text=""):
            """Update the scenario list based on the search text."""

            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            filtered_files = [
                f for f in all_scenario_files if search_text.lower() in f.lower()
            ]

            for index, scenario in enumerate(filtered_files):
                bg_color = BACKGROUND_COLOR if index % 2 == 0 else SECONDARY_COLOR
                scenario_frame = tk.Frame(scrollable_frame, bg="white", padx=0, pady=0)
                scenario_frame.pack(fill="x", padx=0, pady=2)
                button = tk.Button(
                    scenario_frame,
                    text=scenario,
                    bg=bg_color,
                    fg=TEXT_COLOR,
                    font=("Helvetica", 12, "bold"),
                    command=lambda s=scenario: open_Profile_Changer(s),
                    relief="flat",
                )
                button.pack(fill="x")

        search_entry.bind(
            "<KeyRelease>", lambda event: update_scenario_list(search_entry.get())
        )
        update_scenario_list()
        back_button = tk.Button(
            root,
            text="Back",
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            relief="flat",
            command=open_main_Menu,
        )
        back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    root.configure(bg=SECONDARY_COLOR)
    editor_frame = tk.Frame(root, padx=10, pady=10, bg=SECONDARY_COLOR)
    editor_frame.pack(fill="both", expand=True)
    list_scenarios()


FONT_STYLE = ("Helvetica", 12, "bold")


def create_playlist():
    clear_window()

    def get_scenario_directory():
        location_file = "Scenario_Folder_location.txt"

        if os.path.exists(location_file):
            with open(location_file, "r") as file:
                scenario_directory = file.read().strip()
        else:
            scenario_directory = filedialog.askdirectory(title="Select Scenario Folder")

            if scenario_directory:
                with open(location_file, "w") as file:
                    file.write(scenario_directory)
            else:
                messagebox.showwarning(
                    "No Folder Selected", "Please select a valid scenario folder."
                )
                return None
        return scenario_directory

    def get_Playlist_directory():
        location_file = "playlist_folder_location.txt"

        if os.path.exists(location_file):
            with open(location_file, "r") as file:
                Folder_directory = file.read().strip()
        else:
            Folder_directory = filedialog.askdirectory(title="Select Playlist Folder")

            if Folder_directory:
                with open(location_file, "w") as file:
                    file.write(Folder_directory)
            else:
                messagebox.showwarning(
                    "No Playlist", "Please select a valid Playlist folder."
                )
                return None
        return Folder_directory

    selected_scenarios = {}
    filtered_scenarios = []

    def update_chosen_list(frame):
        for widget in frame.winfo_children():
            widget.destroy()
        row = 0

        for scenario, details in selected_scenarios.items():
            play_count_str = f"{details['play_Count']}/{details['play_Count']}"
            row_color_flag = row % 2 == 0
            bg_color = BACKGROUND_COLOR if row_color_flag else SECONDARY_COLOR
            row_frame = tk.Frame(frame, bg=BACKGROUND_COLOR, highlightthickness=0)
            row_frame.grid(row=row, column=0, pady=5, sticky="w")
            play_count_label = tk.Label(
                row_frame,
                text=play_count_str,
                font=("Helvetica", 10, "bold"),
                bg=BACKGROUND_COLOR,
                fg=TEXT_COLOR,
            )
            play_count_label.pack(side=tk.LEFT, padx=(5, 10))
            button_frame = tk.Frame(
                row_frame, bg="white", highlightbackground="black", highlightthickness=1
            )
            button_frame.pack(side=tk.LEFT, fill="x", expand=True)
            button = tk.Button(
                button_frame,
                text=scenario,
                command=lambda s=scenario: remove_from_playlist(s, frame),
                font=("Helvetica", 10, "bold"),
                width=40,
                bg=bg_color,
                fg=TEXT_COLOR,
                activebackground=bg_color,
                relief="flat",
            )
            button.pack(fill="x", expand=True, padx=1, pady=1)
            row += 1

    def remove_from_playlist(scenario_name, frame):
        if scenario_name in selected_scenarios:
            selected_scenarios[scenario_name]["play_Count"] -= 1

            if selected_scenarios[scenario_name]["play_Count"] == 0:
                del selected_scenarios[scenario_name]
        update_chosen_list(frame)

    def add_to_playlist(scenario_name, chosen_frame):
        if scenario_name in selected_scenarios:
            selected_scenarios[scenario_name]["play_Count"] += 1
        else:
            selected_scenarios[scenario_name] = {
                "scenario_name": scenario_name,
                "play_Count": 1,
            }
        update_chosen_list(chosen_frame)

    def search_scenarios(entry, canvas, frame, scenarios, chosen_frame):
        search_term = entry.get().lower()
        global filtered_scenarios
        filtered_scenarios = [
            scenario for scenario in scenarios if search_term in scenario.lower()
        ]
        populate_scenario_buttons(canvas, frame, filtered_scenarios, chosen_frame)

    def populate_scenario_buttons(canvas, frame, scenarios, chosen_frame):
        for widget in frame.winfo_children():
            widget.destroy()
        row, col = 0, 0

        for index, scenario in enumerate(scenarios):
            scenario = scenario[:-4]
            row_color_flag = row % 2 == 0
            bg_color = BACKGROUND_COLOR if row_color_flag else SECONDARY_COLOR
            button_frame = tk.Frame(
                frame, bg="white", highlightbackground="black", highlightthickness=1
            )
            button_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            button = tk.Button(
                button_frame,
                text=scenario,
                command=lambda s=scenario: add_to_playlist(s, chosen_frame),
                font=("Helvetica", 11, "bold"),
                width=40,
                bg=bg_color,
                fg=TEXT_COLOR,
                activebackground=bg_color,
                relief="flat",
            )
            button.pack(fill="both", expand=True, padx=1, pady=1)
            col += 1

            if col == 2:
                col = 0
                row += 1
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def go_back():
        clear_window()

    def open_main_Menu():
        clear_window()
        try:
            Main_Menu()

        except FileNotFoundError:
            messagebox.showerror(
                "Error", "Profile Changer.py not found in the current directory."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Profile Changer.py.\n{e}")

    def clear_frame(parent_frame):
        """Clear all widgets from the parent frame, regardless of how they're managed."""
        print("Clearing frame...")

        for widget in parent_frame.winfo_children():
            print(f"Destroying {widget}")
            widget.destroy()
        parent_frame.update()

    def create_input_section(
        parent_frame, title, prompt, on_submit, back_button=False, on_back=None
    ):
        if on_back is None:
            on_back = go_back
        clear_frame(parent_frame)
        title_label = tk.Label(
            parent_frame,
            text=title,
            font=("Helvetica", 15, "bold"),
            bg=header_color,
            fg=TEXT_COLOR,
        )
        title_label.pack(pady=(20, 10))
        prompt_label = tk.Label(
            parent_frame,
            text=prompt,
            font=("Helvetica", 12),
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            wraplength=250,
        )
        prompt_label.pack(pady=(10, 5))
        input_entry = tk.Entry(
            parent_frame, font=("Helvetica", 12), bg="white", fg="black"
        )
        input_entry.pack(pady=(5, 15))
        submit_button = tk.Button(
            parent_frame,
            text="OK",
            font=("Helvetica", 12, "bold"),
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            activebackground=PRIMARY_COLOR,
            relief="flat",
            command=lambda: on_submit(input_entry.get()),
        )
        submit_button.pack(pady=10)

        if back_button:
            back_button = tk.Button(
                parent_frame,
                text="Back",
                font=("Helvetica", 12, "bold"),
                bg=SECONDARY_COLOR,
                fg=TEXT_COLOR,
                relief="flat",
                activebackground=SECONDARY_COLOR,
                command=open_main_Menu,
            )
            back_button.pack(pady=10)
        input_entry.focus()
        parent_frame.bind("<Return>", lambda event: on_submit(input_entry.get()))

    def save_playlist():
        if not selected_scenarios:
            create_input_section(
                right_frame,
                "No Scenarios",
                "No scenarios selected for the playlist.",
                lambda _: None,
            )
            return

        def get_playlist_name(playlist_name):
            if not playlist_name:
                create_input_section(
                    right_frame,
                    "Input Error",
                    "Please provide a valid playlist name.",
                    lambda _: None,
                )
                return

            def get_description(description):
                scenario_list = [
                    {
                        "scenario_name": details["scenario_name"].replace(".sce", ""),
                        "play_Count": details["play_Count"],
                    }
                    for details in selected_scenarios.values()
                ]
                playlist_data = {
                    "playlistName": playlist_name,
                    "playlistId": 0,
                    "authorSteamId": "",
                    "authorName": "",
                    "scenarioList": scenario_list,
                    "description": description,
                    "hasOfflineScenarios": False,
                    "hasEdited": True,
                    "shareCode": "",
                    "version": 31,
                    "updated": 0,
                    "isPrivate": False,
                }
                Folder_directory = get_Playlist_directory()

                if not Folder_directory:
                    return
                playlist_path = os.path.join(Folder_directory, f"{playlist_name}.json")

                with open(playlist_path, "w") as json_file:
                    json.dump(playlist_data, json_file, indent=4)
                create_input_section(
                    right_frame,
                    "Success",
                    f"Playlist '{playlist_path}' saved successfully!",
                    lambda _: None,
                )

            create_input_section(
                right_frame,
                "Description",
                "You can add a description:",
                get_description,
            )

        create_input_section(
            right_frame, "Playlist Name", "Enter the playlist name:", get_playlist_name
        )

    def create_playlist_window(scenarios):
        global right_frame, selected_scenarios, root
        left_frame = tk.Frame(root, bg=header_color, highlightthickness=0, bd=0)
        left_frame.pack(
            side=tk.LEFT, padx=0, pady=3, anchor="nw", fill=tk.BOTH, expand=True
        )
        right_frame = tk.Frame(root, bg=header_color, highlightthickness=0, bd=0)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=0)
        chosen_label = tk.Label(
            right_frame,
            text="Chosen Scenarios",
            font=("Helvetica", 15, "bold"),
            bg=header_color,
            fg=TEXT_COLOR,
        )
        chosen_label.pack(padx=(0, 0), pady=23)
        chosen_canvas = tk.Canvas(
            right_frame, bg=BACKGROUND_COLOR, highlightthickness=0, bd=0
        )
        chosen_canvas.pack(fill=tk.BOTH, expand=True, pady=0)
        top_frame = tk.Frame(chosen_canvas, bg=BACKGROUND_COLOR)
        chosen_canvas.create_window((0, 0), window=top_frame, anchor="n")
        save_button = tk.Button(
            top_frame,
            text="Save Playlist",
            command=save_playlist,
            bg=PRIMARY_COLOR,
            font=("Helvetica", 15, "bold"),
            fg=TEXT_COLOR,
            relief="flat",
        )
        save_button.pack(pady=8, padx=(430, 0))
        chosen_frame = tk.Frame(
            chosen_canvas, bg=BACKGROUND_COLOR, highlightthickness=0, bd=0
        )
        chosen_canvas.create_window((0, 50), window=chosen_frame, anchor="nw")
        search_label = tk.Label(
            left_frame,
            text="Search Scenarios:",
            bg=header_color,
            font=("Helvetica", 15, "bold"),
            fg=TEXT_COLOR,
        )
        search_label.pack(pady=0)
        search_entry = tk.Entry(left_frame, font=FONT_STYLE)
        search_entry.pack(pady=(5, 15))
        canvas = tk.Canvas(left_frame, bg=BACKGROUND_COLOR, highlightthickness=0, bd=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(
            left_frame, orient=tk.VERTICAL, command=canvas.yview, width=0
        )
        canvas.config(yscrollcommand=scrollbar.set)
        back_button = tk.Button(
            root,
            text="Back",
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            command=open_main_Menu,
            relief="flat",
        )
        back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)
        scenario_frame = tk.Frame(
            canvas, bg=BACKGROUND_COLOR, highlightthickness=0, bd=0
        )
        canvas.create_window((0, 0), window=scenario_frame, anchor="nw")
        populate_scenario_buttons(canvas, scenario_frame, scenarios, chosen_frame)
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        selected_scenarios = {
            scenario: {"scenario_name": scenario, "play_Count": 0}
            for scenario in scenarios
        }

        def adjust_left_frame():
            left_frame.update_idletasks()
            canvas.update_idletasks()
            button_width = scenario_frame.winfo_children()[0].winfo_reqwidth()
            gap_between_buttons = 10
            scrollbar_width = scrollbar.winfo_width()
            required_width = (
                (button_width * 2) + gap_between_buttons + scrollbar_width + 10
            )
            canvas.config(width=required_width)
            left_frame.config(width=required_width)
            left_frame.config(height=root.winfo_height())
            canvas.config(
                height=root.winfo_height()
                - search_entry.winfo_height()
                - search_label.winfo_height()
            )

        adjust_left_frame()
        search_entry.bind(
            "<KeyRelease>",
            lambda event: search_scenarios(
                search_entry, canvas, scenario_frame, scenarios, chosen_frame
            ),
        )

        def on_mouse_wheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")

        canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        search_entry.bind(
            "<KeyRelease>",
            lambda event: search_scenarios(
                search_entry, canvas, scenario_frame, scenarios, chosen_frame
            ),
        )

    def create_playlist_start():
        scenario_directory = get_scenario_directory()

        if not scenario_directory:
            return
        sce_files = [f for f in os.listdir(scenario_directory) if f.endswith(".sce")]

        if not sce_files:
            messagebox.showwarning("No Files", "No .sce files found in the directory.")
            return
        create_playlist_window(sce_files)

    if get_Playlist_directory() and get_scenario_directory() is not None:
        create_playlist_start()


if __name__ == "__main__":
    main_menu = os.path.basename(__file__)
    location_file = "palette_file_location.txt"

    if not os.path.exists(location_file):
        ask_palette_choice()
    root = tk.Tk()
    Main_Menu()
