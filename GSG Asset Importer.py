
#
#   GSG Asset Importer unofficial  for Octane
#   A tool for 3ds Max to import Greyscalegorilla assets for the Octane renderer.
#   It handles materials (procedural and textured), HDRI environments, and FBX files.
#
#   Author: Iman Shirani
#   Version: 0.0.1 - Focused on Octane-only workflow and UI enhancements.
#
#   License: MIT License
#
#   Copyright (c) 2025 Iman Shirani
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
#

import os
import json
import webbrowser
from PySide6 import QtWidgets, QtCore, QtGui
from pymxs import runtime as rt

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +                        SECTION 1: CONSTANTS                       +
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

AUTHOR_NAME = "Iman Shirani"
VERSION = "0.0.1"
GITHUB_LINK = "https://github.com/imanshirani/GSG-Asset-Importer"
PAYPAL_LINK = "https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4"

LINKS = {
    "The Greyscalegorilla Studio": "https://greyscalegorilla.com/"
}

# A modern, consistent style for the main action buttons
BUTTON_STYLE = """
    QPushButton {
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
    QPushButton:pressed {
        background-color: #3e8e41;
    }
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +               SECTION 2: DIALOGS AND TAB WIDGETS                  +
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class AboutDialog(QtWidgets.QDialog):
    """ The About dialog with author info and support links. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About GSG Importer")
        self.setFixedSize(350, 200)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        title_label = QtWidgets.QLabel(f"GSG Asset Importer v{VERSION}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        author_label = QtWidgets.QLabel(f"Author: {AUTHOR_NAME}")
        github_label = QtWidgets.QLabel(f'<a style="color: #4A90E2;" href="{GITHUB_LINK}">GitHub Repository</a>')
        github_label.setOpenExternalLinks(True)
        paypal_label = QtWidgets.QLabel(f'<a style="color: #4A90E2;" href="{PAYPAL_LINK}">Support the Project (PayPal)</a>')
        paypal_label.setOpenExternalLinks(True)
        ok_button = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ok_button.accepted.connect(self.accept)
        layout.addWidget(title_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(author_label)
        layout.addWidget(github_label)
        layout.addWidget(paypal_label)
        layout.addStretch()
        layout.addWidget(ok_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

class MaterialTab(QtWidgets.QWidget):
    """ The UI tab for creating materials from GSG folders. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = ""
        layout = QtWidgets.QVBoxLayout(self)
        self.folder_path_label = QtWidgets.QLabel("Please select a GSG material folder...")
        browse_button = QtWidgets.QPushButton("Browse Folder...")
        create_button = QtWidgets.QPushButton("Create Octane Material")
        create_button.setStyleSheet(BUTTON_STYLE)
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.folder_path_label)
        layout.addWidget(browse_button)
        layout.addWidget(create_button)
        layout.addWidget(QtWidgets.QLabel("Log:"))
        layout.addWidget(self.log_box)
        browse_button.clicked.connect(self.browse_folder)
        create_button.clicked.connect(self.run_creation_process)

    def log_message(self, message):
        self.log_box.append(message)
        print(message)

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select GSG Asset Folder")
        if folder:
            self.selected_folder = folder
            self.folder_path_label.setText(folder)
            self.log_message(f"Folder selected: {folder}")

    def run_creation_process(self):
        if not self.selected_folder:
            rt.messageBox("Please select a folder first!", title="Warning")
            return
        self.log_box.clear()
        create_octane_material(self.selected_folder, self.log_message)

class HDRITab(QtWidgets.QWidget):
    """ The UI tab for creating HDRI environments. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_file = ""
        layout = QtWidgets.QVBoxLayout(self)
        self.file_path_label = QtWidgets.QLabel("Please select an HDRI file (.hdr, .exr)...")
        browse_button = QtWidgets.QPushButton("Browse File...")
        create_button = QtWidgets.QPushButton("Create HDRI Environment")
        create_button.setStyleSheet(BUTTON_STYLE)
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.file_path_label)
        layout.addWidget(browse_button)
        layout.addWidget(create_button)
        layout.addWidget(QtWidgets.QLabel("Log:"))
        layout.addWidget(self.log_box)
        browse_button.clicked.connect(self.browse_file)
        create_button.clicked.connect(self.run_creation_process)

    def log_message(self, message):
        self.log_box.append(message)
        print(message)

    def browse_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select HDRI File", "", "HDRI Files (*.hdr *.exr)")
        if file:
            self.selected_file = file
            self.file_path_label.setText(file)
            self.log_message(f"File selected: {file}")
            
    def run_creation_process(self):
        if not self.selected_file:
            rt.messageBox("Please select a file first!", title="Warning")
            return
        self.log_box.clear()
        create_octane_hdri(self.selected_file, self.log_message)

class FBXTab(QtWidgets.QWidget):
    """ The UI tab for importing FBX files from a folder. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_folder = ""
        layout = QtWidgets.QVBoxLayout(self)
        self.folder_path_label = QtWidgets.QLabel("Please select a folder containing .fbx files...")
        browse_button = QtWidgets.QPushButton("Browse Folder...")
        import_button = QtWidgets.QPushButton("Import All FBX Files")
        import_button.setStyleSheet(BUTTON_STYLE)
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.folder_path_label)
        layout.addWidget(browse_button)
        layout.addWidget(import_button)
        layout.addWidget(QtWidgets.QLabel("Log:"))
        layout.addWidget(self.log_box)
        browse_button.clicked.connect(self.browse_folder)
        import_button.clicked.connect(self.run_import_process)

    def log_message(self, message):
        self.log_box.append(message)
        print(message)

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select FBX Folder")
        if folder:
            self.selected_folder = folder
            self.folder_path_label.setText(folder)
            self.log_message(f"Folder selected: {folder}")

    def run_import_process(self):
        if not self.selected_folder:
            rt.messageBox("Please select a folder first!", title="Warning")
            return
        self.log_box.clear()
        import_fbx_files(self.selected_folder, self.log_message)

class TextureTab(QtWidgets.QWidget):
    """ The UI tab for importing standalone textures as nodes. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files = []
        layout = QtWidgets.QVBoxLayout(self)
        self.files_label = QtWidgets.QLabel("Select one or more texture files to import as nodes...")
        browse_button = QtWidgets.QPushButton("Browse Texture Files...")
        import_button = QtWidgets.QPushButton("Import Textures as Nodes")
        import_button.setStyleSheet(BUTTON_STYLE)
        self.log_box = QtWidgets.QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.files_label)
        layout.addWidget(browse_button)
        layout.addWidget(import_button)
        layout.addWidget(QtWidgets.QLabel("Log:"))
        layout.addWidget(self.log_box)
        browse_button.clicked.connect(self.browse_files)
        import_button.clicked.connect(self.run_import_process)

    def log_message(self, message):
        self.log_box.append(message)
        print(message)

    def browse_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Texture Files", "", "Image Files (*.jpg *.png *.tif *.tiff *.exr *.hdr)")
        if files:
            self.selected_files = files
            self.files_label.setText(f"{len(files)} file(s) selected.")
            for f in files: self.log_message(f"Selected: {os.path.basename(f)}")

    def run_import_process(self):
        if not self.selected_files:
            rt.messageBox("Please select one or more files first!", title="Warning")
            return
        self.log_box.clear()
        import_textures_as_nodes(self.selected_files, self.log_message)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +                    SECTION 3: CORE LOGIC FUNCTIONS                +
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def create_octane_material(folder_path, status_callback):
    status_callback("--- Starting Octane Material Creation ---")
    try:
        if "octane" not in str(rt.classOf(rt.renderers.current)).lower():
            rt.messageBox("Octane is not the active renderer.", title="Renderer Error")
            status_callback("!!! ERROR: Octane is not the active renderer.")
            return False

        gsgm_file_path = next((os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith('.gsgm')), None)
        if not gsgm_file_path:
            rt.messageBox("No .gsgm file found.", title="Error"); return False
        
        with open(gsgm_file_path, 'r', encoding='utf-8') as f: data = json.load(f)
        material_name = data.get('name', os.path.basename(folder_path))
        params = data.get('params', {}).get('standard_surface', {})
        status_callback(f"Found material '{material_name}' with {len(params)} parameters.")
        
        maps = {}
        all_files = os.listdir(folder_path)
        keywords = {"albedo": ["albedo", "basecolor", "diffuse", "_col"], "roughness": ["roughness", "_rgh"], "normal": ["normal", "_nrm", "_nor"], "metallic": ["metallic", "metalness", "_met"], "displacement": ["displacement", "displace", "height", "_disp"], "scattering_weight": ["scatteringweight"], "scattering_distance": ["scatteringdistancescale"]}
        for map_type, keys in keywords.items():
            for filename in all_files:
                if any(k in filename.lower() for k in keys) and any(filename.lower().endswith(ext) for ext in ['.jpg', '.png', '.jpeg', '.tif', '.exr']):
                    maps[map_type] = os.path.join(folder_path, filename); break
        
        param_blocks = []
        param_map = {'base_color': ('baseColor_color', 'albedo', True), 'specular_roughness': ('roughness_value', 'roughness', False), 'metallic': ('metallic_value', 'metallic', False), 'transmission': ('transmission_value', None, False), 'transmission_color': ('transmissionColor_color', None, True), 'specular_IOR': ('ior_value', None, False), 'scattering_weight': ('scattering_color', 'scattering_weight', True), 'scatteringdistancescale': ('radius_value', 'scattering_distance', False)}
        for json_key, (mat_prop, map_key, is_color) in param_map.items():
            if json_key in params and (not map_key or not maps.get(map_key)):
                value = params[json_key]
                if is_color and isinstance(value, dict): param_blocks.append(f'mtl.{mat_prop} = color {value.get("r",0)*255} {value.get("g",0)*255} {value.get("b",0)*255}')
                elif not is_color: param_blocks.append(f'mtl.{mat_prop} = {value}')
        final_param_code = "\n".join(param_blocks)
        
        def tex_block(tex_path, slot, is_linear=False):
            if not tex_path: return ""
            sanitized_path = tex_path.replace("\\", "/"); var_name = slot.replace("_tex", "Tex"); gamma_line = f"{var_name}.gamma = 1.0" if is_linear else ""
            input_prop_name = slot.replace("_tex", "") + "_input_type"
            if slot == "displacement": return f'if doesFileExist "{sanitized_path}" do (local dN=Texture_displacement();local dT=RGB_image filename:"{sanitized_path}";dT.gamma=1.0;dN.texture_tex=dT;mtl.displacement=dN)'
            return f'if doesFileExist "{sanitized_path}" do (local {var_name}=RGB_image filename:"{sanitized_path}";{gamma_line};mtl.{input_prop_name}=2;mtl.{slot}={var_name})'

        tex_code_blocks = [tex_block(maps.get("albedo"), "baseColor_tex"), tex_block(maps.get("roughness"), "roughness_tex", True), tex_block(maps.get("metallic"), "metallic_tex", True), tex_block(maps.get("normal"), "normal_tex", True), tex_block(maps.get("displacement"), "displacement"), tex_block(maps.get("scattering_weight"), "scattering_tex", False), tex_block(maps.get("scattering_distance"), "radius_tex", True)]
        final_tex_code = "\n".join(tex_code_blocks)
        mat_lib_path = os.path.join(folder_path, f"{material_name}.mat").replace("\\", "/")
        
        mxs_command = f'''
        (
            local mtl = Std_Surface_Mtl name:"{material_name}"
            {final_param_code}
            {final_tex_code}
            local activeView = sme.GetView sme.activeView; if (activeView != undefined) do (activeView.CreateNode mtl [200, 200]);
            local lib = materialLibrary(); append lib mtl; saveTempMaterialLibrary lib "{mat_lib_path}";
            "OK"
        )
        '''
        status_callback("Executing generated MaxScript...")
        result = rt.execute(mxs_command)
        if result != "OK": raise Exception("MaxScript execution failed. Check Listener for errors.")
        status_callback(f"-> Octane material '{material_name}' created successfully.")

    except Exception as e:
        error_message = f"An error occurred: {e}"
        status_callback(f"!!! SCRIPT ERROR: {error_message}")
        rt.messageBox(error_message, title="Script Error")
        return False
    status_callback("--- PROCESS COMPLETE! ---"); return True

def create_octane_hdri(file_path, status_callback):
    status_callback("--- Creating Octane HDRI Environment ---")
    try:
        sanitized_path = file_path.replace("\\", "/")
        mxs_command = f'''
        (
            -- Create the nodes
            local tex = RGB_image filename:"{sanitized_path}"
            local env = Texture_environment()
            
            -- Configure the environment node
            env.power = 1.0
            env.importance_sampling = true
            env.texture_input_type = 2
            env.texture_tex = tex
            
            -- Assign to the scene environment (your original logic)
            environmentMap = env
            
            -- NEW: Place the created nodes in the active Slate view
            local activeView = sme.GetView sme.activeView
            if (activeView != undefined) do
            (
                activeView.CreateNode tex [200, 150]
                activeView.CreateNode env [450, 200]
            )
            
            "OK"
        )
        '''
        result = rt.execute(mxs_command)
        if result != "OK": raise Exception("MaxScript failed.")
        status_callback(f"SUCCESS: Environment set and nodes created for '{os.path.basename(file_path)}'")
    except Exception as e:
        status_callback(f"!!! ERROR: Could not create HDRI environment. {e}")

def import_fbx_files(folder_path, status_callback):
    status_callback(f"--- Importing FBX files from: {folder_path} ---"); fbx_found = False
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.fbx'):
            fbx_found = True; full_path = os.path.join(folder_path, filename); status_callback(f"-> Importing '{filename}'...")
            try: rt.importFile(full_path, rt.name("noPrompt"))
            except Exception as e: status_callback(f"!!! ERROR: Failed to import '{filename}'. {e}")
    if not fbx_found: status_callback("No .fbx files found.")
    else: status_callback("--- FBX Import Complete ---")

def import_textures_as_nodes(file_paths, status_callback):
    status_callback(f"--- Importing {len(file_paths)} textures as nodes ---")
    try:
        for i, file_path in enumerate(file_paths):
            sanitized_path = file_path.replace("\\", "/"); file_name = os.path.basename(sanitized_path)
            pos_x = 200; pos_y = i * 150
            status_callback(f"-> Creating node for '{file_name}'...")
            mxs_command = f'(local activeView = sme.GetView sme.activeView; if (activeView != undefined) then (local texNode = RGB_image filename:"{sanitized_path}"; texNode.name = "{file_name}"; activeView.CreateNode texNode [ {pos_x}, {pos_y} ]; "OK") else ("FAIL"))'
            result = rt.execute(mxs_command)
            if result != "OK": status_callback(f"!!! WARNING: Could not get active SME view. Is the Slate Material Editor open?"); break
        status_callback("--- Texture Import Complete ---")
    except Exception as e: status_callback(f"!!! ERROR: An error occurred during import. {e}")

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +                   SECTION 4: MAIN APPLICATION WINDOW              +
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class AssetManagerUI(QtWidgets.QMainWindow):
    """ The main application window, containing menus and tabs. """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # The incorrect self.setParent() line has been removed.
        # We set the window flag to 'Tool' to make it behave correctly within 3ds Max.
        flags = QtCore.Qt.WindowType.Tool | QtCore.Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
        self.setWindowTitle(f"GSG Asset Importer v{VERSION}")
        self.resize(500, 600)
        
        self._create_menus()
        self._create_tabs()

    def _create_menus(self):
        help_menu = self.menuBar().addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.open_about_dialog)

        links_menu = self.menuBar().addMenu("Links")
        for name, url in LINKS.items():
            action = links_menu.addAction(name)
            action.triggered.connect(lambda checked=False, u=url: webbrowser.open(u))

    def _create_tabs(self):
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.tabs.addTab(MaterialTab(), "Materials")
        self.tabs.addTab(HDRITab(), "HDRI")
        self.tabs.addTab(TextureTab(), "Import Textures")
        self.tabs.addTab(FBXTab(), "Import FBX")
        
    def open_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +                        SECTION 5: SCRIPT EXECUTION                +
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def main():
    """
    This function creates and shows the main application window.
    """
    # Create an instance of our UI without a parent to ensure stability
    app_window = AssetManagerUI()
    app_window.show()
    
    # Return the window instance to keep it from being garbage collected
    return app_window
    

if __name__ == "__main__":
    try:
        # Close the previous instance of the window if it exists
        main_window.close()
        main_window.deleteLater()
    except:
        pass
    
    # Run the main function to create and show the window
    main_window = main()