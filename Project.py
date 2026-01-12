import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ImageEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("SCSV3213 - Image Editor")
        self.root.geometry("1200x880")
        
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
        self.root.configure(bg='#2b2b2b')
        
        # Menu Bar
        menubar = tk.Menu(self.root, bg='#2b2b2b', fg='white', 
                         activebackground='#404040', activeforeground='white')
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg='#2b2b2b', fg='white',
                           activebackground='#404040', activeforeground='white')
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="🖼️  Open Image         Ctrl+O", command=self.open_image)
        file_menu.add_command(label="💾  Save Image         Ctrl+S", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="❌  Exit", command=self.root.quit)
        
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
        
        self.selection_btn = tk.Button(toolbar, text="🔲 Select Area", 
                                       command=self.toggle_selection_mode, 
                                       **btn_style)
        self.selection_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        tk.Button(toolbar, text="✂️ Clear Selection", command=self.clear_selection, 
                 **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        
        tk.Frame(toolbar, bg='#555555', width=2).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.img_info_label = tk.Label(toolbar, text="No image loaded", 
                                       bg='#3c3c3c', fg='#aaaaaa', 
                                       font=('Arial', 9))
        self.img_info_label.pack(side=tk.LEFT, padx=15)
        
        self.selection_info_label = tk.Label(toolbar, text="", 
                                             bg='#3c3c3c', fg='#00ff00', 
                                             font=('Arial', 9, 'bold'))
        self.selection_info_label.pack(side=tk.LEFT, padx=10)
        
        # Main Frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Left Panel
        left_panel = tk.Frame(main_frame, width=280, bg='#353535', relief=tk.FLAT, borderwidth=0)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=0)
        left_panel.pack_propagate(False)
        
        header_frame = tk.Frame(left_panel, bg='#2b2b2b', height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text="🎨 Tools & Effects", 
                font=("Segoe UI", 14, "bold"), bg='#2b2b2b', fg='white').pack(pady=15)
        
        # Notebook Style
        style = ttk.Style()
        style.theme_create("dark", parent="alt", settings={
            "TNotebook": {"configure": {"background": "#353535", "borderwidth": 0}},
            "TNotebook.Tab": {
                "configure": {
                    "background": "#2b2b2b",
                    "foreground": "#aaaaaa",
                    "padding": [12, 8],
                    "font": ('Segoe UI', 9, 'bold'),
                    "width": 15,
                },
                "map": {
                    "background": [("selected", "#4a90e2")],
                    "foreground": [("selected", "white")],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            }
        })
        style.theme_use("dark")
        
        notebook = ttk.Notebook(left_panel)
        notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Existing Tabs
        filters_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(filters_frame, text="Filters")
        self.create_filters_panel(filters_frame)
        
        adjustments_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(adjustments_frame, text="Adjustments")
        self.create_adjustments_panel(adjustments_frame)
        
        edge_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(edge_frame, text="Edge Detection")
        self.create_edge_panel(edge_frame)
        
        thresh_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(thresh_frame, text="Thresholding")
        self.create_threshold_panel(thresh_frame)
        
        logic_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(logic_frame, text="Logic Operations")
        self.create_logic_panel(logic_frame)
        
        # Halftoning Tab
        halftone_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(halftone_frame, text="Halftoning")
        self.create_halftoning_panel(halftone_frame)
        
        # Neighborhood Tab
        nb_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(nb_frame, text="Neighborhood")
        self.create_neighborhood_panel(nb_frame)
        
        # Frequency Domain Tab
        freq_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(freq_frame, text="Frequency")
        self.create_frequency_panel(freq_frame)
        
        # Segmentation Tab (NEW)
        seg_frame = tk.Frame(notebook, bg='#353535')
        notebook.add(seg_frame, text="Segmentation")
        self.create_segmentation_panel(seg_frame)
        
        # Right Panel - Display
        right_panel = tk.Frame(main_frame, bg='#2b2b2b', relief=tk.FLAT)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas_frame = tk.Frame(right_panel, bg='#1e1e1e', relief=tk.SUNKEN, borderwidth=1)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Histogram
        hist_frame = tk.Frame(right_panel, bg='#2b2b2b', height=140)
        hist_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))
        hist_frame.pack_propagate(False)
        self.hist_fig = Figure(figsize=(6, 1.4), facecolor='#2b2b2b', dpi=100)
        self.hist_ax = self.hist_fig.add_subplot(111, facecolor='#3c3c3c')
        for spine in self.hist_ax.spines.values():
            spine.set_color('#555555')
        self.hist_ax.tick_params(colors='white', labelsize=8)
        self.hist_ax.set_xlim([0, 256])
        self.hist_ax.set_xticks([0, 64, 128, 192, 255])
        self.hist_ax.set_xlabel('Pixel Intensity', color='white', fontsize=9)
        self.hist_ax.grid(True, color='#444444', linestyle='--', linewidth=0.5)
        self.hist_canvas_agg = FigureCanvasTkAgg(self.hist_fig, hist_frame)
        self.hist_canvas_agg.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Bind Canvas Events
        self.canvas.bind('<Configure>', lambda e: self.display_image())
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        self.canvas.create_text(400, 250, 
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
        header_frame = tk.Frame(parent, bg='#2b2b2b', height=35)
        header_frame.pack(fill=tk.X, pady=(15, 10), padx=10)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text=text, bg='#2b2b2b', fg='white',
                font=('Segoe UI', 11, 'bold')).pack(pady=8, padx=10, anchor=tk.W)

    def create_section_status(self, parent, text):
        header_frame = tk.Frame(parent, bg='#2b2b2b', height=30)
        header_frame.pack(fill=tk.X, pady=(15, 8), padx=10)
        header_frame.pack_propagate(False)
        tk.Label(header_frame, text=text, bg='#2b2b2b', fg='#ffcc00',
                 font=('Segoe UI', 10, 'bold')).pack(pady=6, padx=10, anchor=tk.W)

    # ========== EXISTING PANELS ==========
    def create_filters_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.create_section_header(container, "Blur Filters")
        btn_style = {'bg': '#4a90e2', 'fg': 'white', 'font': ('Segoe UI', 10),
                     'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#357abd'}
        tk.Button(container, text="Gaussian Blur", command=self.apply_gaussian_blur,
                 width=22, **btn_style).pack(pady=5)
        tk.Button(container, text="Median Blur", command=self.apply_median_blur,
                 width=22, **btn_style).pack(pady=5)
        tk.Button(container, text="Mean (Box) Blur", command=self.apply_mean_blur,
                 width=22, **btn_style).pack(pady=5)
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
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.create_section_header(container, "Brightness")
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
        self.create_section_header(container, "Contrast")
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
        tk.Frame(container, bg='#353535', height=20).pack()
        btn_style = {'bg': '#27ae60', 'fg': 'white', 'font': ('Segoe UI', 11, 'bold'),
                     'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#1e8449'}
        tk.Button(container, text="✓ Apply Adjustments", 
                 command=self.apply_brightness_contrast,
                 width=20, height=2, **btn_style).pack(pady=10)
    
    def create_edge_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.create_section_header(container, "Laplacian Edge")
        edge_btn_style = {'bg': '#d35400', 'fg': 'white', 'font': ('Segoe UI', 10),
                         'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#c0392b'}
        tk.Button(container, text="Apply Laplacian", command=self.apply_laplacian_edge,
                 width=22, **edge_btn_style).pack(pady=5)
        tk.Label(container, text="Detects edges using 2nd derivative",
                 bg='#353535', fg='#bbbbbb', font=('Segoe UI', 8), justify=tk.CENTER).pack(pady=(10,0))
    
    def create_threshold_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.create_section_header(container, "Otsu Threshold")
        thresh_btn_style = {'bg': '#2c3e50', 'fg': 'white', 'font': ('Segoe UI', 10),
                           'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#1a252f'}
        tk.Button(container, text="RGBO: Otsu Threshold", command=self.apply_otsu_threshold,
                 width=22, **thresh_btn_style).pack(pady=5)
        tk.Label(container, text="Automatic binary segmentation\nBest threshold chosen by algorithm",
                 bg='#353535', fg='#bbbbbb', font=('Segoe UI', 8), justify=tk.CENTER).pack(pady=(10,0))
    
    def create_logic_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.create_section_header(container, "Second Image")
        btn_style = {'bg': '#9b59b6', 'fg': 'white', 'font': ('Segoe UI', 10),
                     'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#8e44ad'}
        tk.Button(container, text="Load Second Image", 
                  command=self.load_second_image,
                  width=22, **btn_style).pack(pady=5)
        self.second_img_label = tk.Label(container, text="No second image",
                                         bg='#353535', fg='#cccccc',
                                         font=('Segoe UI', 9), wraplength=200)
        self.second_img_label.pack(pady=5)
        self.create_section_status(container, "Logical Operations")
        logic_btn_style = {'bg': '#e67e22', 'fg': 'white', 'font': ('Segoe UI', 10),
                           'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#d35400'}
        tk.Button(container, text="AND", command=lambda: self.apply_logic_operation('AND'),
                  width=22, **logic_btn_style).pack(pady=4)
        tk.Button(container, text="OR",  command=lambda: self.apply_logic_operation('OR'),
                  width=22, **logic_btn_style).pack(pady=4)
        tk.Button(container, text="XOR", command=lambda: self.apply_logic_operation('XOR'),
                  width=22, **logic_btn_style).pack(pady=4)

    # ========== HALFTONING ==========
    def create_halftoning_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.create_section_header(container, "Halftoning Methods")
        self.halftone_method = tk.StringVar(value="patterning")
        rb_style = {'bg': '#353535', 'fg': '#cccccc', 'selectcolor': '#2b2b2b',
                    'font': ('Segoe UI', 10)}
        tk.Radiobutton(container, text="Patterning (2×2, 5 levels)", 
                       variable=self.halftone_method, value="patterning", **rb_style).pack(anchor=tk.W, pady=4)
        tk.Radiobutton(container, text="Dithering (2×2 matrix D₁)", 
                       variable=self.halftone_method, value="dithering", **rb_style).pack(anchor=tk.W, pady=4)
        btn_style = {'bg': '#8e44ad', 'fg': 'white', 'font': ('Segoe UI', 10, 'bold'),
                     'relief': tk.FLAT, 'cursor': 'hand2', 'activebackground': '#7d3c98'}
        tk.Button(container, text="🎨 Apply Halftoning", 
                  command=self.apply_halftoning,
                  width=22, **btn_style).pack(pady=15)
        tk.Label(container, text="Converts grayscale image\nto binary using halftoning",
                 bg='#353535', fg='#bbbbbb', font=('Segoe UI', 8), justify=tk.CENTER).pack(pady=(0,10))

    # ========== NEIGHBORHOOD ==========
    def create_neighborhood_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.create_section_header(container, "Linear Filters")
        
        mean_frame = tk.Frame(container, bg='#353535')
        mean_frame.pack(fill=tk.X, pady=5)
        tk.Label(mean_frame, text="Mean (Box) Kernel:", bg='#353535', fg='#cccccc',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        self.mean_kernel = tk.Scale(mean_frame, from_=3, to=31, orient=tk.HORIZONTAL,
                                    resolution=2, bg='#353535', fg='#cccccc',
                                    troughcolor='#2b2b2b', highlightthickness=0,
                                    activebackground='#4a90e2', font=('Segoe UI', 8))
        self.mean_kernel.set(5)
        self.mean_kernel.pack(fill=tk.X)
        tk.Button(container, text="Blur: Mean Filter", 
                  command=self.apply_mean_filter,
                  bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#1e8449').pack(pady=6)

        gauss_frame = tk.Frame(container, bg='#353535')
        gauss_frame.pack(fill=tk.X, pady=10)
        tk.Label(gauss_frame, text="Gaussian Kernel:", bg='#353535', fg='#cccccc',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        self.gauss_kernel = tk.Scale(gauss_frame, from_=3, to=31, orient=tk.HORIZONTAL,
                                     resolution=2, bg='#353535', fg='#cccccc',
                                     troughcolor='#2b2b2b', highlightthickness=0,
                                     activebackground='#4a90e2', font=('Segoe UI', 8))
        self.gauss_kernel.set(5)
        self.gauss_kernel.pack(fill=tk.X)
        tk.Label(gauss_frame, text="Sigma (σ):", bg='#353535', fg='#cccccc',
                 font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(8,0))
        self.gauss_sigma = tk.Scale(gauss_frame, from_=0.1, to=5.0, orient=tk.HORIZONTAL,
                                    resolution=0.1, bg='#353535', fg='#cccccc',
                                    troughcolor='#2b2b2b', highlightthickness=0,
                                    activebackground='#4a90e2', font=('Segoe UI', 8))
        self.gauss_sigma.set(1.0)
        self.gauss_sigma.pack(fill=tk.X)
        tk.Button(container, text="Blur: Gaussian", 
                  command=self.apply_gaussian_filter,
                  bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#1e8449').pack(pady=6)

        self.create_section_header(container, "Non-Linear Filters")
        tk.Label(container, text="Median Kernel (odd):", bg='#353535', fg='#cccccc',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        self.median_kernel = tk.Scale(container, from_=3, to=21, orient=tk.HORIZONTAL,
                                      resolution=2, bg='#353535', fg='#cccccc',
                                      troughcolor='#2b2b2b', highlightthickness=0,
                                      activebackground='#4a90e2', font=('Segoe UI', 8))
        self.median_kernel.set(5)
        self.median_kernel.pack(fill=tk.X, pady=(0,8))
        tk.Button(container, text="Noise: Median Filter", 
                  command=self.apply_median_filter,
                  bg='#d35400', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#c0392b').pack(pady=6)

        self.create_section_header(container, "Sharpening")
        tk.Button(container, text="Sharpen: Laplacian", 
                  command=self.apply_sharpen_laplacian,
                  bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#c0392b').pack(pady=5)
        tk.Button(container, text="Sharpen: Unsharp Mask", 
                  command=self.apply_unsharp_mask,
                  bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#c0392b').pack(pady=5)

    # ========== FREQUENCY DOMAIN ==========
    def create_frequency_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.create_section_header(container, "Fourier Spectrum")
        tk.Button(container, text="🔍 Show FFT Magnitude", 
                  command=self.show_fft_magnitude,
                  bg='#3498db', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#2980b9').pack(pady=6)

        self.create_section_header(container, "Ideal Filters")
        
        tk.Label(container, text="Cutoff Radius (D₀):", bg='#353535', fg='#cccccc',
                 font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(10,0))
        self.cutoff_scale = tk.Scale(container, from_=1, to=150, orient=tk.HORIZONTAL,
                                     resolution=1, bg='#353535', fg='#cccccc',
                                     troughcolor='#2b2b2b', highlightthickness=0,
                                     activebackground='#4a90e2', font=('Segoe UI', 8))
        self.cutoff_scale.set(30)
        self.cutoff_scale.pack(fill=tk.X, pady=(0,10))
        
        tk.Button(container, text="Blur: Ideal LPF", 
                  command=self.apply_ideal_lowpass,
                  bg='#27ae60', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#1e8449').pack(pady=5)
        tk.Button(container, text="Sharpen: Ideal HPF", 
                  command=self.apply_ideal_highpass,
                  bg='#e74c3c', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#c0392b').pack(pady=5)
        
        tk.Label(container, text="Note: Works on grayscale.\nSelection ignored.",
                 bg='#353535', fg='#bbbbbb', font=('Segoe UI', 8), justify=tk.CENTER).pack(pady=(15,0))

    # ========== SEGMENTATION ==========
    def create_segmentation_panel(self, parent):
        parent.configure(bg='#353535')
        container = tk.Frame(parent, bg='#353535')
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.create_section_header(container, "Thresholding")
        
        # Global Threshold
        thresh_frame = tk.Frame(container, bg='#353535')
        thresh_frame.pack(fill=tk.X, pady=5)
        tk.Label(thresh_frame, text="Global Threshold:", bg='#353535', fg='#cccccc',
                 font=('Segoe UI', 9)).pack(anchor=tk.W)
        self.global_thresh = tk.Scale(thresh_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                                     resolution=1, bg='#353535', fg='#cccccc',
                                     troughcolor='#2b2b2b', highlightthickness=0,
                                     activebackground='#4a90e2', font=('Segoe UI', 8))
        self.global_thresh.set(127)
        self.global_thresh.pack(fill=tk.X)
        tk.Button(container, text="RGBO: Global Threshold", 
                  command=self.apply_global_threshold,
                  bg='#2c3e50', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#1a252f').pack(pady=5)

        # Otsu (reuse existing)
        tk.Button(container, text="RGBO: Otsu Threshold", 
                  command=self.apply_otsu_threshold,
                  bg='#2c3e50', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#1a252f').pack(pady=5)

        # Adaptive Threshold
        self.adaptive_method = tk.StringVar(value="mean")
        rb_style = {'bg': '#353535', 'fg': '#cccccc', 'selectcolor': '#2b2b2b',
                    'font': ('Segoe UI', 9)}
        tk.Radiobutton(container, text="Adaptive: Mean", variable=self.adaptive_method,
                       value="mean", **rb_style).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(container, text="Adaptive: Gaussian", variable=self.adaptive_method,
                       value="gaussian", **rb_style).pack(anchor=tk.W, pady=2)
        
        tk.Label(container, text="Block Size (odd):", bg='#353535', fg='#cccccc',
                 font=('Segoe UI', 9)).pack(anchor=tk.W, pady=(8,0))
        self.block_size = tk.Scale(container, from_=3, to=51, orient=tk.HORIZONTAL,
                                   resolution=2, bg='#353535', fg='#cccccc',
                                   troughcolor='#2b2b2b', highlightthickness=0,
                                   activebackground='#4a90e2', font=('Segoe UI', 8))
        self.block_size.set(11)
        self.block_size.pack(fill=tk.X, pady=(0,8))
        
        tk.Button(container, text="RGBO: Adaptive Threshold", 
                  command=self.apply_adaptive_threshold,
                  bg='#2c3e50', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#1a252f').pack(pady=5)

        self.create_section_header(container, "Advanced Segmentation")
        tk.Button(container, text="🔍 Watershed Segmentation", 
                  command=self.apply_watershed_segmentation,
                  bg='#8e44ad', fg='white', font=('Segoe UI', 10, 'bold'),
                  relief=tk.FLAT, cursor='hand2', activebackground='#7d3c98').pack(pady=8)
        
        tk.Label(container, text="Note: Watershed works on\nentire grayscale image.",
                 bg='#353535', fg='#bbbbbb', font=('Segoe UI', 8), justify=tk.CENTER).pack(pady=(10,0))

    def update_brightness_label(self, value):
        self.brightness_value.config(text=f"{int(float(value))}")
    def update_contrast_label(self, value):
        self.contrast_value.config(text=f"{float(value):.1f}")

    # ========== SELECTION FUNCTIONS ==========
    def toggle_selection_mode(self):
        self.selection_active = not self.selection_active
        if self.selection_active:
            self.selection_btn.config(bg='#27ae60', text='🔲 Selection ON')
            self.update_status("🔲 Selection mode: Click and drag to select area")
        else:
            self.selection_btn.config(bg='#4a90e2', text='🔲 Select Area')
            self.update_status("Selection mode disabled")
    def clear_selection(self):
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
        if not self.selection_active or self.current_image is None:
            return
        self.selection_start = (event.x, event.y)
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
    def on_mouse_drag(self, event):
        if not self.selection_active or self.selection_start is None:
            return
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        x1, y1 = self.selection_start
        x2, y2 = event.x, event.y
        self.selection_rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline='#00ff00',
            width=2,
            dash=(5, 5)
        )
    def on_mouse_up(self, event):
        if not self.selection_active or self.selection_start is None:
            return
        self.selection_end = (event.x, event.y)
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
        if self.current_image is None or self.selection_start is None or self.selection_end is None:
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        img_h, img_w = self.current_image.shape[:2]
        scale = min(canvas_width/img_w, canvas_height/img_h, 1.0)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        offset_x = (canvas_width - new_w) // 2
        offset_y = (canvas_height - new_h) // 2
        x1_canvas, y1_canvas = self.selection_start
        x2_canvas, y2_canvas = self.selection_end
        x1_img = int((x1_canvas - offset_x) / scale)
        y1_img = int((y1_canvas - offset_y) / scale)
        x2_img = int((x2_canvas - offset_x) / scale)
        y2_img = int((y2_canvas - offset_y) / scale)
        x1_img = max(0, min(x1_img, img_w))
        y1_img = max(0, min(y1_img, img_h))
        x2_img = max(0, min(x2_img, img_w))
        y2_img = max(0, min(y2_img, img_h))
        if x1_img > x2_img:
            x1_img, x2_img = x2_img, x1_img
        if y1_img > y2_img:
            y1_img, y2_img = y2_img, y1_img
        self.selection_coords = (x1_img, y1_img, x2_img, y2_img)
    def apply_to_selection(self, operation_func):
        if self.selection_coords is None:
            return operation_func(self.current_image)
        x1, y1, x2, y2 = self.selection_coords
        selected_region = self.current_image[y1:y2, x1:x2].copy()
        processed_region = operation_func(selected_region)
        result = self.current_image.copy()
        result[y1:y2, x1:x2] = processed_region
        return result

    # ========== FILE OPERATIONS ==========
    def open_image(self):
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
                self.second_image = None
                if hasattr(self, 'second_img_label'):
                    self.second_img_label.config(text="No second image")
                self.canvas.delete('placeholder')
                self.display_image()
                h, w = self.current_image.shape[:2]
                filename = file_path.split('/')[-1]
                self.img_info_label.config(text=f"📷 {filename} ({w}x{h}px)")
                self.update_status(f"✓ Loaded: {filename}")
            else:
                messagebox.showerror("Error", "Failed to load image")
    def save_image(self):
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

    # ========== HISTORY ==========
    def add_to_history(self):
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_image.copy())
        self.history_index += 1
        if len(self.history) > 20:
            self.history.pop(0)
            self.history_index -= 1
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image()
            self.update_status("↶ Undo applied")
        else:
            self.update_status("⚠️ No more actions to undo")
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_image = self.history[self.history_index].copy()
            self.display_image()
            self.update_status("↷ Redo applied")
        else:
            self.update_status("⚠️ No more actions to redo")
    def reset_image(self):
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            self.second_image = None
            if hasattr(self, 'second_img_label'):
                self.second_img_label.config(text="No second image")
            self.add_to_history()
            self.display_image()
            self.update_status("🔄 Image reset to original")
        else:
            messagebox.showwarning("Warning", "No image loaded")

    # ========== ORIGINAL FILTERS ==========
    def apply_gaussian_blur(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        kernel_size = self.blur_scale.get()
        if kernel_size % 2 == 0: kernel_size += 1
        def blur_operation(img): return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
        self.current_image = self.apply_to_selection(blur_operation)
        self.add_to_history()
        self.display_image()
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Gaussian Blur applied{region_text} (kernel: {kernel_size}x{kernel_size})")
    def apply_median_blur(self):
        if self.current_image is None: return
        kernel_size = self.blur_scale.get()
        if kernel_size % 2 == 0: kernel_size += 1
        def blur_operation(img): return cv2.medianBlur(img, kernel_size)
        self.current_image = self.apply_to_selection(blur_operation)
        self.add_to_history()
        self.display_image()
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Median Blur applied{region_text} (kernel: {kernel_size})")
    def apply_mean_blur(self):
        if self.current_image is None: return
        kernel_size = self.blur_scale.get()
        if kernel_size % 2 == 0: kernel_size += 1
        def blur_operation(img): return cv2.blur(img, (kernel_size, kernel_size))
        self.current_image = self.apply_to_selection(blur_operation)
        self.add_to_history()
        self.display_image()
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Mean Blur applied{region_text} (kernel: {kernel_size}x{kernel_size})")
    def apply_brightness_contrast(self):
        if self.current_image is None: return
        brightness = self.brightness_scale.get()
        contrast = self.contrast_scale.get()
        def adjust_operation(img):
            img_float = img.astype(np.float32)
            scaled = cv2.multiply(img_float, contrast)
            adjusted = cv2.add(scaled, brightness)
            clipped = np.clip(adjusted, 0, 255)
            return clipped.astype(np.uint8)
        self.current_image = self.apply_to_selection(adjust_operation)
        self.add_to_history()
        self.display_image()
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"Adjusted{region_text}: Brightness={brightness}, Contrast={contrast}")
    def apply_laplacian_edge(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        def edge_operation(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            lap = cv2.Laplacian(gray, cv2.CV_16S, ksize=3)
            lap = cv2.convertScaleAbs(lap)
            return cv2.cvtColor(lap, cv2.COLOR_GRAY2BGR)
        self.current_image = self.apply_to_selection(edge_operation)
        self.add_to_history()
        self.display_image()
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Laplacian Edge applied{region_text}")
    def apply_otsu_threshold(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        def threshold_operation(img):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        self.current_image = self.apply_to_selection(threshold_operation)
        self.add_to_history()
        self.display_image()
        region_text = " to selected region" if self.selection_coords else ""
        self.update_status(f"✓ Otsu Threshold applied{region_text}")
    def load_second_image(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load a main image first!")
            return
        file_path = filedialog.askopenfilename(
            title="Select Second Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                       ("All Files", "*.*")]
        )
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                h1, w1 = self.current_image.shape[:2]
                self.second_image = cv2.resize(img, (w1, h1))
                filename = file_path.split('/')[-1]
                self.second_img_label.config(text=f"✓ {filename}")
                self.update_status(f"✓ Second image loaded: {filename}")
            else:
                messagebox.showerror("Error", "Failed to load second image")
                self.second_image = None
                self.second_img_label.config(text="Load failed")
    def apply_logic_operation(self, op):
        if self.current_image is None:
            messagebox.showwarning("Warning", "No main image loaded")
            return
        if self.second_image is None:
            messagebox.showwarning("Warning", "Please load a second image first!")
            return
        try:
            if op == 'AND':
                result = cv2.bitwise_and(self.current_image, self.second_image)
                msg = "BitFields AND applied"
            elif op == 'OR':
                result = cv2.bitwise_or(self.current_image, self.second_image)
                msg = "BitFields OR applied"
            elif op == 'XOR':
                result = cv2.bitwise_xor(self.current_image, self.second_image)
                msg = "BitFields XOR applied"
            else:
                return
            self.current_image = result
            self.add_to_history()
            self.display_image()
            self.update_status(f"✓ {msg}")
        except Exception as e:
            messagebox.showerror("Error", f"Logical operation failed:\n{str(e)}")

    # ========== HALFTONING METHODS ==========
    def apply_halftoning(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image.copy()
        method = self.halftone_method.get()
        if method == "patterning":
            result = self._apply_patterning(gray)
            msg = "Patterning halftoning applied"
        elif method == "dithering":
            result = self._apply_dithering(gray)
            msg = "Dithering halftoning applied"
        else:
            return
        self.current_image = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        self.add_to_history()
        self.display_image()
        self.update_status(f"✓ {msg}")
    def _apply_patterning(self, gray_img):
        h, w = gray_img.shape
        fonts = [
            np.array([[0, 0], [0, 0]], dtype=np.uint8),
            np.array([[0, 1], [0, 0]], dtype=np.uint8),
            np.array([[0, 1], [1, 0]], dtype=np.uint8),
            np.array([[1, 1], [0, 1]], dtype=np.uint8),
            np.array([[1, 1], [1, 1]], dtype=np.uint8),
        ]
        levels = np.digitize(gray_img, bins=[51, 102, 153, 204], right=False)
        out = np.zeros((h * 2, w * 2), dtype=np.uint8)
        for i in range(h):
            for j in range(w):
                lvl = levels[i, j]
                out[i*2:(i+1)*2, j*2:(j+1)*2] = fonts[lvl]
        return out * 255
    def _apply_dithering(self, gray_img):
        dither_matrix = np.array([[0, 128], [192, 64]], dtype=np.uint8)
        h, w = gray_img.shape
        tiled = np.tile(dither_matrix, (int(np.ceil(h/2)), int(np.ceil(w/2))))
        threshold_map = tiled[:h, :w]
        binary = (gray_img > threshold_map).astype(np.uint8) * 255
        return binary

    # ========== NEIGHBORHOOD METHODS ==========
    def apply_mean_filter(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        k = int(self.mean_kernel.get())
        if k % 2 == 0: k += 1
        def op(img): return cv2.blur(img, (k, k))
        self.current_image = self.apply_to_selection(op)
        self.add_to_history()
        self.display_image()
        region = " to selection" if self.selection_coords else ""
        self.update_status(f"✓ Mean blur ({k}×{k}) applied{region}")

    def apply_gaussian_filter(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        k = int(self.gauss_kernel.get())
        if k % 2 == 0: k += 1
        sigma = float(self.gauss_sigma.get())
        def op(img): return cv2.GaussianBlur(img, (k, k), sigmaX=sigma, sigmaY=sigma)
        self.current_image = self.apply_to_selection(op)
        self.add_to_history()
        self.display_image()
        region = " to selection" if self.selection_coords else ""
        self.update_status(f"✓ Gaussian blur ({k}×{k}, σ={sigma}) applied{region}")

    def apply_median_filter(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        k = int(self.median_kernel.get())
        if k % 2 == 0: k += 1
        def op(img): return cv2.medianBlur(img, k)
        self.current_image = self.apply_to_selection(op)
        self.add_to_history()
        self.display_image()
        region = " to selection" if self.selection_coords else ""
        self.update_status(f"✓ Median filter ({k}×{k}) applied{region}")

    def apply_sharpen_laplacian(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        def op(img):
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                lap = cv2.Laplacian(gray, cv2.CV_16S, ksize=3)
                lap = cv2.convertScaleAbs(lap)
                sharpened_gray = cv2.addWeighted(gray, 1.5, lap, -0.5, 0)
                return cv2.cvtColor(sharpened_gray, cv2.COLOR_GRAY2BGR)
            else:
                lap = cv2.Laplacian(img, cv2.CV_16S, ksize=3)
                lap = cv2.convertScaleAbs(lap)
                return cv2.addWeighted(img, 1.5, lap, -0.5, 0)
        self.current_image = self.apply_to_selection(op)
        self.add_to_history()
        self.display_image()
        region = " to selection" if self.selection_coords else ""
        self.update_status(f"✓ Laplacian sharpening applied{region}")

    def apply_unsharp_mask(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        def op(img):
            blurred = cv2.GaussianBlur(img, (0, 0), sigmaX=1.0)
            sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
            return np.clip(sharpened, 0, 255).astype(np.uint8)
        self.current_image = self.apply_to_selection(op)
        self.add_to_history()
        self.display_image()
        region = " to selection" if self.selection_coords else ""
        self.update_status(f"✓ Unsharp masking applied{region}")

    # ========== FREQUENCY DOMAIN METHODS ==========
    def show_fft_magnitude(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image.copy()
        f = np.fft.fft2(gray.astype(np.float32))
        fshift = np.fft.fftshift(f)
        magnitude = np.log(1 + np.abs(fshift))
        magnitude = ((magnitude - magnitude.min()) / (magnitude.max() - magnitude.min()) * 255).astype(np.uint8)
        cv2.imshow("FFT Magnitude Spectrum", magnitude)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def apply_ideal_lowpass(self):
        self._apply_freq_filter('lowpass')

    def apply_ideal_highpass(self):
        self._apply_freq_filter('highpass')

    def _apply_freq_filter(self, filter_type):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        if self.selection_coords is not None:
            messagebox.showinfo("Info", "Frequency filters ignore selection.\nApplying to entire image.")
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image.copy().astype(np.float32)
        D0 = int(self.cutoff_scale.get())
        rows, cols = gray.shape
        crow, ccol = rows // 2, cols // 2
        f = np.fft.fft2(gray)
        fshift = np.fft.fftshift(f)
        mask = np.zeros((rows, cols), dtype=np.float32)
        for i in range(rows):
            for j in range(cols):
                D = np.sqrt((i - crow)**2 + (j - ccol)**2)
                if filter_type == 'lowpass':
                    if D <= D0:
                        mask[i, j] = 1
                else:
                    if D > D0:
                        mask[i, j] = 1
        f_filtered = fshift * mask
        f_ishift = np.fft.ifftshift(f_filtered)
        img_back = np.fft.ifft2(f_ishift)
        img_back = np.abs(img_back)
        img_back = np.clip(img_back, 0, 255).astype(np.uint8)
        self.current_image = cv2.cvtColor(img_back, cv2.COLOR_GRAY2BGR)
        self.add_to_history()
        self.display_image()
        self.update_status(f"✓ Ideal {'LPF' if filter_type == 'lowpass' else 'HPF'} applied (D₀={D0})")

    # ========== SEGMENTATION METHODS ==========
    def apply_global_threshold(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image.copy()
        thresh_val = int(self.global_thresh.get())
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
        self.current_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        self.add_to_history()
        self.display_image()
        self.update_status(f"✓ Global threshold applied (T={thresh_val})")

    def apply_adaptive_threshold(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        if len(self.current_image.shape) == 3:
            gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.current_image.copy()
        block = int(self.block_size.get())
        if block % 2 == 0:
            block += 1
        c = 2
        if self.adaptive_method.get() == "gaussian":
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, block, c)
        else:
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, block, c)
        self.current_image = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        self.add_to_history()
        self.display_image()
        method_name = "Gaussian" if self.adaptive_method.get() == "gaussian" else "Mean"
        self.update_status(f"✓ Adaptive {method_name} threshold applied (block={block})")

    def apply_watershed_segmentation(self):
        if self.current_image is None:
            messagebox.showwarning("Warning", "Please load an image first")
            return
        if len(self.current_image.shape) == 3:
            img = self.current_image.copy()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            img = cv2.cvtColor(self.current_image, cv2.COLOR_GRAY2BGR)
            gray = self.current_image.copy()

        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        _, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        markers = cv2.watershed(img, markers)
        img[markers == -1] = [0, 0, 255]
        self.current_image = img
        self.add_to_history()
        self.display_image()
        self.update_status("✓ Watershed segmentation applied")

    # ========== HISTOGRAM ==========
    def update_histogram(self):
        if self.current_image is None:
            self.hist_ax.clear()
            self.hist_ax.set_facecolor('#3c3c3c')
            self.hist_ax.set_xlim([0, 256])
            self.hist_ax.set_xticks([0, 64, 128, 192, 255])
            self.hist_ax.set_xlabel('Pixel Intensity', color='white', fontsize=9)
            self.hist_ax.tick_params(colors='white', labelsize=8)
            self.hist_ax.grid(True, color='#444444', linestyle='--', linewidth=0.5)
            self.hist_fig.suptitle("RGB Histogram", color='white', fontsize=10)
            self.hist_canvas_agg.draw()
            return

        if len(self.current_image.shape) == 3:
            b, g, r = cv2.split(self.current_image)
            channels = [b, g, r]
            colors = ['blue', 'green', 'red']
        else:
            channels = [self.current_image]
            colors = ['white']

        self.hist_ax.clear()
        self.hist_ax.set_facecolor('#3c3c3c')
        for spine in self.hist_ax.spines.values():
            spine.set_color('#555555')
        self.hist_ax.tick_params(colors='white', labelsize=8)
        self.hist_ax.grid(True, color='#444444', linestyle='--', linewidth=0.5)
        self.hist_ax.set_xlim([0, 256])
        self.hist_ax.set_xticks([0, 64, 128, 192, 255])
        self.hist_ax.set_xlabel('Pixel Intensity', color='white', fontsize=9)

        max_freq = 0
        for channel, color in zip(channels, colors):
            hist, bins = np.histogram(channel.ravel(), bins=256, range=[0, 256])
            max_freq = max(max_freq, np.max(hist))
            self.hist_ax.plot(hist, color=color, linewidth=1.2)

        if max_freq > 0:
            y_max = int(np.ceil(max_freq / 1000) * 1000)
            y_max = max(y_max, 1000)
            self.hist_ax.set_ylim([0, y_max])
            self.hist_ax.set_yticks(np.linspace(0, y_max, 5, dtype=int))
        else:
            self.hist_ax.set_ylim([0, 1000])
            self.hist_ax.set_yticks([0, 250, 500, 750, 1000])

        self.hist_fig.suptitle("RGB Histogram", color='white', fontsize=10)
        self.hist_canvas_agg.draw()

    # ========== DISPLAY ==========
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
        self.update_histogram()
    
    def update_status(self, message):
        if self.current_image is not None:
            h, w = self.current_image.shape[:2]
            self.status_bar.config(text=f"{message}  |  Size: {w}×{h}px")
        else:
            self.status_bar.config(text=message)

# ========== MAIN ==========
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditor(root)
    root.bind('<Control-o>', lambda e: app.open_image())
    root.bind('<Control-s>', lambda e: app.save_image())
    root.bind('<Control-z>', lambda e: app.undo())
    root.bind('<Control-y>', lambda e: app.redo())
    root.mainloop()