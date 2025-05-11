import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, colorchooser
from tkinter import filedialog
import json
import datetime

class FieldFrame(tk.Frame):
    def __init__(self, parent, remove_callback=None):
        super().__init__(parent, bd=1, relief=tk.RIDGE, padx=5, pady=5)
        self.remove_callback = remove_callback
        
        tk.Label(self, text="Field Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = tk.Entry(self, width=30)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=2)
        
        tk.Label(self, text="Field Value:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.value_text = scrolledtext.ScrolledText(self, width=30, height=3)
        self.value_text.grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=2)
        
        self.inline_var = tk.BooleanVar(value=True)
        self.inline_check = tk.Checkbutton(self, text="Inline", variable=self.inline_var)
        self.inline_check.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        if remove_callback:
            tk.Button(self, text="Remove Field", command=self.remove).grid(row=2, column=2, sticky=tk.E, pady=2)
    
    def remove(self):
        if self.remove_callback:
            self.remove_callback(self)
    
    def get_data(self):
        return {
            "name": self.name_entry.get(),
            "value": self.value_text.get("1.0", tk.END).strip(),
            "inline": self.inline_var.get()
        }

class EmbedBuilder(tk.Tk):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.title("Discord Embed Builder")
        self.geometry("640x700")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Main")
        
        self.author_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.author_frame, text="Author")
        
        self.image_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.image_frame, text="Images")
        
        self.footer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.footer_frame, text="Footer")
        
        self.fields_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fields_frame, text="Fields")
        
        
        self._setup_main_tab()
        self._setup_author_tab()
        self._setup_image_tab()
        self._setup_footer_tab()
        self._setup_fields_tab()
        
        self.submit_button = tk.Button(self, text="Send Embed", command=self.on_submit, bg="#7289DA", fg="white", padx=20, pady=10)
        self.submit_button.pack(pady=10)
        
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Export JSON", command=self.export_json).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Import JSON", command=self.import_json).pack(side=tk.LEFT, padx=5)
        
        self.configure(bg="#36393F")  # Discord dark theme
        self.fields = []

    def _setup_main_tab(self):
        frame = self.main_frame
        
        tk.Label(frame, text="Message Content (Optional)").pack(anchor=tk.W, pady=(10, 2))
        self.content_entry = tk.Entry(frame, width=70)
        self.content_entry.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Embed Title").pack(anchor=tk.W, pady=(10, 2))
        self.title_entry = tk.Entry(frame, width=70)
        self.title_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(frame, text="Title URL (Optional)").pack(anchor=tk.W, pady=(5, 2))
        self.url_entry = tk.Entry(frame, width=70)
        self.url_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(frame, text="Embed Description").pack(anchor=tk.W, pady=(10, 2))
        self.description_text = scrolledtext.ScrolledText(frame, width=70, height=10)
        self.description_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        color_frame = tk.Frame(frame)
        color_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(color_frame, text="Embed Color").pack(side=tk.LEFT, padx=(0, 10))
        self.color_entry = tk.Entry(color_frame, width=10)
        self.color_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.color_preview = tk.Label(color_frame, text="   ", bg="#7289DA", width=3)
        self.color_preview.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(color_frame, text="Pick Color", command=self.pick_color).pack(side=tk.LEFT)
        
        timestamp_frame = tk.Frame(frame)
        timestamp_frame.pack(fill=tk.X, pady=10)
        
        self.timestamp_var = tk.BooleanVar(value=False)
        self.timestamp_check = tk.Checkbutton(timestamp_frame, text="Include Current Timestamp", 
                                             variable=self.timestamp_var)
        self.timestamp_check.pack(side=tk.LEFT)

    def _setup_author_tab(self):
        frame = self.author_frame
        
        tk.Label(frame, text="Author Name").pack(anchor=tk.W, pady=(10, 2))
        self.author_name_entry = tk.Entry(frame, width=70)
        self.author_name_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(frame, text="Author URL (Optional)").pack(anchor=tk.W, pady=(5, 2))
        self.author_url_entry = tk.Entry(frame, width=70)
        self.author_url_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(frame, text="Author Icon URL (Optional)").pack(anchor=tk.W, pady=(5, 2))
        self.author_icon_entry = tk.Entry(frame, width=70)
        self.author_icon_entry.pack(fill=tk.X, pady=(0, 5))

    def _setup_image_tab(self):
        frame = self.image_frame
        
        tk.Label(frame, text="Main Image URL (Optional)").pack(anchor=tk.W, pady=(10, 2))
        self.image_url_entry = tk.Entry(frame, width=70)
        self.image_url_entry.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(frame, text="Thumbnail URL (Optional)").pack(anchor=tk.W, pady=(10, 2))
        self.thumbnail_url_entry = tk.Entry(frame, width=70)
        self.thumbnail_url_entry.pack(fill=tk.X, pady=(0, 10))

    def _setup_footer_tab(self):
        frame = self.footer_frame
        
        tk.Label(frame, text="Footer Text (Optional)").pack(anchor=tk.W, pady=(10, 2))
        self.footer_text_entry = tk.Entry(frame, width=70)
        self.footer_text_entry.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(frame, text="Footer Icon URL (Optional)").pack(anchor=tk.W, pady=(5, 2))
        self.footer_icon_entry = tk.Entry(frame, width=70)
        self.footer_icon_entry.pack(fill=tk.X, pady=(0, 5))

    def _setup_fields_tab(self):
        frame = self.fields_frame
        
        self.fields_container = tk.Frame(frame)
        self.fields_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Button(frame, text="Add Field", command=self.add_field).pack(pady=10)

    def add_field(self):
        field = FieldFrame(self.fields_container, remove_callback=self.remove_field)
        field.pack(fill=tk.X, pady=5)
        self.fields.append(field)
        
    def remove_field(self, field):
        if field in self.fields:
            self.fields.remove(field)
            field.destroy()

    def pick_color(self):
        color = colorchooser.askcolor(title="Choose Embed Color", initialcolor="#7289DA")
        if color[1]:  
            hex_color = color[1][1:]  
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, hex_color)
            self.color_preview.config(bg=color[1])

    def export_json(self):
        embed_data = self.collect_data()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Embed Configuration"
        )
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(embed_data, f, indent=2)
            messagebox.showinfo("Export Successful", f"Embed configuration saved to {file_path}")

    def import_json(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Embed Configuration"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    embed_data = json.load(f)
                self.load_data(embed_data)
                messagebox.showinfo("Import Successful", "Embed configuration loaded successfully")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import configuration: {str(e)}")

    def load_data(self, embed_data):
        self.title_entry.delete(0, tk.END)
        self.url_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.content_entry.delete(0, tk.END)
        self.color_entry.delete(0, tk.END)
        self.author_name_entry.delete(0, tk.END)
        self.author_url_entry.delete(0, tk.END)
        self.author_icon_entry.delete(0, tk.END)
        self.image_url_entry.delete(0, tk.END)
        self.thumbnail_url_entry.delete(0, tk.END)
        self.footer_text_entry.delete(0, tk.END)
        self.footer_icon_entry.delete(0, tk.END)
        
        for field in self.fields:
            field.destroy()
        self.fields = []
        
        if "content" in embed_data:
            self.content_entry.insert(0, embed_data["content"])
        
        if "embed" in embed_data:
            embed = embed_data["embed"]
            
            if "title" in embed:
                self.title_entry.insert(0, embed["title"])
            if "url" in embed:
                self.url_entry.insert(0, embed["url"])
            if "description" in embed:
                self.description_text.insert("1.0", embed["description"])
            if "color" in embed:
                hex_color = format(embed["color"], 'x')
                self.color_entry.insert(0, hex_color)
                self.color_preview.config(bg=f"#{hex_color}")
            
            if "author" in embed:
                author = embed["author"]
                if "name" in author:
                    self.author_name_entry.insert(0, author["name"])
                if "url" in author:
                    self.author_url_entry.insert(0, author["url"])
                if "icon_url" in author:
                    self.author_icon_entry.insert(0, author["icon_url"])
            
            if "image" in embed and "url" in embed["image"]:
                self.image_url_entry.insert(0, embed["image"]["url"])
            if "thumbnail" in embed and "url" in embed["thumbnail"]:
                self.thumbnail_url_entry.insert(0, embed["thumbnail"]["url"])
            
            if "footer" in embed:
                footer = embed["footer"]
                if "text" in footer:
                    self.footer_text_entry.insert(0, footer["text"])
                if "icon_url" in footer:
                    self.footer_icon_entry.insert(0, footer["icon_url"])
            
            if "fields" in embed:
                for field_data in embed["fields"]:
                    self.add_field()
                    field = self.fields[-1]
                    field.name_entry.insert(0, field_data.get("name", ""))
                    field.value_text.insert("1.0", field_data.get("value", ""))
                    field.inline_var.set(field_data.get("inline", True))

    def collect_data(self):
        embed_data = {
            "content": self.content_entry.get(),
            "embed": {
                "title": self.title_entry.get(),
                "description": self.description_text.get("1.0", tk.END).strip(),
            }
        }
        
        if self.url_entry.get():
            embed_data["embed"]["url"] = self.url_entry.get()
            
        if self.color_entry.get():
            try:
                color_int = int(self.color_entry.get(), 16)
                embed_data["embed"]["color"] = color_int
            except ValueError:
                messagebox.showwarning("Invalid Color", "Color must be a valid hex value (without #)")
        
        author_name = self.author_name_entry.get()
        if author_name:
            author_data = {"name": author_name}
            
            if self.author_url_entry.get():
                author_data["url"] = self.author_url_entry.get()
                
            if self.author_icon_entry.get():
                author_data["icon_url"] = self.author_icon_entry.get()
                
            embed_data["embed"]["author"] = author_data
        
        if self.image_url_entry.get():
            embed_data["embed"]["image"] = {"url": self.image_url_entry.get()}
            
        if self.thumbnail_url_entry.get():
            embed_data["embed"]["thumbnail"] = {"url": self.thumbnail_url_entry.get()}
        
        footer_text = self.footer_text_entry.get()
        if footer_text:
            footer_data = {"text": footer_text}
            
            if self.footer_icon_entry.get():
                footer_data["icon_url"] = self.footer_icon_entry.get()
                
            embed_data["embed"]["footer"] = footer_data
        
        if self.timestamp_var.get():
            embed_data["embed"]["timestamp"] = datetime.datetime.utcnow().isoformat()
        
        if self.fields:
            fields_data = []
            for field in self.fields:
                field_data = field.get_data()
                if field_data["name"] and field_data["value"]:  
                    fields_data.append(field_data)
            
            if fields_data:
                embed_data["embed"]["fields"] = fields_data
        
        return embed_data

    def on_submit(self):
        try:
            embed_data = self.collect_data()
            self.destroy()
            self.callback(embed_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create embed: {str(e)}")


