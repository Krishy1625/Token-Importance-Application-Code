# homepage_frame.py
# homepage stuff
# used code for help from https://www.youtube.com/watch?v=7u87KAO5-Ug

import tkinter as tk
from tkinter import ttk


class HomepageFrame(ttk.Frame):
    def __init__(
        self, parent, controller, api_key, selected_dataset, num_prompts, show_key
    ):
        super().__init__(parent)
        self.controller = controller
        self.api_key = api_key
        self.selected_dataset = selected_dataset
        self.num_prompts = num_prompts
        self.show_key = show_key

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

        self.canvas.bind(
            "<Configure>", self.on_canvas_configure
        )  # configure canvas for settings
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        self.create_widgets()  # create ui

    def on_canvas_configure(self, event):  # upd scroll for convienience sake
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_widgets(self):  # content
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 40))

        title_label = ttk.Label(  # title desc
            title_frame,
            text="Welcome To The Homepage",
            font=("Helvetica", 32, "bold"),
            foreground="#FFFFFF",
        )
        title_label.pack(pady=(0, 10))

        accent_canvas = tk.Canvas(  # line
            title_frame, height=4, background="#121212", highlightthickness=0
        )
        accent_canvas.pack(fill=tk.X)
        accent_canvas.create_rectangle(
            0, 0, 1400, 4, fill="#6C3CE9", outline=""
        )  # grad

        # api key frames/ inp
        api_frame = ttk.LabelFrame(self.content_frame, text="API Input")
        api_frame.pack(fill=tk.X, pady=25, padx=20)

        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, pady=10)

        api_key_label = ttk.Label(
            api_key_frame, text="API Key:", font=("Helvetica", 16)
        )
        api_key_label.pack(anchor=tk.W, pady=(0, 10))

        api_key_description = ttk.Label(
            api_key_frame, text="Enter your API key", foreground="#AAAAAA"
        )
        api_key_description.pack(anchor=tk.W, pady=(0, 15))

        api_key_entry = ttk.Entry(
            api_key_frame, textvariable=self.api_key, width=80, show="•"
        )
        api_key_entry.pack(fill=tk.X, pady=(0, 15))

        show_key_check = tk.Checkbutton(  # toggle show/hidden api key
            api_key_frame,
            text="Show API Key",
            variable=self.show_key,
            command=lambda: self.toggle_api_key_visibility(api_key_entry),
            bg="#121212",
            fg="#FFFFFF",
            selectcolor="#1E1E1E",
            activebackground="#121212",
            activeforeground="#FFFFFF",
            font=("Helvetica", 14),
            highlightthickness=0,
            bd=0,
            borderwidth=0,
        )
        show_key_check.pack(anchor=tk.W)

        dataset_frame = ttk.LabelFrame(self.content_frame, text="Dataset Configuration")
        dataset_frame.pack(
            fill=tk.X, pady=25, padx=20
        )  # dataset frame, just custom for now

        dataset_select_frame = ttk.Frame(dataset_frame)
        dataset_select_frame.pack(fill=tk.X, pady=10)

        dataset_label = ttk.Label(
            dataset_select_frame, text="Selected Dataset:", font=("Helvetica", 16)
        )
        dataset_label.pack(anchor=tk.W, pady=(0, 10))

        dataset_description = ttk.Label(
            dataset_select_frame,
            text="Using custom dataset (CustomSet.txt)",
            foreground="#AAAAAA",
        )
        dataset_description.pack(anchor=tk.W, pady=(0, 15))

        dataset_value_label = ttk.Label(
            dataset_select_frame,
            text="CustomSet",
            font=("Helvetica", 14, "bold"),
            foreground="#6C3CE9",
        )
        dataset_value_label.pack(anchor=tk.W, pady=(0, 10))

        num_prompts_frame = ttk.LabelFrame(self.content_frame, text="Number of Prompts")
        # no. of Prompts Selection frames
        num_prompts_frame.pack(fill=tk.X, pady=25, padx=20)

        num_prompts_select_frame = ttk.Frame(num_prompts_frame)
        num_prompts_select_frame.pack(fill=tk.X, pady=10)

        num_prompts_label = ttk.Label(
            num_prompts_select_frame,
            text="Number of Prompts to Generate:",
            font=("Helvetica", 16),
        )
        num_prompts_label.pack(anchor=tk.W, pady=(0, 10))

        num_prompts_description = ttk.Label(
            num_prompts_select_frame,
            text="Select how many random prompts you want to generate from the dataset (1-5)",
            foreground="#AAAAAA",
        )
        num_prompts_description.pack(anchor=tk.W, pady=(0, 15))

        # slider for no. of prompts
        num_prompts_slider_frame = ttk.Frame(num_prompts_select_frame)
        num_prompts_slider_frame.pack(fill=tk.X, pady=10)

        num_prompts_slider = ttk.Scale(
            num_prompts_slider_frame,
            from_=1,
            to=5,
            orient=tk.HORIZONTAL,
            variable=self.num_prompts,
            command=lambda v: self.update_num_prompts_label(num_prompts_value_label),
        )
        num_prompts_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        num_prompts_value_label = ttk.Label(
            num_prompts_slider_frame,
            text=str(int(self.num_prompts.get())),
            width=2,
            font=("Helvetica", 16, "bold"),
            foreground="#6C3CE9",
        )
        num_prompts_value_label.pack(side=tk.RIGHT)

        # buttons
        button_container = ttk.Frame(self.content_frame)
        button_container.pack(fill=tk.X, pady=(20, 20), padx=20)

        button_frame = ttk.Frame(button_container)
        button_frame.pack(fill=tk.X)

        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_fields)
        clear_button.pack(side=tk.RIGHT, padx=10)

        save_button = ttk.Button(
            button_frame, text="Save Configuration", command=self.controller.save_config
        )
        save_button.pack(side=tk.RIGHT, padx=10)

        next_button = ttk.Button(
            button_frame,
            text="Next →",
            command=self.controller.go_to_prompts_page,
            style="Accent.TButton",
        )
        next_button.pack(side=tk.RIGHT, padx=10)

        ttk.Frame(self.content_frame, height=20).pack(fill=tk.X)

    def toggle_api_key_visibility(self, entry_widget):
        if self.show_key.get():
            entry_widget.config(show="")
        else:
            entry_widget.config(show="•")

    def clear_fields(self):
        self.api_key.set("")
        self.selected_dataset.set("CustomSet")  # keep custon for now
        self.num_prompts.set(3)

    def update_num_prompts_label(self, label_widget):
        label_widget.config(text=str(int(self.num_prompts.get())))
