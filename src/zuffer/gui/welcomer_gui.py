import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
import tkinter.font as tkFont 
import json
import uuid
import os
import shutil
from PIL import Image, ImageTk

DEFAULT_CONFIG = {
    "image_settings": {
        "width": 700,
        "height": 250,
        "background_type": "color",
        "background_color": "#2c2f33",
        "background_image_path": ""
    },
    "discord_settings": {
        "channel_id": "YOUR_CHANNEL_ID_HERE"
    },
    "avatar_settings": {
        "x": 20,
        "y": 20,
        "size": 100,
        "visible": True
    },
    "text_elements": [
        {
            "id": "text_default_1",
            "content": "Welcome, {username}!",
            "x": 150,
            "y": 50,
            "color": "#ffffff",
            "font_size": 28,
            "font_family": "Arial"
        },
        {
            "id": "text_default_2",
            "content": "Enjoy your stay in the server!",
            "x": 150,
            "y": 100,
            "color": "#b9bbbe",
            "font_size": 18,
            "font_family": "Arial"
        }
    ]
}

class WelcomeImageConfigurator:
    def __init__(self, master):
        self.master = master
        master.title("Welcome Image Configurator")
        master.geometry("1200x750")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.config = DEFAULT_CONFIG.copy()
        self.selected_item_on_canvas = None
        self.current_selection_type = None # Added: "avatar", "text", or None
        self.drag_data = {"x": 0, "y": 0, "item_dict": None, "item_type": None}

        self.bg_pil_image = None
        self.bg_photo_image = None
        self.current_config_file_path = None

        self.image_width_var = tk.IntVar(value=self.config["image_settings"]["width"])
        self.image_height_var = tk.IntVar(value=self.config["image_settings"]["height"])

        self.avatar_size_var = tk.IntVar(value=self.config["avatar_settings"]["size"]) # Added

        self.background_type_var = tk.StringVar(value=self.config["image_settings"]["background_type"])
        self.image_bg_color_var = tk.StringVar(value=self.config["image_settings"]["background_color"])
        self.image_bg_image_path_abs_var = tk.StringVar(value="")

        self.channel_id_var = tk.StringVar(value=self.config["discord_settings"]["channel_id"])

        self.current_text_content_var = tk.StringVar()
        self.current_text_font_size_var = tk.IntVar()
        self.current_text_color_var = tk.StringVar()
        self.current_text_font_family_var = tk.StringVar()

        self.image_width_var.trace_add("write", self.on_image_settings_change)
        self.image_height_var.trace_add("write", self.on_image_settings_change)
        self.background_type_var.trace_add("write", self.on_background_type_change)
        self.avatar_size_var.trace_add("write", self.on_avatar_settings_change) # Added

        self.setup_ui()
        self.update_canvas_dimensions()
        self.update_bg_controls_state()
        self.redraw_canvas()

    def setup_ui(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        control_panel = ttk.Frame(main_frame, width=380, padding="10")
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_panel.pack_propagate(False)

        canvas_panel = ttk.Frame(main_frame)
        canvas_panel.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self._create_image_settings_ui(control_panel)
        self._create_discord_settings_ui(control_panel)
        self._create_elements_ui(control_panel)
        self._create_text_properties_ui(control_panel)
        self._create_alignment_tools_ui(control_panel) # Added
        self._create_file_operations_ui(control_panel)

        self.canvas = tk.Canvas(canvas_panel, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)

    def _create_image_settings_ui(self, parent):
        frame = ttk.LabelFrame(parent, text="Image Settings", padding="10")
        frame.pack(fill=tk.X, pady=5)

        ttk.Label(frame, text="Width:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame, textvariable=self.image_width_var, width=7).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(frame, text="Height:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(frame, textvariable=self.image_height_var, width=7).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(frame, text="Background:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        bg_type_frame = ttk.Frame(frame)
        bg_type_frame.grid(row=2, column=1, columnspan=2, sticky=tk.EW)
        self.rb_bg_color = ttk.Radiobutton(bg_type_frame, text="Color", variable=self.background_type_var, value="color")
        self.rb_bg_color.pack(side=tk.LEFT, padx=(0,10))
        self.rb_bg_image = ttk.Radiobutton(bg_type_frame, text="Image", variable=self.background_type_var, value="image")
        self.rb_bg_image.pack(side=tk.LEFT)

        ttk.Label(frame, text="BG Color:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.bg_color_preview = tk.Label(frame, text="  ", bg=self.image_bg_color_var.get(), relief=tk.SUNKEN, width=3)
        self.bg_color_preview.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        self.bg_color_choose_btn = ttk.Button(frame, text="Choose", command=self.choose_bg_color, width=8)
        self.bg_color_choose_btn.grid(row=3, column=2, sticky=tk.E, padx=5, pady=2)

        ttk.Label(frame, text="BG Image:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.bg_image_path_label = ttk.Label(frame, textvariable=self.image_bg_image_path_abs_var, relief=tk.SUNKEN, width=25, anchor=tk.W, wraplength=180) # Wraplength for better path display
        self.bg_image_path_label.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=2)
        self.bg_image_browse_btn = ttk.Button(frame, text="Browse", command=self.choose_bg_image, width=8)
        self.bg_image_browse_btn.grid(row=4, column=2, sticky=tk.E, padx=5, pady=2)

        frame.columnconfigure(1, weight=1)

    def update_bg_controls_state(self, *args):
        bg_type = self.background_type_var.get()
        if bg_type == "color":
            self.bg_color_preview.config(state=tk.NORMAL)
            self.bg_color_choose_btn.config(state=tk.NORMAL)
            self.bg_image_path_label.config(state=tk.DISABLED) 
            self.bg_image_browse_btn.config(state=tk.DISABLED)
        elif bg_type == "image":
            self.bg_color_preview.config(state=tk.DISABLED)
            self.bg_color_choose_btn.config(state=tk.DISABLED)
            self.bg_image_path_label.config(state=tk.NORMAL)
            self.bg_image_browse_btn.config(state=tk.NORMAL)
        self.config["image_settings"]["background_type"] = bg_type

    def on_background_type_change(self, *args):
        self.update_bg_controls_state()
        self.redraw_canvas()

    def choose_bg_image(self):
        try:
            filepath = filedialog.askopenfilename(
                title="Select Background Image",
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
            )
            if filepath and os.path.exists(filepath):
                self.image_bg_image_path_abs_var.set(filepath)
                self.bg_pil_image = Image.open(filepath)
                self.config["image_settings"]["background_image_path"] = "" 
                self.redraw_canvas()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")
            self.image_bg_image_path_abs_var.set("")
            self.bg_pil_image = None
            self.redraw_canvas()


    def _create_discord_settings_ui(self, parent):
        frame = ttk.LabelFrame(parent, text="Discord Settings", padding="10")
        frame.pack(fill=tk.X, pady=5)
        ttk.Label(frame, text="Channel ID:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(frame, textvariable=self.channel_id_var).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

    def _create_elements_ui(self, parent):
        frame = ttk.LabelFrame(parent, text="Elements", padding="10")
        frame.pack(fill=tk.X, pady=5)

        avatar_frame = ttk.Frame(frame)
        avatar_frame.pack(fill=tk.X, pady=(0,5))

        ttk.Label(avatar_frame, text="Avatar: Draggable").pack(side=tk.LEFT, pady=2)

        avatar_controls_frame = ttk.Frame(avatar_frame)
        avatar_controls_frame.pack(side=tk.LEFT, padx=(10,0))

        ttk.Label(avatar_controls_frame, text="Size:").pack(side=tk.LEFT, pady=2, padx=(0,2))
        self.avatar_size_entry = ttk.Entry(avatar_controls_frame, textvariable=self.avatar_size_var, width=5)
        self.avatar_size_entry.pack(side=tk.LEFT, pady=2)

        ttk.Button(frame, text="Add Text Element", command=self.add_text_element).pack(fill=tk.X, pady=(5,0))

    def on_avatar_settings_change(self, *args):
        try:
            new_size = self.avatar_size_var.get()
            current_avatar_conf = self.config["avatar_settings"]
            default_size = DEFAULT_CONFIG["avatar_settings"]["size"]

            if new_size <= 0: 
                self.avatar_size_var.set(current_avatar_conf.get("size", default_size))
                return

            current_avatar_conf["size"] = new_size

            img_width = self.config["image_settings"]["width"]
            img_height = self.config["image_settings"]["height"]

            # current_avatar_conf["x"] = max(0, min(current_avatar_conf["x"], img_width - new_size if img_width > new_size else 0))
            # current_avatar_conf["y"] = max(0, min(current_avatar_conf["y"], img_height - new_size if img_height > new_size else 0))
            clamped_x = max(0, min(current_avatar_conf["x"], img_width - new_size if img_width > new_size else 0))
            clamped_y = max(0, min(current_avatar_conf["y"], img_height - new_size if img_height > new_size else 0))
            current_avatar_conf["x"] = int(round(clamped_x))
            current_avatar_conf["y"] = int(round(clamped_y))

            if new_size >= img_width: current_avatar_conf["x"] = 0
            if new_size >= img_height: current_avatar_conf["y"] = 0

            self.redraw_canvas()
        except tk.TclError: 
            self.avatar_size_var.set(self.config["avatar_settings"].get("size", DEFAULT_CONFIG["avatar_settings"]["size"]))
        except Exception as e: 
            print(f"Error in on_avatar_settings_change: {e}")
            self.avatar_size_var.set(self.config["avatar_settings"].get("size", DEFAULT_CONFIG["avatar_settings"]["size"]))


    def _create_text_properties_ui(self, parent):
        self.text_props_frame = ttk.LabelFrame(parent, text="Selected Text Properties", padding="10")
        self.text_props_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.text_props_frame, text="Content:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.text_content_entry = ttk.Entry(self.text_props_frame, textvariable=self.current_text_content_var, width=30)
        self.text_content_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(self.text_props_frame, text="Font Family:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.font_family_combo = ttk.Combobox(self.text_props_frame, textvariable=self.current_text_font_family_var, width=15,
                                             values=["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "Impact", "Comic Sans MS", "Tahoma", "Georgia"]) # Added more fonts
        self.font_family_combo.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)

        ttk.Label(self.text_props_frame, text="Font Size:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(self.text_props_frame, textvariable=self.current_text_font_size_var, width=5).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.text_props_frame, text="Color:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.text_color_preview = tk.Label(self.text_props_frame, text="  ", relief=tk.SUNKEN, width=4)
        self.text_color_preview.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Button(self.text_props_frame, text="Choose", command=self.choose_text_color, width=8).grid(row=3, column=2, sticky=tk.E, padx=5, pady=2)

        self.delete_text_button = ttk.Button(self.text_props_frame, text="Delete Selected Text", command=self.delete_selected_text_element)
        self.delete_text_button.grid(row=4, column=0, columnspan=3, sticky=tk.EW, pady=(10,0), padx=5)

        self.text_props_frame.columnconfigure(1, weight=1)
        self.disable_text_properties_panel()

    def _create_alignment_tools_ui(self, parent):
        self.alignment_frame = ttk.LabelFrame(parent, text="Alignment Tools", padding="10")
        self.alignment_frame.pack(fill=tk.X, pady=5)

        self.alignment_buttons = {}
        button_config = [
            ("Align Left", self.align_left), ("Center H", self.align_center_h), ("Align Right", self.align_right),
            ("Align Top", self.align_top), ("Center V", self.align_center_v), ("Align Bottom", self.align_bottom),
        ]

        row, col = 0, 0
        for i, (text, command) in enumerate(button_config):
            button = ttk.Button(self.alignment_frame, text=text, command=command, state=tk.DISABLED)
            button.grid(row=row, column=col, padx=2, pady=2, sticky=tk.EW)
            self.alignment_buttons[text] = button
            col += 1
            if col >= 3:  
                col = 0
                row += 1

        for c_idx in range(3): 
            self.alignment_frame.columnconfigure(c_idx, weight=1)

    def enable_disable_alignment_buttons(self, enable=True):
        state_cmd = '!disabled' if enable else 'disabled'
        for button in self.alignment_buttons.values():
            if isinstance(button, ttk.Button): # Ensure it's a ttk button
                 button.state([state_cmd])

    def _create_file_operations_ui(self, parent):
        frame = ttk.Frame(parent, padding="10")
        frame.pack(fill=tk.X, pady=10, side=tk.BOTTOM)
        ttk.Button(frame, text="Save Configuration", command=self.save_config).pack(side=tk.LEFT, expand=True, padx=2)
        ttk.Button(frame, text="Load Configuration", command=self.load_config).pack(side=tk.LEFT, expand=True, padx=2)

    def on_image_settings_change(self, *args):
        try:
            new_width = self.image_width_var.get()
            new_height = self.image_height_var.get()
            if new_width > 0 and new_height > 0:
                self.config["image_settings"]["width"] = new_width
                self.config["image_settings"]["height"] = new_height
                self.update_canvas_dimensions()
                self.redraw_canvas()
        except tk.TclError: 
            pass

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Choose Background Color", initialcolor=self.image_bg_color_var.get())
        if color_code and color_code[1]:
            self.image_bg_color_var.set(color_code[1])
            self.config["image_settings"]["background_color"] = color_code[1]
            self.bg_color_preview.config(bg=color_code[1])
            if self.background_type_var.get() == "color":
                 self.redraw_canvas()

    def update_canvas_dimensions(self):
        canvas_width = self.config["image_settings"]["width"]
        canvas_height = self.config["image_settings"]["height"]
        self.canvas.config(width=canvas_width, height=canvas_height)

    def redraw_canvas(self):
        self.canvas.delete("all")
        img_conf = self.config["image_settings"]
        width, height = img_conf["width"], img_conf["height"]

        if self.background_type_var.get() == "image":
            abs_image_path = self.image_bg_image_path_abs_var.get()
            if abs_image_path and os.path.exists(abs_image_path):
                try:
                    if not self.bg_pil_image or \
                       (hasattr(self.bg_pil_image, 'fp') and self.bg_pil_image.fp and self.bg_pil_image.fp.name != abs_image_path) or \
                       (not hasattr(self.bg_pil_image, 'fp')): 
                        self.bg_pil_image = Image.open(abs_image_path)

                    pil_image_resized = self.bg_pil_image.resize((width, height), Image.Resampling.LANCZOS)
                    self.bg_photo_image = ImageTk.PhotoImage(pil_image_resized)
                    self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_photo_image, tags="image_boundary")
                except Exception as e:
                    print(f"Error processing background image for canvas: {e}")
                    self.canvas.create_rectangle(0, 0, width, height, fill=img_conf["background_color"], outline="lightgray", tags="image_boundary")
            else:
                self.canvas.create_rectangle(0, 0, width, height, fill=img_conf["background_color"], outline="lightgray", tags="image_boundary")
        else:
            self.canvas.create_rectangle(0, 0, width, height, fill=img_conf["background_color"], outline="lightgray", tags="image_boundary")

        avatar_conf = self.config["avatar_settings"]
        if avatar_conf["visible"]:
            x, y, size = avatar_conf["x"], avatar_conf["y"], avatar_conf["size"]
            self.canvas.create_oval(x, y, x + size, y + size, fill="gray", outline="darkgray", tags="avatar")
            if self.selected_item_on_canvas is avatar_conf and self.current_selection_type == "avatar":
                 self.canvas.create_oval(x-2, y-2, x + size+2, y + size+2, outline="cyan", width=2, tags="selection_highlight")

        for text_elem in self.config["text_elements"]:
            text_id_on_canvas = self.canvas.create_text(text_elem["x"], text_elem["y"], text=text_elem["content"],
                                 fill=text_elem["color"],
                                 font=(text_elem["font_family"], text_elem["font_size"]),
                                 anchor=tk.NW, tags=("text_element", text_elem["id"]))
            if self.selected_item_on_canvas is text_elem and self.current_selection_type == "text":
                bbox = self.canvas.bbox(text_id_on_canvas)
                if bbox: self.canvas.create_rectangle(bbox, outline="cyan", width=2, tags="selection_highlight")

        self.canvas.tag_raise("selection_highlight")


    def on_canvas_press(self, event):
        self.selected_item_on_canvas = None
        self.current_selection_type = None
        self.drag_data = {"x": 0, "y": 0, "item_dict": None, "item_type": None}

        self.disable_text_properties_panel()

        avatar_conf = self.config["avatar_settings"]
        ax, ay, asize = avatar_conf["x"], avatar_conf["y"], avatar_conf["size"]
        center_x, center_y, radius = ax + asize / 2, ay + asize / 2, asize / 2

        clicked_on_item = False
        if avatar_conf["visible"] and (event.x - center_x)**2 + (event.y - center_y)**2 <= radius**2 :
            self.selected_item_on_canvas = avatar_conf
            self.current_selection_type = "avatar"
            self.drag_data["item_dict"] = avatar_conf 
            self.drag_data["item_type"] = "avatar"
            clicked_on_item = True
        else: 
            overlapping_ids = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
            selected_text_elem = None
            for item_id_on_canvas in reversed(overlapping_ids):
                item_tags = self.canvas.gettags(item_id_on_canvas)
                if "text_element" in item_tags:
                    text_elem_id_from_tag = item_tags[1] if len(item_tags) > 1 else None
                    if text_elem_id_from_tag:
                        for elem_dict in self.config["text_elements"]:
                            if elem_dict["id"] == text_elem_id_from_tag:
                                selected_text_elem = elem_dict
                                break
                    if selected_text_elem:
                        break

            if selected_text_elem:
                self.selected_item_on_canvas = selected_text_elem
                self.current_selection_type = "text"
                self.drag_data["item_dict"] = selected_text_elem 
                self.drag_data["item_type"] = "text"
                self.enable_text_properties_panel(selected_text_elem)
                clicked_on_item = True

        if clicked_on_item:
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.enable_disable_alignment_buttons(True)
        else: 
            self.disable_text_properties_panel() 
            self.enable_disable_alignment_buttons(False)

        self.redraw_canvas()


    def on_canvas_drag(self, event):
        if self.drag_data["item_dict"] and self.selected_item_on_canvas: 
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]

            item_to_move = self.selected_item_on_canvas 

            item_to_move["x"] += dx
            item_to_move["y"] += dy

            img_width = self.config["image_settings"]["width"]
            img_height = self.config["image_settings"]["height"]

            if self.current_selection_type == "avatar":
                item_size = item_to_move["size"]
                item_to_move["x"] = max(0, min(item_to_move["x"], img_width - item_size if img_width > item_size else 0))
                item_to_move["y"] = max(0, min(item_to_move["y"], img_height - item_size if img_height > item_size else 0))
                # clamped_x = max(0, min(item_to_move["x"], img_width - item_size if img_width > item_size else 0))
                # clamped_y = max(0, min(item_to_move["y"], img_height - item_size if img_height > item_size else 0))
                # item_to_move["x"] = int(round(clamped_x))
                # item_to_move["y"] = int(round(clamped_y))
                 # If avatar is larger than canvas, its (x,y) should be 0
                if item_size >= img_width: item_to_move["x"] = 0
                if item_size >= img_height: item_to_move["y"] = 0

            elif self.current_selection_type == "text":
                item_width, item_height = self._get_selected_item_dimensions() 
                item_to_move["x"] = max(0, min(item_to_move["x"], img_width - item_width if img_width > item_width else 0))
                item_to_move["y"] = max(0, min(item_to_move["y"], img_height - item_height if img_height > item_height else 0))
                if item_width >= img_width: item_to_move["x"] = 0
                if item_height >= img_height: item_to_move["y"] = 0


            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.redraw_canvas()

    def on_canvas_release(self, event):
        self.drag_data["item_dict"] = None 
        self.drag_data["item_type"] = None


    def on_canvas_right_click(self, event):
        self.selected_item_on_canvas = None
        self.current_selection_type = None
        self.disable_text_properties_panel()
        self.enable_disable_alignment_buttons(False)
        self.redraw_canvas()

    def add_text_element(self):
        new_id = "text_" + uuid.uuid4().hex[:8]
        default_x = 20 + (len(self.config["text_elements"]) % 5) * 10
        default_y = 20 + (len(self.config["text_elements"]) // 5) * 20
        new_text_elem = {"id": new_id, "content": "New Text", "x": default_x, "y": default_y,
                         "color": "#ffffff", "font_size": 20, "font_family": "Arial"}
        self.config["text_elements"].append(new_text_elem)
        self.selected_item_on_canvas = new_text_elem
        self.current_selection_type = "text"
        self.enable_text_properties_panel(new_text_elem)
        self.enable_disable_alignment_buttons(True)
        self.redraw_canvas()

    def delete_selected_text_element(self):
        if self.selected_item_on_canvas and self.current_selection_type == "text":
            elem_id_to_delete = self.selected_item_on_canvas.get("id")
            if elem_id_to_delete:
                self.config["text_elements"] = [e for e in self.config["text_elements"] if e["id"] != elem_id_to_delete]
                self.selected_item_on_canvas = None
                self.current_selection_type = None
                self.disable_text_properties_panel()
                self.enable_disable_alignment_buttons(False)
                self.redraw_canvas()
        else: messagebox.showinfo("Info", "No text element selected to delete, or selected item is not text.")

    def enable_text_properties_panel(self, text_element_dict):
        if hasattr(self, "_text_content_trace_id") and self._text_content_trace_id:
            self.current_text_content_var.trace_vdelete("w", self._text_content_trace_id)
        if hasattr(self, "_font_size_trace_id") and self._font_size_trace_id:
            self.current_text_font_size_var.trace_vdelete("w", self._font_size_trace_id)
        if hasattr(self, "_font_family_trace_id") and self._font_family_trace_id:
            self.current_text_font_family_var.trace_vdelete("w", self._font_family_trace_id)

        self.current_text_content_var.set(text_element_dict["content"])
        self.current_text_font_size_var.set(text_element_dict["font_size"])
        self.current_text_color_var.set(text_element_dict["color"])
        self.current_text_font_family_var.set(text_element_dict["font_family"])
        self.text_color_preview.config(bg=text_element_dict["color"])

        for child in self.text_props_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Button, ttk.Combobox)):
                try:
                    child.state(['!disabled'])
                except tk.TclError:
                    pass
            elif isinstance(child, tk.Label):
                try:
                    child.config(state=tk.NORMAL)
                except tk.TclError:
                    pass
        self.delete_text_button.config(state=tk.NORMAL) 

        self._text_content_trace_id = self.current_text_content_var.trace_add("write", self.on_selected_text_property_change)
        self._font_size_trace_id = self.current_text_font_size_var.trace_add("write", self.on_selected_text_property_change)
        self._font_family_trace_id = self.current_text_font_family_var.trace_add("write", self.on_selected_text_property_change)
        
    def disable_text_properties_panel(self):
        if hasattr(self, "_text_content_trace_id") and self._text_content_trace_id:
            self.current_text_content_var.trace_vdelete("w", self._text_content_trace_id)
            self._text_content_trace_id = None
        if hasattr(self, "_font_size_trace_id") and self._font_size_trace_id:
            self.current_text_font_size_var.trace_vdelete("w", self._font_size_trace_id)
            self._font_size_trace_id = None
        if hasattr(self, "_font_family_trace_id") and self._font_family_trace_id:
            self.current_text_font_family_var.trace_vdelete("w", self._font_family_trace_id)
            self._font_family_trace_id = None

        self.current_text_content_var.set("")
        try: self.current_text_font_size_var.set(0) #
        except tk.TclError: self.current_text_font_size_var.set(12) 
        self.current_text_color_var.set("#000000")
        self.current_text_font_family_var.set("Arial")
        self.text_color_preview.config(bg="lightgray")

        for child in self.text_props_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Button, ttk.Combobox)):
                try:
                     if hasattr(child, 'state') and callable(child.state): 
                         child.state(['disabled'])
                     else: 
                         child.config(state=tk.DISABLED)
                except tk.TclError: pass
        self.delete_text_button.config(state=tk.DISABLED) 

    def on_selected_text_property_change(self, *args):
        if self.selected_item_on_canvas and self.current_selection_type == "text":
            try:
                font_size = self.current_text_font_size_var.get()
                if font_size <= 0: font_size = 1 
            except tk.TclError: 
                font_size = self.selected_item_on_canvas.get("font_size", 12) 

            self.selected_item_on_canvas["content"] = self.current_text_content_var.get()
            self.selected_item_on_canvas["font_size"] = font_size
            self.selected_item_on_canvas["font_family"] = self.current_text_font_family_var.get()
            self.redraw_canvas()

    def choose_text_color(self):
        if self.selected_item_on_canvas and self.current_selection_type == "text":
            initial_color = self.selected_item_on_canvas.get("color", "#000000")
            color_code = colorchooser.askcolor(title="Choose Text Color", initialcolor=initial_color)
            if color_code and color_code[1]:
                new_color = color_code[1]
                self.current_text_color_var.set(new_color)
                self.selected_item_on_canvas["color"] = new_color
                self.text_color_preview.config(bg=new_color)
                self.redraw_canvas()

    # --- Alignment Helper Methods ---
    def _get_selected_item_dimensions(self):
        if not self.selected_item_on_canvas or not self.current_selection_type:
            return 0, 0

        item_dict = self.selected_item_on_canvas
        if self.current_selection_type == "avatar":
            size = item_dict.get("size", DEFAULT_CONFIG["avatar_settings"]["size"])
            return size, size
        elif self.current_selection_type == "text":
            font_size, font_family, content = item_dict["font_size"], item_dict["font_family"], item_dict["content"]
            if self.selected_item_on_canvas is item_dict and \
               hasattr(self, 'current_text_font_size_var'): 
                try:
                    ui_font_size = self.current_text_font_size_var.get()
                    if ui_font_size > 0: font_size = ui_font_size
                    font_family = self.current_text_font_family_var.get()
                    content = self.current_text_content_var.get()
                except tk.TclError: pass 

            try:
                font = tkFont.Font(family=font_family, size=font_size)
                width = font.measure(content)
                height = font.metrics("linespace")
                return width, height
            except Exception as e:
                print(f"Error measuring text in _get_selected_item_dimensions: {e}")
                return 20, 10 
        return 0, 0

    def _align_item(self, set_x=None, set_y=None, center_h=False, center_v=False, align_r=False, align_b=False):
        if not self.selected_item_on_canvas: return

        item_dict = self.selected_item_on_canvas 
        item_width, item_height = self._get_selected_item_dimensions()

        if item_width == 0: item_width = 1
        if item_height == 0: item_height = 1

        canvas_width = self.config["image_settings"]["width"]
        canvas_height = self.config["image_settings"]["height"]

        new_x = item_dict["x"] 
        new_y = item_dict["y"] 

        if set_x is not None: new_x = set_x
        if set_y is not None: new_y = set_y

        if center_h: new_x = (canvas_width - item_width) / 2.0
        if center_v: new_y = (canvas_height - item_height) / 2.0

        if align_r: new_x = canvas_width - item_width
        if align_b: new_y = canvas_height - item_height

        final_x = max(0, min(new_x, canvas_width - item_width if canvas_width > item_width else 0))
        final_y = max(0, min(new_y, canvas_height - item_height if canvas_height > item_height else 0))
        item_dict["x"] = final_x
        item_dict["y"] = final_y

        if item_width >= canvas_width: item_dict["x"] = 0
        if item_height >= canvas_height: item_dict["y"] = 0

        self.redraw_canvas()

    def align_left(self): self._align_item(set_x=0)
    def align_right(self): self._align_item(align_r=True)
    def align_top(self): self._align_item(set_y=0)
    def align_bottom(self): self._align_item(align_b=True)
    def align_center_h(self): self._align_item(center_h=True)
    def align_center_v(self): self._align_item(center_v=True)

    # --- File Operations ---
    def save_config(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="welcome_config.json",
            title="Save Configuration"
        )
        if not filepath: return

        self.current_config_file_path = filepath

        config_to_save = self.config.copy() 

        if config_to_save["image_settings"].get("background_type") == "image":
            original_abs_image_path = self.image_bg_image_path_abs_var.get()
            if original_abs_image_path and os.path.exists(original_abs_image_path):
                json_dir = os.path.dirname(filepath)
                assets_dir = os.path.join(json_dir, "assets")
                os.makedirs(assets_dir, exist_ok=True)

                image_filename = os.path.basename(original_abs_image_path)
                destination_path_abs = os.path.join(assets_dir, image_filename)

                try:
                    if not os.path.exists(destination_path_abs) or not os.path.samefile(original_abs_image_path, destination_path_abs):
                        shutil.copy2(original_abs_image_path, destination_path_abs)
                    config_to_save["image_settings"]["background_image_path"] = os.path.join("assets", image_filename)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy background image: {e}\nSaving config with current image path setting.")
            else: 
                config_to_save["image_settings"]["background_image_path"] = ""
        else:
            config_to_save["image_settings"]["background_image_path"] = ""

        config_to_save["discord_settings"]["channel_id"] = self.channel_id_var.get()

        try:
            with open(filepath, "w") as f:
                json.dump(config_to_save, f, indent=4)
            messagebox.showinfo("Success", f"Configuration saved to {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def load_config(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Configuration"
        )
        if not filepath: return

        self.current_config_file_path = filepath

        try:
            with open(filepath, "r") as f:
                loaded_config = json.load(f)

            required_keys = ["image_settings", "text_elements", "avatar_settings", "discord_settings"]
            if not all(k in loaded_config for k in required_keys):
                 messagebox.showerror("Error", "Invalid or incomplete configuration file format."); return

            self.config = loaded_config 

            img_settings = self.config.get("image_settings", DEFAULT_CONFIG["image_settings"].copy())
            self.image_width_var.set(img_settings.get("width", DEFAULT_CONFIG["image_settings"]["width"]))
            self.image_height_var.set(img_settings.get("height", DEFAULT_CONFIG["image_settings"]["height"]))

            loaded_bg_type = img_settings.get("background_type", "color")
            self.background_type_var.set(loaded_bg_type)

            self.image_bg_color_var.set(img_settings.get("background_color", DEFAULT_CONFIG["image_settings"]["background_color"]))
            self.bg_color_preview.config(bg=self.image_bg_color_var.get())

            avatar_settings = self.config.get("avatar_settings", DEFAULT_CONFIG["avatar_settings"].copy())
            self.avatar_size_var.set(avatar_settings.get("size", DEFAULT_CONFIG["avatar_settings"]["size"]))


            self.image_bg_image_path_abs_var.set("")
            self.bg_pil_image = None

            if loaded_bg_type == "image":
                relative_image_path = img_settings.get("background_image_path", "")
                if relative_image_path:
                    json_dir = os.path.dirname(filepath)
                    abs_image_path = os.path.normpath(os.path.join(json_dir, relative_image_path))
                    if os.path.exists(abs_image_path):
                        self.image_bg_image_path_abs_var.set(abs_image_path)
                        try:
                            self.bg_pil_image = Image.open(abs_image_path)
                        except Exception as e:
                            messagebox.showerror("Error", f"Failed to load background image '{relative_image_path}': {e}\nReverting to color background.")
                            self.background_type_var.set("color")
                            self.config["image_settings"]["background_type"] = "color" # Update config state
                            self.config["image_settings"]["background_image_path"] = ""
                    else:
                        messagebox.showwarning("Warning", f"Background image not found: {abs_image_path} (from '{relative_image_path}')\nReverting to color background.")
                        self.background_type_var.set("color")
                        self.config["image_settings"]["background_type"] = "color"
                        self.config["image_settings"]["background_image_path"] = ""
                else: 
                    self.background_type_var.set("color")
                    self.config["image_settings"]["background_type"] = "color"


            self.channel_id_var.set(self.config.get("discord_settings", {}).get("channel_id", DEFAULT_CONFIG["discord_settings"]["channel_id"]))

            self.selected_item_on_canvas = None
            self.current_selection_type = None
            self.disable_text_properties_panel()
            self.enable_disable_alignment_buttons(False) 

            self.update_canvas_dimensions() 
            self.update_bg_controls_state() 
            self.redraw_canvas() 
            messagebox.showinfo("Success", f"Configuration loaded from {filepath}")

        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to parse configuration file (invalid JSON): {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")

