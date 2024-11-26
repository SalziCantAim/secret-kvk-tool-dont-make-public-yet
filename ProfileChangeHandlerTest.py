import sys
import subprocess
import getpass


def get_scenario_directory():

    location_file = 'Scenario_folder_location.txt'

    if os.path.exists(location_file):


        with open(location_file, 'r') as file:

            Folder_directory = file.read().strip()
    else:
        Folder_directory = filedialog.askdirectory(title="Select Scenario Folder")

        if Folder_directory:


            with open(location_file, 'w') as file:

                file.write(Folder_directory)
            open_main_Menu()
        else:
            messagebox.showwarning("No scenarios", "Please select a valid Scenario folder.")
            get_scenario_directory()
            return None
    return Folder_directory
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
DEFAULT_BACKGROUND_COLOR = "#36323b"
DEFAULT_PRIMARY_COLOR = "#ff5722"
DEFAULT_SECONDARY_COLOR = "#4e4a54"
TEXT_COLOR = "white"
user = getpass.getuser()
colors = {
    "Background": DEFAULT_BACKGROUND_COLOR,
    "Primary": DEFAULT_PRIMARY_COLOR,
    "Secondary": DEFAULT_SECONDARY_COLOR
}


def ask_palette_choice():


    def use_custom_palette():

        choice_window.destroy()
        get_palette_directory(use_default=False)
        label = tk.Label(
            choice_window,
            text=fr'the Palette.ini file is normally found at "C:\Users\{user}\AppData\Local\FPSAimTrainer\Saved\Config\WindowsNoEditor"',
            bg=DEFAULT_BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 14),
            wraplength=350,
            justify="center"
        )
        label.pack(pady=20)


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
        justify="center"
    )
    label.pack(pady=20)
    custom_button = tk.Button(
        choice_window,
        text="My Own",
        bg=DEFAULT_PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12),
        relief="flat",
        command=use_custom_palette
    )
    custom_button.pack(pady=5)
    default_button = tk.Button(
        choice_window,
        text="Default",
        bg=DEFAULT_SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12),
        relief="flat",
        command=use_default_palette
    )
    default_button.pack(pady=5)
    choice_window.mainloop()


def get_palette_directory(use_default):

    global colors

    if use_default:
        messagebox.showinfo("Default Palette", "Using default palette colors.")
        return
    location_file = 'palette_folder_location.txt'
    appdata = os.getenv('LOCALAPPDATA')

    if os.path.exists(location_file):


        with open(location_file, 'r') as file:

            palette_file_path = file.read().strip()
    else:
        palette_file_path = filedialog.askopenfilename(
            title="Select Palette.ini File",
            filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")],
            initialdir=appdata)

        if palette_file_path:


            with open(location_file, 'w') as file:

                file.write(palette_file_path)
        else:
            messagebox.showwarning("No Palette", "Please select a valid Palette folder.")
            return

    if os.path.exists(palette_file_path):
        colors = extract_palette_colors(palette_file_path)
    else:
        messagebox.showerror("Error", "Palette.ini file not found in the selected folder.")


def extract_palette_colors(file_path):


    with open(file_path, 'r') as file:

        content = file.read()
    pattern = r"\((?P<name>[^,]+), \(\s*B=(?P<B>\d+),G=(?P<G>\d+),R=(?P<R>\d+),A=\d+\)\)"
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
header_color = "#1b191f"


def clear_window():


    for widget in root.winfo_children():
        widget.destroy()


def clear_back():

    clear_window()
    open_scenario_editor(scenario)


def open_main_Menu():

    clear_window()
    try:
        print("hi")
        subprocess.run(["python", main_file], check=True)

    except FileNotFoundError:
        messagebox.showerror("Error", "Profile Changer.py not found in the current directory.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Profile Changer.py.\n{e}")


def save_to_temp_file(profile_name, values):

    key_replacements = {
        "Size": "MainBBRadius",
        "HealthRegen": "HealthRegenPerSec"
    }
    formatted_data = "\n".join(
        f"{key_replacements.get(key, key)}={value}" for key, value in values.items()
    )
    try:


        with open("temp_scenario.txt", "w") as file:

            file.write(formatted_data)
        print("Data saved successfully.")

    except Exception as e:
        print(f"Error saving data: {e}")
    messagebox.showinfo("Success", "Changes saved to a temporary file.")


def load_temp_scenario_data():

    temp_data = {}
    try:


        with open('temp_scenario.txt', 'r') as temp_file:

            lines = temp_file.readlines()

            for line in lines:
                line = line.strip()

                if "=" in line:
                    key, value = line.split("=", 1)
                    temp_data[key] = value
                    print(f"{key}: {value}")

    except FileNotFoundError:
        messagebox.showerror("Error", "temp_scenario.txt not found.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load temp_scenario.txt.\n{e}")
    print("temp_data:", temp_data)
    return temp_data


def copy_scen_file():


    with open(path, 'r', encoding='utf-8') as file:

        lines = file.read()
        return lines


def edit_values(selected_profile, file_path):

    temp_values = {}


    with open("temp_scenario.txt", 'r') as temp_file:


        for line in temp_file:

            if "=" in line:
                key, value = line.strip().split("=", 1)
                temp_values[key] = value


    with open(file_path, 'r', encoding='utf-8') as file:

        lines = file.readlines()
    in_correct_profile = False
    updated_lines = []

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith("[Character Profile]"):
            in_correct_profile = False

        if stripped_line.startswith("Name="):
            current_profile_name = stripped_line.split("=")[1]
            in_correct_profile = current_profile_name == selected_profile

        if in_correct_profile and "=" in stripped_line:
            key = stripped_line.split("=")[0]

            if key in temp_values:
                line = f"{key}={temp_values[key]}\n"
        updated_lines.append(line)


    with open(file_path, 'w', encoding='utf-8') as file:

        file.writelines(updated_lines)


def get_current_values(profile, path):

    print(fr"{path}")


    with open(path, "r", encoding="utf-8") as file:

        lines = file.readlines()
    updated_lines = lines.copy()
    in_character_profile = False
    current_profile_name = None
    current_values = {}

    for i, line in enumerate(updated_lines):
        stripped_line = line.strip()

        if stripped_line.startswith("[Character Profile]"):
            in_character_profile = True
            current_profile_name = None

        if in_character_profile and stripped_line.startswith("Name="):
            current_profile_name = stripped_line.split("=")[-1].strip()
            in_character_profile = False

        if current_profile_name == profile:

            if stripped_line.startswith("MaxHealth="):
                current_values["MaxHealth"] = stripped_line.split("=")[-1]

            elif stripped_line.startswith("MainBBRadius="):
                current_values["Size"] = stripped_line.split("=")[-1]

            elif stripped_line.startswith("MaxSpeed="):
                current_values["Speed"] = stripped_line.split("=")[-1]

            elif stripped_line.startswith("HealthRegenPerSec="):
                current_values["HealthRegen"] = stripped_line.split("=")[-1]
    return current_values


def count_button_calls():

    profile_button_count = len(character_profiles)
    explicit_button_count = 2
    total_button_count = profile_button_count + explicit_button_count
    return total_button_count


def open_scenario_editor(scenario):

    clear_window()
    fixed_width = 400
    current_file_path = ""
    print("hi1")
    new_file_path = ""
    path = rf"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Scenarios\{scenario}"
    root.config(bg=BACKGROUND_COLOR)
    """Open a new window to edit the selected scenario."""
    editor_frame = tk.Frame(padx=10, pady=25, bg=BACKGROUND_COLOR)
    editor_frame.pack()
    headers = tk.Label(
        editor_frame,
        text=f"Editing {scenario}",
        bg=BACKGROUND_COLOR,
        fg=TEXT_COLOR,
        width=60,
        font=("Helvetica", 32, "bold"),
        pady=10)
    headers.pack(padx=0)
    back_button = tk.Button(
        root,
        text="Back",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 16, "bold"),
        relief="flat",
        command=lambda: root.destroy()
    )
    back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)


    def open_presets():

        global current_file_path
        subprocess.run(["python", "presets.py", path], check=True)


    def rename_copied_file():

        global new_file_path


        with open('temp_scenario.txt') as f:

            first_line = f.readline()
        header = tk.Label(
            root,
            text=f"Save changes for {scenario}",
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            pady=10
        )
        header.pack(fill="x")
        form_frame = tk.Frame(root, bg=BACKGROUND_COLOR, padx=10, pady=10)
        form_frame.pack(fill="y")
        labels = "Enter new Name:"
        entries = {}
        bg_color = BACKGROUND_COLOR
        tk.Label(
                form_frame,
                text=labels,
                bg=PRIMARY_COLOR,
                fg=TEXT_COLOR,
                font=("Helvetica", 14, "bold"),
                anchor="w"
        ).grid(row=1, column=0, padx=10, pady=5)
        initial_value = scenario
        entry_width = max(10, len(str(initial_value)) + 2)
        entry = tk.Entry(
            form_frame,
                bg=SECONDARY_COLOR,
                fg=TEXT_COLOR,
                font=("Helvetica", 12, "bold"),
                relief="flat",
                width=entry_width
        )
        entry.insert(0, initial_value)
        entry.grid(row=1, column=1, padx=10, pady=5)
        entries[labels] = entry
        form_frame.grid_columnconfigure(1, weight=1)
        save_button = tk.Button(
            root,
            text="Save",
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 12, "bold"),
            relief="flat",
            command=lambda: save_changes(entry)
        )
        save_button.pack(pady=10)
        back_button = tk.Button(
            root,
            text="Back",
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            command=lambda:clear_back(),
            relief="flat"
        )
        back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)


        def save_changes(entry_field):

            global new_file_path
            new_name = entry_field.get().strip()
            print(new_name)
            new_file_name = f"{new_name}.sce"
            renamed_file_path = os.path.join(os.path.dirname(path), new_file_name)

            if os.path.exists(renamed_file_path):
                new_file_name = f"Salzi_{new_name}.sce"
                renamed_file_path = os.path.join(os.path.dirname(path), new_file_name)
            os.rename(new_file_path, renamed_file_path)
            messagebox.showinfo("Success", f"File renamed to {new_file_name}")
            print(renamed_file_path)
            root.destroy()


    def create_profile_buttons():

        total_height = 0
        label = tk.Label(
            editor_frame,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 20, "bold"),
            text="Select a Character Profile to edit:",
            width=fixed_width // 10
        )
        label.pack(fill="x", padx=250, pady=10)
        total_height += label.winfo_reqheight() + 10

        for profile in character_profiles:
            button = tk.Button(
                editor_frame,
                text=profile,
                bg=PRIMARY_COLOR,
                fg=TEXT_COLOR,
                command=lambda p=profile: edit_attributes_dialog(p, editor_frame),
                font=("Helvetica", 16, "bold"),
                relief="flat",
                width=fixed_width // 10
            )
            button.pack(fill="x", padx=250, pady=(10,50))
            total_height += button.winfo_reqheight() + 10
        preset_button = tk.Button(
            editor_frame,
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            text="Open Presets",
            relief="flat",
            command=open_presets,
            width=fixed_width // 10
        )
        preset_button.pack(fill="x", padx=250, pady=10)
        total_height += preset_button.winfo_reqheight() + 10
        rename_button = tk.Button(
            editor_frame,
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            text="Rename Copied File, Save and Exit",
            command=rename_copied_file,
            relief="flat",
            width=fixed_width // 10
        )
        rename_button.pack(fill="x", padx=250, pady=10)
        total_height += rename_button.winfo_reqheight() + 10
        editor_frame.config(height=total_height + 10)


    def process_file(file_path):

        global character_profiles
        character_profiles = []


        with open(file_path, "r", encoding="utf-8") as file:

            lines = file.readlines()
        current_profile_name = None
        player_profile_name = None
        in_character_profile = False

        for line in lines:
            stripped_line = line.strip()

            if stripped_line.startswith("PlayerCharacters="):
                player_profile_name = stripped_line.split("=")[-1].strip()
                break

        for line in lines:
            stripped_line = line.strip()

            if stripped_line.startswith("[Character Profile]"):
                in_character_profile = True
                current_profile_name = None

            if in_character_profile and stripped_line.startswith("Name="):
                current_profile_name = stripped_line.split("=")[-1].strip()

                if current_profile_name != player_profile_name:
                    character_profiles.append(current_profile_name)
                in_character_profile = False

    if path:
        path = fr"{path}"
        process_file(path)
        create_profile_buttons()
        root.mainloop()


def edit_attributes_dialog(selected_profile, editor_frame):

    counter = count_button_calls()
    header = tk.Label(
        root,
        text=f"Edit Attributes for {selected_profile}",
        bg=BACKGROUND_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 20, "bold"),
        pady=10,
        relief="flat"
    )
    header.pack(fill="x", pady=10)
    container_frame = tk.Frame(root, bg=SECONDARY_COLOR, padx=20, pady=20)
    container_frame.pack(fill="y")
    container_frame.grid_columnconfigure(0, weight=1)
    container_frame.grid_columnconfigure(1, weight=1)
    labels = ["MaxHealth", "Size", "Speed", "HealthRegen"]
    entries = {}
    current_values = get_current_values(selected_profile, path)

    for i, label in enumerate(labels):
        tk.Label(
            container_frame,
            text=label,
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 14, "bold"),
            anchor="center",
            relief="flat"
        ).grid(row=i, column=0, padx=10, pady=5, sticky="nsew")
        initial_value = current_values.get(label, "")
        entry_width = max(10, len(str(initial_value)) + 2)
        entry = tk.Entry(
            container_frame,
            bg=BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 12, "bold"),
            relief="flat",
            width=entry_width
        )
        entry.insert(0, initial_value)
        entry.grid(row=i, column=1, padx=10, pady=5, sticky="nsew")
        entries[label] = entry
    save_button = tk.Button(
        container_frame,
        text="Save",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12, "bold"),
        relief="flat",
        command=lambda: save_changes(entries)
    )
    save_button.grid(row=len(labels), column=0, columnspan=2, pady=15)
    back_button = tk.Button(
        root,
        text="Back",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 16, "bold"),
        command=lambda: clear_back(),
        relief="flat"
    )
    back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)


    def save_changes(entries):

        updated_values = {label: entry.get() for label, entry in entries.items()}
        save_to_temp_file(selected_profile, updated_values)
        new_lines = copy_scen_file()
        new_file_path = os.path.join(os.path.dirname(path),
                                     "Profile_Changer_" + os.path.basename(path))


        with open(new_file_path, 'w', encoding='utf-8') as new_file:

            new_file.write(new_lines)
        edit_values(selected_profile, new_file_path)
        open_scenario_editor(scenario)

if __name__ == "__main__":
    TEMP_FILE_PATH = "temp_scenario.txt"
    main_file = sys.argv[1]
    scenario = sys.argv[2]
    scen_folder = get_scenario_directory()
    location_file = 'palette_file_location.txt'

    if not os.path.exists(location_file):
        ask_palette_choice()
    root = tk.Tk()
    root.title("Kovaak's Menu")
    root.geometry("1200x1000")
    path = rf"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Scenarios\{scenario}"
    new_file_path = os.path.join(os.path.dirname(path),
                                 "Profile_Changer_" + os.path.basename(path))
    open_scenario_editor(scenario)
