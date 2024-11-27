import getpass
import os
import re
import shutil
import sys
import tkinter as tk
from tkinter import Button, Label, Toplevel, filedialog, messagebox, simpledialog

monitored_directory = r"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\Saved\SaveGames\Scenarios"
presets = {}
current_file = sys.argv[1] if len(sys.argv) > 1 else None
preset_file = "presets.txt"
location_file = "palette_file_location.txt"
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
created_widgets = []


def create_widget(root):
    label = tk.Label(
        root,
        text=f"Widget {len(created_widgets) + 1}",
        bg="#4CAF50",
        fg="white",
        font=("Helvetica", 14, "bold"),
        relief="flat",
    )
    label.pack(pady=10)
    created_widgets.append(label)


def destroy_last_widget():
    if created_widgets:
        widget = created_widgets.pop()
        widget.destroy()
    else:
        print("No widgets to destroy!")


def ask_palette_choice():
    def use_custom_palette():
        choice_window.destroy()
        choice_window1 = tk.Tk()
        choice_window1.title("Palette Info")
        choice_window1.geometry("400x200")
        choice_window1.configure(bg=DEFAULT_BACKGROUND_COLOR)
        label1 = tk.Label(
            choice_window1,
            text=f'the Palette.ini file is normally found at\n "C:/Users/{user}/AppData/Local/FPSAimTrainer/Saved/Config/WindowsNoEditor"',
            bg=DEFAULT_BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 13),
            wraplength=350,
            relief="flat",
            justify="center",
        )
        label1.pack(pady=20)
        label = tk.Button(
            choice_window1,
            text=r"Okay",
            bg=DEFAULT_BACKGROUND_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 14),
            wraplength=350,
            justify="center",
            relief="flat",
            command=lambda: get_palette_directory(use_default=False),
        )
        label.pack(pady=20)
        choice_window1.mainloop()

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
    global choice_window1
    global colors

    if use_default:
        messagebox.showinfo("Default Palette", "Using default palette colors.")
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
        extracted_colors[name] = f"#{R:02x}{G:02x}{B:02x}"  # Convert to hex color
    return extracted_colors


BACKGROUND_COLOR = colors.get("Background", DEFAULT_BACKGROUND_COLOR)
PRIMARY_COLOR = colors.get("Primary", DEFAULT_PRIMARY_COLOR)
SECONDARY_COLOR = colors.get("Secondary", DEFAULT_SECONDARY_COLOR)


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


character_profiles = []
background_color = colors.get("Background", "#222222")  # Default to dark grey
primary_color = colors.get("Primary", "#ff5722")  # Default to orange
secondary_color = colors.get("Secondary", "#555555")  # Default to grey

if not os.path.exists(location_file):
    ask_palette_choice()


def load_presets():
    if os.path.exists(preset_file):
        with open(preset_file, "r") as file:
            for line in file:
                try:
                    name, max_health, size, speed, regen = line.strip().split(",")
                    presets[name] = {
                        "MaxHealth": int(max_health),
                        "Size": int(size),
                        "Speed": int(speed),
                        "HealthRegen": int(regen),
                    }

                except ValueError:
                    continue


def save_preset_to_file(name, max_health, size, speed, regen):
    with open(preset_file, "a") as file:
        file.write(f"{name},{max_health},{size},{speed},{regen}\n")


def show_custom_dialog(title, message, is_error=False):
    dialog = Toplevel(root)
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    label = Label(
        dialog,
        text=message,
        wraplength=350,
        justify="center",
        fg="red" if is_error else "black",
    )
    label.pack(pady=20)
    Button(dialog, text="OK", command=dialog.destroy).pack(pady=10)
    dialog.transient(root)
    dialog.grab_set()
    dialog.wait_window()


def apply_preset(root, preset_name, preset_values):
    if not current_file:
        show_custom_dialog(
            "Error", "No file specified to apply the preset.", is_error=True
        )
        return
    try:
        apply_preset_to_file(current_file, preset_values)

    except Exception as e:
        show_custom_dialog("Error", f"Failed to apply preset: {e}", is_error=True)


def apply_preset_to_file(file_path, preset_values):
    new_name = simpledialog.askstring("Copy File", "Enter a name for the copied file:")

    if not new_name:
        show_custom_dialog("Error", "File name cannot be empty.", is_error=True)
        return
    new_file_path = os.path.join(os.path.dirname(file_path), f"{new_name}.sce")
    shutil.copy(file_path, new_file_path)

    with open(new_file_path, "r+", encoding="utf-8") as file:
        lines = file.readlines()
        updated_lines = []

        for line in lines:
            if line.strip().startswith("MaxHealth="):
                current_value = float(
                    re.search(r"MaxHealth=(\d+(\.\d+)?)", line).group(1)
                )
                new_value = round(current_value * (preset_values["MaxHealth"] / 100), 2)
                updated_lines.append(f"MaxHealth={new_value}\n")

            elif line.strip().startswith("MainBBRadius="):
                current_value = float(
                    re.search(r"MainBBRadius=(\d+(\.\d+)?)", line).group(1)
                )
                new_value = round(current_value * (preset_values["Size"] / 100), 2)
                updated_lines.append(f"MainBBRadius={new_value}\n")

            elif line.strip().startswith("MaxSpeed="):
                current_value = float(
                    re.search(r"MaxSpeed=(\d+(\.\d+)?)", line).group(1)
                )
                new_value = round(current_value * (preset_values["Speed"] / 100), 2)
                updated_lines.append(f"MaxSpeed={new_value}\n")

            elif line.strip().startswith("HealthRegenPerSec="):
                current_value = float(
                    re.search(r"HealthRegenPerSec=(\d+(\.\d+)?)", line).group(1)
                )
                new_value = round(
                    current_value * (preset_values["HealthRegen"] / 100), 2
                )
                updated_lines.append(f"HealthRegenPerSec={new_value}\n")
            else:
                updated_lines.append(line)
        file.seek(0)
        file.writelines(updated_lines)
        file.truncate()


def add_form_row(label_text, entry_var, initial_value, parent):
    row_frame = tk.Frame(parent, bg=BACKGROUND_COLOR)
    row_frame.pack(fill="x", pady=5)
    label = tk.Label(
        row_frame,
        text=label_text,
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14, "bold"),
        width=15,
        anchor="e",
        relief="flat",
    )
    label.pack(side="left", padx=10)
    entry = tk.Entry(
        row_frame,
        bg=SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12, "bold"),
        relief="flat",
    )
    entry.insert(0, initial_value)
    entry.pack(side="left", fill="x", expand=True, padx=10)
    entry_var[label_text] = entry


def edit_preset(root, preset_name):
    clear_window()
    preset = presets[preset_name]
    edit_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
    edit_frame.pack(fill="both", expand=True)
    header = tk.Label(
        edit_frame,
        text=f"Editing Preset: {preset_name}",
        bg=BACKGROUND_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 18, "bold"),
        relief="flat",
    )
    header.pack(pady=10)
    entry_vars = {}
    add_form_row("Preset Name", entry_vars, preset_name, edit_frame)
    add_form_row("MaxHealth %", entry_vars, preset["MaxHealth"], edit_frame)
    add_form_row("MainBBRadius %", entry_vars, preset["Size"], edit_frame)
    add_form_row("MaxSpeed %", entry_vars, preset["Speed"], edit_frame)
    add_form_row("HealthRegenPerSec %", entry_vars, preset["HealthRegen"], edit_frame)

    def save_changes():
        try:
            new_name = entry_vars["Preset Name"].get().strip()
            max_health = int(entry_vars["MaxHealth %"].get())
            size = int(entry_vars["MainBBRadius %"].get())
            speed = int(entry_vars["MaxSpeed %"].get())
            regen = int(entry_vars["HealthRegenPerSec %"].get())

            if not new_name:
                show_custom_dialog(
                    "Error", "Preset name cannot be empty.", is_error=True
                )
                return

            if new_name != preset_name:
                presets.pop(preset_name)
            presets[new_name] = {
                "MaxHealth": max_health,
                "Size": size,
                "Speed": speed,
                "HealthRegen": regen,
            }

            with open(preset_file, "w") as file:
                for name, values in presets.items():
                    file.write(
                        f"{name},{values['MaxHealth']},{values['Size']},{values['Speed']},{values['HealthRegen']}\n"
                    )
            show_presets(root)

        except ValueError:
            show_custom_dialog(
                "Error", "All values must be valid integers.", is_error=True
            )

    save_button = tk.Button(
        edit_frame,
        text="Save Changes",
        command=save_changes,
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 15, "bold"),
        relief="flat",
    )
    save_button.pack(pady=15)
    back_button = tk.Button(
        edit_frame,
        text="Back",
        command=lambda: show_presets(root),
        bg=DEFAULT_PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14),
        relief="flat",
    )
    back_button.pack(pady=10)


def show_presets(root):
    clear_window()
    load_presets()
    preset_list_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
    preset_list_frame.pack(fill="both", expand=True)
    header = tk.Label(
        preset_list_frame,
        text="Select a Preset to Edit or Apply:",
        bg=BACKGROUND_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 18, "bold"),
        relief="flat",
    )
    header.pack(pady=10)

    for name, preset_values in presets.items():
        row_frame = tk.Frame(preset_list_frame, bg=BACKGROUND_COLOR)
        row_frame.pack(fill="x", pady=5)
        preset_label = tk.Label(
            row_frame,
            text=name,
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 14, "bold"),
            width=15,
            anchor="w",
            relief="flat",
        )
        preset_label.pack(side="left", padx=10)
        apply_button = tk.Button(
            row_frame,
            text="Apply",
            command=lambda n=name, p=preset_values: apply_preset(root, n, p),
            bg=PRIMARY_COLOR,
            fg="white",
            font=("Helvetica", 12),
            relief="flat",
        )
        apply_button.pack(side="left", padx=5)
        edit_button = tk.Button(
            row_frame,
            text="Edit",
            command=lambda n=name: edit_preset(root, n),
            bg=DEFAULT_PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 12),
            relief="flat",
        )
        edit_button.pack(side="left", padx=5)
    back_button = tk.Button(
        root,
        text="Back",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 16, "bold"),
        relief="flat",
        command=lambda: open_preset_button(),
    )
    back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)


def save_preset():
    name = name_entry.get().strip()

    if not name:
        show_custom_dialog("Error", "Preset name cannot be empty.", is_error=True)
        return
    try:
        max_health = int(max_health_entry.get() or 100)
        size = int(size_entry.get() or 100)
        speed = int(speed_entry.get() or 100)
        regen = int(regen_entry.get() or 100)

    except ValueError:
        show_custom_dialog(
            "Error", "Please enter valid integers from 0 to 100.", is_error=True
        )
        return
    presets[name] = {
        "MaxHealth": max_health,
        "Size": size,
        "Speed": speed,
        "HealthRegen": regen,
    }
    save_preset_to_file(name, max_health, size, speed, regen)
    clear_window()
    open_preset_button()


def create_new_preset_window(root):
    new_preset_window = tk.Frame(root, bg=BACKGROUND_COLOR)
    new_preset_window.pack(fill="both", expand=True)
    header_frame = tk.Frame(new_preset_window, bg=BACKGROUND_COLOR, padx=10, pady=10)
    header_frame.pack(fill="x")
    header = tk.Label(
        header_frame,
        text="If you want 30% smaller, input 70\nfor 60% smaller, input 40 etc.",
        bg=BACKGROUND_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 20, "bold"),
        relief="flat",
    )
    header.pack(fill="x", pady=5)
    form_frame = tk.Frame(new_preset_window, bg=BACKGROUND_COLOR, padx=20, pady=10)
    form_frame.pack(fill="both", expand=True)
    tk.Label(
        form_frame,
        text="Preset Name",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14, "bold"),
    ).grid(row=0, column=0, padx=10, pady=5, sticky="e")

    global name_entry
    name_entry = tk.Entry(
        form_frame,
        bg=SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12, "bold"),
        relief="flat",
    )
    name_entry.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(
        form_frame,
        text="MaxHealth %",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14, "bold"),
    ).grid(row=1, column=0, padx=10, pady=5, sticky="e")

    global max_health_entry
    max_health_entry = tk.Entry(
        form_frame,
        bg=SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12, "bold"),
        relief="flat",
    )
    max_health_entry.grid(row=1, column=1, padx=10, pady=5)
    tk.Label(
        form_frame,
        text="MainBBRadius %",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14, "bold"),
    ).grid(row=2, column=0, padx=10, pady=5, sticky="e")

    global size_entry
    size_entry = tk.Entry(
        form_frame,
        bg=SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12, "bold"),
        relief="flat",
    )
    size_entry.grid(row=2, column=1, padx=10, pady=5)
    tk.Label(
        form_frame,
        text="MaxSpeed %",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14, "bold"),
    ).grid(row=3, column=0, padx=10, pady=5, sticky="e")

    global speed_entry
    speed_entry = tk.Entry(
        form_frame,
        bg=SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12, "bold"),
        relief="flat",
    )
    speed_entry.grid(row=3, column=1, padx=10, pady=5)
    tk.Label(
        form_frame,
        text="HealthRegenPerSec %",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 14, "bold"),
    ).grid(row=4, column=0, padx=10, pady=5, sticky="e")

    global regen_entry
    regen_entry = tk.Entry(
        form_frame,
        bg=SECONDARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 12, "bold"),
        relief="flat",
    )
    regen_entry.grid(row=4, column=1, padx=10, pady=5)
    save_button = tk.Button(
        form_frame,
        text="Save Preset",
        command=save_preset,
        bg=PRIMARY_COLOR,
        fg="white",
        font=("Helvetica", 15, "bold"),
        relief="flat",
    )
    save_button.grid(row=5, column=0, columnspan=2, pady=15)
    back_button = tk.Button(
        root,
        text="Back",
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        font=("Helvetica", 16, "bold"),
        relief="flat",
        command=lambda: open_preset_button(),
    )
    back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("600x600")
    root.config(background=BACKGROUND_COLOR)

    def open_preset_button():
        clear_window()
        create_preset_button = tk.Button(
            root,
            text="Create New Preset",
            command=lambda: create_new_preset_window(root),
            bg=DEFAULT_PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 14),
            relief="flat",
        )
        create_preset_button.pack(pady=10)
        show_presets_button = tk.Button(
            root,
            text="Show Presets",
            command=lambda: show_presets(root),
            bg=DEFAULT_SECONDARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 14),
            relief="flat",
        )
        show_presets_button.pack(pady=10)
        back_button = tk.Button(
            root,
            text="Back",
            bg=PRIMARY_COLOR,
            fg=TEXT_COLOR,
            font=("Helvetica", 16, "bold"),
            relief="flat",
            command=lambda: root.destroy(),
        )
        back_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    open_preset_button()
    root.mainloop()
