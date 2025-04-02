# This file contains base template frames for each feature option.
# A lot of code was used from the other files in my frames folder
import tkinter as tk
from tkinter import ttk


class BaseFeatureFrame(ttk.Frame):
    def __init__(self, parent, controller, title):
        super().__init__(parent)
        self.controller = controller
        self.title_text = title

        self.canvas_container = ttk.Frame(self)
        self.canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_container, background="#121212", highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self.canvas_container, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_frame = ttk.Frame(self.canvas, padding="40")
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.content_frame,
            anchor=tk.NW,
            width=self.canvas.winfo_width(),
        )
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.create_header()
        self.create_content()
        self.create_back_button()

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_header(self):
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))

        title_label = ttk.Label(
            title_frame,
            text=self.title_text,
            font=("Helvetica", 32, "bold"),
            foreground="#FFFFFF",
        )
        title_label.pack(pady=(0, 10))

        accent_canvas = tk.Canvas(
            title_frame, height=4, background="#121212", highlightthickness=0
        )
        accent_canvas.pack(fill=tk.X)
        accent_canvas.create_rectangle(0, 0, 1400, 4, fill="#6C3CE9", outline="")

    def create_content(self):
        placeholder_frame = ttk.Frame(self.content_frame, padding=20)
        placeholder_frame.pack(fill=tk.BOTH, expand=True, pady=40, padx=20)

        placeholder_label = ttk.Label(
            placeholder_frame,
            text=f"This is the {self.title_text} feature page.\nImplementation will be added here.",
            font=("Helvetica", 18),
            foreground="#AAAAAA",
            background="#1E1E1E",
            padding=40,
        )
        placeholder_label.pack(fill=tk.BOTH, expand=True, pady=80)

    def create_back_button(self):
        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 10))

        back_button = ttk.Button(
            button_frame,
            text="← Back to Features",
            command=lambda: self.controller.show_frame("FeaturesPage"),
        )
        back_button.pack(side=tk.LEFT, padx=10)

        ttk.Frame(self.content_frame, height=20).pack(fill=tk.X)


class DisplayTokensFrame(BaseFeatureFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Display Tokens")


class CosineSimilarityFrame(BaseFeatureFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Cosine Similarity")


class ShapValuesFrame(BaseFeatureFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "SHAP Values")


# specific frames ^
