# features_frame.py
# shows the features of the application on the features frame
# and buttons for them 


import tkinter as tk
from tkinter import ttk


class FeaturesFrame(ttk.Frame):
    def __init__(
        self,
        parent,
        controller,
        display_tokens_enabled,
        method_cosine,
        method_shap,
    ):
        super().__init__(parent)
        self.controller = controller

        self.display_tokens_enabled = display_tokens_enabled
        self.method_cosine = method_cosine
        self.method_shap = method_shap # variable initialisation

        self.canvas_container = ttk.Frame(self) # canvas
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

        #content frame 
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
        # ^ make it adjustable to any screen size and some improvements like scrolling
        self.create_widgets()

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_widgets(self):
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))

        title_label = ttk.Label(
            title_frame,
            text="Token Importance Features",
            font=("Helvetica", 32, "bold"),
            foreground="#FFFFFF",
        )
        title_label.pack(pady=(0, 10))

        accent_canvas = tk.Canvas( # line ---
            title_frame, height=4, background="#121212", highlightthickness=0
        )
        accent_canvas.pack(fill=tk.X)
        accent_canvas.create_rectangle(0, 0, 1400, 4, fill="#6C3CE9", outline="")

        # first section 1: display tokens
        section1_frame = ttk.LabelFrame(
            self.content_frame, text="Section 1: Display Tokens"
        )
        section1_frame.pack(fill=tk.X, pady=15, padx=20)

        # description for display tokens
        display_tokens_desc = ttk.Label(
            section1_frame,
            text="Enable token visualization to see how important each token is in your prompts.",
            font=("Helvetica", 14),
            foreground="#AAAAAA",
        )
        display_tokens_desc.pack(anchor=tk.W, pady=(10, 15), padx=20)

        # token container for display 
        button_container1 = ttk.Frame(section1_frame)
        button_container1.pack(fill=tk.X, padx=20, pady=(0, 15))

        # display the tokens when button clicked
        open_button1 = ttk.Button(
            button_container1,
            text="Open Display Tokens",
            command=lambda: self.controller.open_feature_page("display_tokens"),
            style="Accent.TButton",
        )
        open_button1.pack(side=tk.RIGHT)

        # section 2: cosine similarity
        section2_frame = ttk.LabelFrame(
            self.content_frame, text="Section 2: Cosine Similarity"
        )
        section2_frame.pack(fill=tk.X, pady=15, padx=20)

        # display the tokens when cosine similarity frame
        cosine_desc = ttk.Label(
            section2_frame,
            text="Measures token importance based on embedding similarity between prompts with and without specific tokens.",
            font=("Helvetica", 14),
            foreground="#AAAAAA",
        )
        cosine_desc.pack(anchor=tk.W, pady=(10, 15), padx=20)

        # cosine button container
        cosine_container = ttk.Frame(section2_frame)
        cosine_container.pack(fill=tk.X, padx=20, pady=(0, 15))

        cosine_button = ttk.Button(
            cosine_container,
            text="Open Cosine Similarity",
            command=lambda: self.controller.open_feature_page("cosine_similarity"),
            style="Accent.TButton",
        )
        cosine_button.pack(side=tk.RIGHT)

        # section 3: SHAP Method
        section3_frame = ttk.LabelFrame(
            self.content_frame, text="Section 3: SHAP Analysis"
        )
        section3_frame.pack(fill=tk.X, pady=15, padx=20)

        shap_desc = ttk.Label(
            section3_frame,
            text="SHAP (SHapley Additive exPlanations) Values measure each token's contribution to the model output.",
            font=("Helvetica", 14),
            foreground="#AAAAAA",
        )
        shap_desc.pack(anchor=tk.W, pady=(10, 15), padx=20)

        shap_container = ttk.Frame(section3_frame)
        shap_container.pack(fill=tk.X, padx=20, pady=(0, 15))

        shap_button = ttk.Button(
            shap_container,
            text="Open SHAP Analysis",
            command=lambda: self.controller.open_feature_page("shap_values"),
            style="Accent.TButton",
        )
        shap_button.pack(side=tk.RIGHT)

        button_frame = ttk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, pady=(30, 10))

        back_button = ttk.Button(
            button_frame,
            text="← Back to Prompts",
            command=lambda: self.controller.show_frame("PromptsPage"),
        )
        back_button.pack(side=tk.LEFT, padx=10) # padding

        ttk.Frame(self.content_frame, height=20).pack(fill=tk.X)