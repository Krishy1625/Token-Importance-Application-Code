# prompts_frame.py
# shows prompts
# second page
# used code from
# https://www.tutorialspoint.com/how-to-separate-view-and-controller-in-python-tkinter
# and https://www.pythontutorial.net/tkinter/tkinter-mvc/

import tkinter as tk
from tkinter import ttk


class PromptsFrame(ttk.Frame):
    def __init__(self, parent, controller, prompts, num_prompts):
        super().__init__(parent)
        self.controller = controller
        self.prompts = prompts
        self.num_prompts = num_prompts

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

        self.create_widgets()  # make prompts ui

    def on_canvas_configure(self, event):  # ca nvas content
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())

    def on_frame_configure(self, event):  # upd scroll
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_widgets(self):  # title
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))

        title_label = ttk.Label(
            title_frame,
            text="Random Prompts from CustomSet",
            font=("Helvetica", 32, "bold"),
            foreground="#FFFFFF",
        )
        title_label.pack(pady=(0, 10))

        accent_canvas = tk.Canvas(  # line
            title_frame, height=4, background="#121212", highlightthickness=0
        )
        accent_canvas.pack(fill=tk.X)
        accent_canvas.create_rectangle(0, 0, 1400, 4, fill="#6C3CE9", outline="")

        config_frame = ttk.Frame(self.content_frame)
        config_frame.pack(fill=tk.X, pady=(0, 20))

        dataset_label = ttk.Label(
            config_frame,
            text="Dataset: CustomSet",
            font=("Helvetica", 16, "bold"),
            foreground="#AAAAAA",
        )
        dataset_label.pack(anchor=tk.W, pady=(0, 5))

        prompts_section = ttk.LabelFrame(
            self.content_frame, text=f"{self.num_prompts.get()} Random Prompts"
        )
        prompts_section.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

        for i, prompt in enumerate(self.prompts, 1):
            prompt_container = ttk.Frame(prompts_section)
            prompt_container.pack(fill=tk.X, pady=15, padx=10)

            prompt_header = ttk.Frame(prompt_container)
            prompt_header.pack(fill=tk.X)

            prompt_number = ttk.Label(
                prompt_header,
                text=f"Prompt {i}",
                font=("Helvetica", 18, "bold"),
                foreground="#6C3CE9",
            )
            prompt_number.pack(anchor=tk.W)

            divider = ttk.Separator(prompt_container, orient="horizontal")
            divider.pack(fill=tk.X, pady=10)

            prompt_content_frame = ttk.Frame(prompt_container)  # prompt content
            prompt_content_frame.pack(fill=tk.BOTH, expand=True)

            text_container = ttk.Frame(prompt_content_frame)
            text_container.pack(fill=tk.BOTH, expand=True)

            prompt_scrollbar = ttk.Scrollbar(text_container, orient="vertical")
            prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            prompt_content = tk.Text(
                text_container,
                wrap=tk.WORD,
                height=4,  # inc if using larger prompt dataset
                background="#1E1E1E",
                foreground="#FFFFFF",
                font=("Consolas", 14),
                padx=15,
                pady=15,
                relief=tk.FLAT,
                borderwidth=0,
                yscrollcommand=prompt_scrollbar.set,
            )
            prompt_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            prompt_scrollbar.config(command=prompt_content.yview)

            prompt_content.insert(tk.END, prompt)
            prompt_content.config(state=tk.DISABLED)  # read only

        button_frame = ttk.Frame(self.content_frame)  # button frame
        button_frame.pack(fill=tk.X, pady=(30, 10))

        back_button = ttk.Button(
            button_frame, text="← Back", command=self.controller.go_to_homepage
        )
        back_button.pack(side=tk.LEFT, padx=10)

        refresh_button = ttk.Button(
            button_frame,
            text="Generate New Prompts",
            command=self.controller.refresh_prompts,
        )
        refresh_button.pack(side=tk.RIGHT, padx=10)

        features_button = ttk.Button(
            button_frame,
            text="Select Features →",
            command=self.controller.go_to_features_page,
            style="Accent.TButton",
        )
        features_button.pack(side=tk.RIGHT, padx=10)

        ttk.Frame(self.content_frame, height=20).pack(fill=tk.X)  # more padding
