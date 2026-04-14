import os
import shutil
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

FILES_TO_MOVE = ["CETAVDynamicCampaignCLIENT.luac", "CETAVDynamicCampaignSYSTEM.luac"]
LINES_TO_INSERT = r"pcall(function() function LuaExportStop() local CETAVDynamicCampaignlfs=require('lfs') dofile(CETAVDynamicCampaignlfs.writedir()..'Scripts\\Hooks\\CETAVDynamicCampaignSYSTEM.luac') end end)"
IMAGE_FILE = "cetav-logo.png"
LOGO_FILE = "cetav-isologo.png"

TEXTS = {
    "en": {
        "title": "CETAV Dynamic Campaign Package Installer",
        "welcome": "Select the DCS installation folder:",
        "browse": "Browse",
        "install": "Install",
        "back": "← Change Language",
        "success": "Installation complete!",
        "error": "Error during installation.",
        "invalid": "Please select a valid folder."
    },
    "es": {
        "title": "Instalador de paquete para campaña dinámica de CETAV",
        "welcome": "Selecciona la carpeta de instalación de DCS:",
        "browse": "Buscar",
        "install": "Instalar",
        "back": "← Cambiar Idioma",
        "success": "¡Instalación completada!",
        "error": "Error durante la instalación.",
        "invalid": "Por favor, selecciona una carpeta válida."
    }
}

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x480") 
        self.lang = None
        
        # --- Window icon ---
        try:
            icon_path = resource_path(LOGO_FILE)
            icon_img = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(False, icon_img)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
        
        self.banner_img = None
        
        try:
            img_path = resource_path(IMAGE_FILE)
            if os.path.exists(img_path):
                self.banner_img = tk.PhotoImage(file=img_path)
        except Exception as e:
            print(f"No se pudo cargar la imagen: {e}")

        self.show_language_selection()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_language_selection(self):
        self.root.title(TEXTS['en']["title"])
        self.clear_window()
        
        # --- Banner ---
        if self.banner_img:
            img_label = tk.Label(self.root, image=self.banner_img)
            img_label.pack(pady=(10, 0))
        else:
            tk.Frame(self.root, height=80).pack()

        tk.Label(self.root, text="CETAV Dynamic Campaign installation pack", 
                 font=("Arial", 12), pady=20).pack()

        tk.Label(self.root, text="Select Language\n/ Seleccione Idioma", 
                 font=("Arial", 12, "bold"), pady=20).pack()
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(expand=True)

        tk.Button(btn_frame, text="English", width=15, height=2,
                  command=lambda: self.start_installer("en")).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Español", width=15, height=2,
                  command=lambda: self.start_installer("es")).pack(side=tk.LEFT, padx=10)

    def start_installer(self, lang):
        self.lang = lang
        self.root.title(TEXTS[self.lang]["title"])
        self.clear_window()
        self.setup_main_ui()

    def setup_main_ui(self):
        # Back button
        back_btn = tk.Button(self.root, text=TEXTS[self.lang]["back"], 
                             command=self.show_language_selection, 
                             relief=tk.FLAT, fg="blue", cursor="hand2")
        back_btn.pack(anchor="nw", padx=10, pady=5)

        # --- Banner ---
        if self.banner_img:
            img_label = tk.Label(self.root, image=self.banner_img)
            img_label.pack(pady=5)

        tk.Label(self.root, text=TEXTS[self.lang]["welcome"], font=("Arial", 10)).pack(pady=15)

        # Path selection
        path_frame = tk.Frame(self.root)
        path_frame.pack(padx=30, fill='x')

        user_home = os.path.expanduser("~")
        path_beta = os.path.join(user_home, "Saved Games", "DCS.openbeta")
        path_stable = os.path.join(user_home, "Saved Games", "DCS")

        default_path = path_beta if os.path.exists(path_beta) else path_stable
        
        self.path_var = tk.StringVar(value=default_path)
        
        self.entry = tk.Entry(path_frame, textvariable=self.path_var)
        self.entry.pack(side=tk.LEFT, expand=True, fill='x', padx=(0, 5))

        tk.Button(path_frame, text=TEXTS[self.lang]["browse"], command=self.browse_folder).pack(side=tk.RIGHT)

        # Install button
        tk.Button(self.root, text=TEXTS[self.lang]["install"], bg="#2e7d32", fg="white", 
                  font=("Arial", 11, "bold"), width=20, height=2,
                  command=self.run_install).pack(pady=30)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def run_install(self):
        dest_path = self.path_var.get()

        if not dest_path or not os.path.exists(dest_path):
            messagebox.showwarning("!", TEXTS[self.lang]["invalid"])
            return

        try:
            hooks_path = os.path.join(dest_path, "Scripts", "Hooks")
            os.makedirs(hooks_path, exist_ok=True)

            # 1. Copy the hook files to the destination
            for file in FILES_TO_MOVE:
                source = resource_path(file)
                shutil.copy(source, hooks_path)

            # 2. Insert the line into Export.lua
            export_script_path = os.path.join(dest_path, "Scripts", "Export.lua")
            
            # Ensure the Scripts folder exists for Export.lua
            os.makedirs(os.path.dirname(export_script_path), exist_ok=True)

            # 3. Read the existing content of Export.lua (if it exists) to avoid duplicate insertions
            content = ""
            if os.path.exists(export_script_path):
                with open(export_script_path, "r", encoding="utf-8") as f:
                    content = f.read()

            # 4. Only insert the line if it's not already present
            if LINES_TO_INSERT.strip() not in content:
                with open(export_script_path, "a", encoding="utf-8") as f:
                    f.write(f"\n{LINES_TO_INSERT}")

            messagebox.showinfo("DCS", TEXTS[self.lang]["success"])
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"{TEXTS[self.lang]['error']}\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()