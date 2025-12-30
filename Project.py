import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenCV Image Editor")
        self.root.geometry("1200x800")
        
        # Image storage
        self.original_image = None
        self.current_image = None
        self.second_image = None
        self.history = []
        self.history_index = -1
        
        # Selection rectangle
        self.selection_active = False
        self.selection_start = None
        self.selection_end = None
        self.selection_rect = None
        self.selection_coords = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configure root window
        self.root.configure(bg='#2b2b2b')
        
        # Menu Bar
        menubar = tk.Menu(self.root, bg='#2b2b2b', fg='white', 
                         activebackground='#404040', activeforeground='white')
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2b2b2b', fg='white',
                           activebackground='#404040', activeforeground='white')
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="🖼️  Open Image         Ctrl+O", command=self.open_image)
        file_menu.add_command(label="💾  Save Image         Ctrl+S", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="❌  Exit", command=self.root.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#2b2b2b', fg='white',
                           activebackground='#404040', activeforeground='white')
        menubar.add_cascade(label="✏️ Edit", menu=edit_menu)
        edit_menu.add_command(label="↶  Undo               Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="↷  Redo               Ctrl+Y", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="🔄  Reset to Original", command=self.reset_image)
        
        # Top Toolbar
        toolbar = tk.Frame(self.root, bg='#3c3c3c', height=60)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)
        
        btn_style = {'bg': '#4a90e2', 'fg': 'white', 'font': ('Arial', 10, 'bold'),
                     'relief': tk.FLAT, 'padx': 15, 'pady': 8, 'cursor': 'hand2'}
        
        tk.Button(toolbar, text="📂 Open", command=self.open_image, **btn_style).pack(
            side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="💾 Save", command=self.save_image, **btn_style).pack(
            side=tk.LEFT, padx=5, pady=10)
        
        tk.Frame(toolbar, bg='#555555', width=2).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        tk.Button(toolbar, text="↶ Undo", command=self.undo, **btn_style).pack(
            side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="↷ Redo", command=self.redo, **btn_style).pack(
            side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="🔄 Reset", command=self.reset_image, **btn_style).pack(
            side=tk.LEFT, padx=5, pady=10)
        
        tk.Frame(toolbar, bg='#555555', width=2).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Selection tools
        self.selection_btn = tk.Button(toolbar, text="🔲 Select Area", 
                                       command=self.toggle_selection_mode, 
                                       **btn_style)
        self.selection_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        tk.Button(toolbar, text="✂️ Clear Selection", command=self.clear_selection, 
                 **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        
        tk.Frame(toolbar, bg='#555555', width=2).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Image info label
        self.img_info_label = tk.Label(toolbar, text="No image loaded", 
                                       bg='#3c3c3c', fg='#aaaaaa', 
                                       font=('Arial', 9))
        self.img_info_label.pack(side=tk.LEFT, padx=15)
        
        # Selection info label
        self.selection_info_label = tk.Label(toolbar, text="", 
                                             bg='#3c3c3c', fg='#00ff00', 
                                             font=('Arial', 9, 'bold'))
        self.selection_info_label.pack(side=tk.LEFT, padx=10)
        
        # Main Frame Layout
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Left Panel - Tools
        left_panel = tk.Frame(main_frame, width=280, bg='#353535', 
                             relief=tk.FLAT, borderwidth=0)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=0)
        left_panel.pack_propagate(False)
        
        # Tools Header
        header_frame = tk.Frame(left_panel, bg='#2b2b2b', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🎨 Tools & Effects", 
                font=("Segoe UI", 14, "bold"), bg='#2b2b2b', fg='white').pack(pady=15)
        
        # Create custom style for Notebook
        style = ttk.Style()
        style.theme_create("dark", parent="alt", settings={
            "TNotebook": {
                "configure": {"background": "#353535", "borderwidth": 0}
            },
            "TNotebook.Tab": {
                "configure": {
                    "background": "#2b2b2b",
                    "foreground": "#aaaaaa",
                    "padding": [20, 10],
                    "font": ('Segoe UI', 9, 'bold')
                },
                "map": {
                    "background": [("selected", "#4a90e2")],
                    "foreground": [("selected", "white")],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            }
        })
        style.theme_use("dark")
        
        # Create Notebook
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Filters Tab
        filters_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(filters_frame, text="🎭 Filters")
        self.create_filters_panel(filters_frame)
        
        # Adjustments Tab
        adjustments_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(adjustments_frame, text="⚙️ Adjust")
        self.create_adjustments_panel(adjustments_frame)
        
        # Transform Tab
        transform_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(transform_frame, text="🔄 Transform")
        self.create_transform_panel(transform_frame)
        
        # Effects Tab
        effects_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(effects_frame, text="✨ Effects")
        self.create_effects_panel(effects_frame)
        
        # Right Panel - Image Display
        right_panel = tk.Frame(main_frame, bg='#2b2b2b', relief=tk.FLAT)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas frame
        canvas_frame = tk.Frame(right_panel, bg='#1e1e1e', relief=tk.SUNKEN, borderwidth=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for image display
        self.canvas = tk.Canvas(canvas_frame, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind('<Configure>', lambda e: self.display_image())
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Placeholder text
        self.canvas.create_text(400, 300, 
                               text="📷\n\nOpen an image to start editing\n(File > Open Image)",
                               fill='#555555', font=('Segoe UI', 16), 
                               tags='placeholder', justify=tk.CENTER)
        
        # Status Bar
        status_frame = tk.Frame(self.root, bg='#2b2b2b', height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_bar = tk.Label(status_frame, text="⚡ Ready  |  No image loaded", 
                                   bg='#2b2b2b', fg='#aaaaaa', 
                                   anchor=tk.W, font=('Segoe UI', 9), padx=10)
        self.status_bar.pack(fill=tk.X, pady=5)
        
    def create_section_header(self, parent, text):
        """Create a styled section header"""
        header_frame = tk.Frame(parent, bg='#2b2b2b', height=35)
        header_frame.pack(fill=tk.X, pady=(15, 10), padx=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=text, bg='#2b2b2b', fg='white',
                font=('Segoe UI', 11, 'bold')).pack(pady=8, padx=10, anchor=tk.W)
        
    def create_filters_panel(self, parent):
        """Only Gaussian, Median, and Mean Blur"""
        parent.configure(bg='#353535')
        
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Blur Filters
        self.create_section_header(container, "🌫️ Blur Filters")
        
        btn_style = {'bg': '#4a90e2', 'fg': 'white', 'font': ('Segoe UI', 10),
                     'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#357abd'}
        
        tk.Button(container, text="Gaussian Blur", command=self.apply_gaussian_blur,
                 width=22, **btn_style).pack(pady=5)
        
        tk.Button(container, text="Median Blur", command=self.apply_median_blur,
                 width=22, **btn_style).pack(pady=5)
        
        tk.Button(container, text="Mean (Box) Blur", command=self.apply_mean_blur,
                 width=22, **btn_style).pack(pady=5)
        
        # Kernel size slider
        slider_frame = tk.Frame(container, bg='#353535')
        slider_frame.pack(pady=10, fill=tk.X)
        
        tk.Label(slider_frame, text="Kernel Size:", bg='#353535', 
                fg='#cccccc', font=('Segoe UI', 9)).pack(anchor=tk.W)
        
        self.blur_scale = tk.Scale(slider_frame, from_=1, to=51, orient=tk.HORIZONTAL,
                                   resolution=2, bg='#353535', fg='#cccccc',
                                   troughcolor='#2b2b2b', highlightthickness=0,
                                   activebackground='#4a90e2', font=('Segoe UI', 8))
        self.blur_scale.set(5)
        self.blur_scale.pack(fill=tk.X)

    def create_adjustments_panel(self, parent):
        """Brightness, contrast, etc."""
        parent.configure(bg='#353535')
        
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Brightness
        self.create_section_header(container, "☀️ Brightness")
        
        brightness_frame = tk.Frame(container, bg='#353535')
        brightness_frame.pack(pady=5, fill=tk.X)
        
        self.brightness_value = tk.Label(brightness_frame, text="0", 
                                         bg='#353535', fg='#4a90e2',
                                         font=('Segoe UI', 11, 'bold'))
        self.brightness_value.pack(anchor=tk.E)
        
        self.brightness_scale = tk.Scale(brightness_frame, from_=-100, to=100, 
                                        orient=tk.HORIZONTAL, bg='#353535', 
                                        fg='#cccccc', troughcolor='#2b2b2b',
                                        highlightthickness=0, activebackground='#4a90e2',
                                        showvalue=0, command=self.update_brightness_label)
        self.brightness_scale.set(0)
        self.brightness_scale.pack(fill=tk.X)
        
        # Contrast
        self.create_section_header(container, "🔆 Contrast")
        
        contrast_frame = tk.Frame(container, bg='#353535')
        contrast_frame.pack(pady=5, fill=tk.X)
        
        self.contrast_value = tk.Label(contrast_frame, text="1.0", 
                                       bg='#353535', fg='#4a90e2',
                                       font=('Segoe UI', 11, 'bold'))
        self.contrast_value.pack(anchor=tk.E)
        
        self.contrast_scale = tk.Scale(contrast_frame, from_=0.5, to=3.0, 
                                      orient=tk.HORIZONTAL, resolution=0.1,
                                      bg='#353535', fg='#cccccc',
                                      troughcolor='#2b2b2b', highlightthickness=0,
                                      activebackground='#4a90e2', showvalue=0,
                                      command=self.update_contrast_label)
        self.contrast_scale.set(1.0)
        self.contrast_scale.pack(fill=tk.X)
        
        # Apply button
        tk.Frame(container, bg='#353535', height=20).pack()
        
        btn_style = {'bg': '#27ae60', 'fg': 'white', 'font': ('Segoe UI', 11, 'bold'),
                     'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#1e8449'}
        
        tk.Button(container, text="✓ Apply Adjustments", 
                 command=self.apply_brightness_contrast,
                 width=20, height=2, **btn_style).pack(pady=10)
    
    def update_brightness_label(self, value):
        self.brightness_value.config(text=f"{int(float(value))}")
    
    def update_contrast_label(self, value):
        self.contrast_value.config(text=f"{float(value):.1f}")
        
    def create_transform_panel(self, parent):
        """Only Rotation (Flip removed)"""
        parent.configure(bg='#353535')
        
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Rotation only
        self.create_section_header(container, "🔄 Rotation")
        
        btn_style = {'bg': '#3498db', 'fg': 'white', 'font': ('Segoe UI', 10),
                     'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#2980b9'}
        
        tk.Button(container, text="↻ Rotate 90° CW", command=lambda: self.rotate_image(90),
                 width=22, **btn_style).pack(pady=5)
        tk.Button(container, text="↺ Rotate 90° CCW", command=lambda: self.rotate_image(-90),
                 width=22, **btn_style).pack(pady=5)
        tk.Button(container, text="⟲ Rotate 180°", command=lambda: self.rotate_image(180),
                 width=22, **btn_style).pack(pady=5)
        
    def create_effects_panel(self, parent):
        """Edge detection, sharpening, etc."""
        parent.configure(bg='#353535')
        
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Edge Detection
        self.create_section_header(container, "🔍 Edge Detection")
        
        edge_btn_style = {'bg': '#16a085', 'fg': 'white', 'font': ('Segoe UI', 10),
                         'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#138d75'}
        
        tk.Button(container, text="Canny Edge", command=self.apply_canny,
                 width=22, **edge_btn_style).pack(pady=5)
        tk.Button(container, text="Sobel Edge", command=self.apply_sobel,
                 width=22, **edge_btn_style).pack(pady=5)
        
        # Enhancement
        self.create_section_header(container, "✨ Enhancement")
        
        enhance_btn_style = {'bg': '#e74c3c', 'fg': 'white', 'font': ('Segoe UI', 10),
                            'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#c0392b'}
        
        tk.Button(container, text="Sharpen", command=self.apply_sharpen,
                 width=22, **enhance_btn_style).pack(pady=5)
        tk.Button(container, text="Emboss", command=self.apply_emboss,
                 width=22, **enhance_btn_style).pack(pady=5)
    
    # ========== Selection Functions ==========
    
    def toggle_selection_mode(self):
        """Toggle selection mode on/off"""
        self.selection_active = not self.selection_active
        if self.selection_active:
            self.selection_btn.config(bg='#27ae60', text='🔲 Selection ON')
            self.update_status("🔲 Selection mode: Click and drag to select area")
        else:
            self.selection_btn.config(bg='#4a90e2', text='🔲 Select Area')
            self.update_status("Selection mode disabled")
    
    def clear_selection(self):
        """Clear the current selection"""
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
        self.selection_start = None
        self.selection_end = None
        self.selection_coords = None
        self.selection_info_label.config(text="")
        self.update_status("✓ Selection cleared")
        self.display_image()
    
    def on_mouse_down(self, event):
        """Handle mouse button press"""
        if not self.selection_active or self.current_image is None:
            return
        
        self.selection_start = (event.x, event.y)
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag"""
        if not self.selection_active or self.selection_start is None:
            return
        
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y
        
        # Draw selection rectangle
        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='#00ff00',
            width=2,
            dash=(5, 5)
        )
    
    def on_mouse_up(self, event):
        """Handle mouse button release"""
        if not self.selection_active or self.selection_start is None:
            return
        
        self.selection_end = (event.x, event.y)
        
        # Convert canvas coordinates to image coordinates
        self.convert_selection_to_image_coords()
        
        if self.selection_coords:
            x1, y1, x2, y2 = self.selection_coords
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            self.update_status(f"✓ Selected region: {w}×{h}px")
            self.selection_info_label.config(text=f"🔲 Selection: {w}×{h}px")
        else:
            self.selection_info_label.config(text="")
    
    def convert_selection_to_image_coords(self):
        """Convert canvas selection coordinates to actual image pixel coordinates"""
        if self.current_image is None or self.selection_start is None or self.selection_end is None:
            return
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Get image dimensions
        img_h, img_w = self.current_image.shape[:2]
        
        # Calculate scale and offset
        scale = min(canvas_width/img_w, canvas_height/img_h, 1.0)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        offset_x = (canvas_width - new_w) // 2
        offset_y = (canvas_height - new_h) // 2
        
        # Convert selection coordinates
        x1_canvas, y1_canvas = self.selection_start
        x2_canvas, y2_canvas = self.selection_end
        
        x1_img = int((x1_canvas - offset_x) / scale)
        y1_img = int((y1_canvas - offset_y) / scale)
        x2_img = int((x2_canvas - offset_x) / scale)
        y2_img = int((y2_canvas - offset_y) / scale)
        
        # Ensure coordinates are within image bounds
        x1_img = max(0, min(x1_img, img_w))
        y1_img = max(0, min(y1_img, img_h))
        x2_img = max(0, min(x2_img, img_w))
        y2_img = max(0, min(y2_img, img_h))
        
        # Ensure x1 < x2 and y1 < y2
        if x1_img > x2_img:
            x1_img, x2_img = x2_img, x1_img
        if y1_img > y2_img:
            y1_img, y2_img = y2_img, y1_img
        
        self.selection_coords = (x1_img, y1_img, x2_img, y2_img)
    
    def apply_to_selection(self, operation_func):
        """Apply an operation only to the selected region"""
        if self.selection_coords is None:
            return operation_func(self.current_image)
        
        x1, y1, x2, y2 = self.selection_coords
        selected_region = self.current_image[y1:y2, x1:x2].copy()
        processed_region = operation_func(selected_region)
        result = self.current_image.copy()
        result[y1:y2, x1:x2] = processed_region
        return result
    
    # ========== File Operations ==========
    
    def open_image(self):
        """Open and load an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                      ("All Files", "*.*")]
        )
        
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.current_image = self.original_image.copy()
                self.history = [self.current_image.copy()]
                self.history_index = 0
                self.canvas.delete('placeholder')
                self.display_image()
                
                h, w = self.current_image.shape[:2]
                filename = file_path.split('/')[-1]
                self.img_info_label.config(text=f"📷 {filename} ({w}x{h}px)")
                self.update_status(f"✓ Loaded: {filename}")
            else:
                messagebox.showerror("Error", "Failed to load image")
    
    def save_image(self):
        """Save the current image"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), 
                      ("BMP", "*.bmp"), ("All Files", "*.*")]
        )
        
        if file_path:
            cv2.imwrite(file_path, self.current_image)
            filename = file_path.split('/')[-1]
            self.update_status(f"💾 Saved: {filename}")
            messagebox.showinfo("Success", f"Image saved successfully!\n\n{filename}")
    
    # ========== History Management ==========
    
    def add_to_history(self):
        """Add current state to history for undo/redo"""
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_image.copy())
        self.history_index += 1
        if len(self.history) > 20:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        """Undo last operation"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image()
            self.update_status("↶ Undo applied")
        else:
            self.update_status("⚠️ No more actions to undo")
    
    def redo(self):
        """Redo operation"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image()
            self.update_status("↷ Redo applied")
        else:
            self.update_status("⚠️ No more actions to redo")
    
    def reset_image(self):
        """Reset to original image"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.add_to_history()
            self.display_image()
            self.update_status("🔄 Image reset to original")
        else:
            messagebox.showwarning("Warning", "No image loaded")
    
    # ========== Image Processing Functions ==========
    
    def apply_gaussian_blur(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        
        kernel_size = self.blur_scale.get()
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        def blur_operation(img):
            return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        
        self.current_image = self.apply_to_selection(blur_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Gaussian Blur applied{region_text} (kernel: {kernel_size}x{kernel_size})")
    
    def apply_median_blur(self):
        if self.current_image is None:
            return
        
        kernel_size = self.blur_scale.get()
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        def blur_operation(img):
            return cv2.medianBlur(img, kernel_size)
        
        self.current_image = self.apply_to_selection(blur_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Median Blur applied{region_text} (kernel: {kernel_size})")
    
    def apply_mean_blur(self):
        """Apply Mean (Box) Blur"""
        if self.current_image is None:
            return
        
        kernel_size = self.blur_scale.get()
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        def blur_operation(img):
            return cv2.blur(img, (kernel_size, kernel_size))
        
        self.current_image = self.apply_to_selection(blur_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Mean Blur applied{region_text} (kernel: {kernel_size}x{kernel_size})")
    
    def apply_brightness_contrast(self):
        if self.current_image is None:
            return
        
        brightness = self.brightness_scale.get()
        contrast = self.contrast_scale.get()
        
        def adjust_operation(img):
            return cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)
        
        self.current_image = self.apply_to_selection(adjust_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"Adjusted{region_text}: Brightness={brightness}, Contrast={contrast}")
    
    def rotate_image(self, angle):
        if self.current_image is None:
            return
        
        if angle == 90:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_CLOCKWISE)
        elif angle == -90:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif angle == 180:
            self.current_image = cv2.rotate(self.current_image, cv2.ROTATE_180)
        
        self.add_to_history()
        self.display_image()
        self.update_status(f"Rotated {angle}°")
    
    def apply_canny(self):
        if self.current_image is None:
            return
        
        def canny_operation(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        self.current_image = self.apply_to_selection(canny_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Canny edge detection applied{region_text}")
    
    def apply_sobel(self):
        if self.current_image is None:
            return
        
        def sobel_operation(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel = np.sqrt(sobelx**2 + sobely**2)
            sobel = np.uint8(np.clip(sobel, 0, 255))
            return cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
        
        self.current_image = self.apply_to_selection(sobel_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Sobel edge detection applied{region_text}")
    
    def apply_sharpen(self):
        if self.current_image is None:
            return
        
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        
        def sharpen_operation(img):
            return cv2.filter2D(img, -1, kernel)
        
        self.current_image = self.apply_to_selection(sharpen_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Sharpen applied{region_text}")
    
    def apply_emboss(self):
        if self.current_image is None:
            return
        
        kernel = np.array([[-2, -1, 0],
                          [-1,  1, 1],
                          [ 0,  1, 2]])
        
        def emboss_operation(img):
            result = cv2.filter2D(img, -1, kernel)
            return cv2.convertScaleAbs(result)
        
        self.current_image = self.apply_to_selection(emboss_operation)
        self.add_to_history()
        self.display_image()
        
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Emboss effect applied{region_text}")
    
    # ========== Display Functions ==========
    
    def display_image(self):
        if self.current_image is None:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 600
        
        img_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]
        
        scale = min(canvas_width/w, canvas_height/h, 1.0)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        img_resized = cv2.resize(img_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        img_pil = Image.fromarray(img_resized)
        self.photo = ImageTk.PhotoImage(img_pil)
        
        self.canvas.delete("all")
        x = (canvas_width - new_w) // 2
        y = (canvas_height - new_h) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo)
        
        if self.selection_rect and self.selection_start and self.selection_end:
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            self.selection_rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='#00ff00',
                width=2,
                dash=(5, 5)
            )
    
    def update_status(self, message):
        if self.current_image is not None:
            h, w = self.current_image.shape[:2]
            self.status_bar.config(text=f"{message}  |  Size: {w}×{h}px")
        else:
            self.status_bar.config(text=message)

# ========== Main Application ==========

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    
    root.bind('<Control-o>', lambda e: app.open_image())
    root.bind('<Control-s>', lambda e: app.save_image())
    root.bind('<Control-z>', lambda e: app.undo())
    root.bind('<Control-y>', lambda e: app.redo())
    
    root.mainloop()