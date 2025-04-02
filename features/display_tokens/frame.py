# display tokens.py
# https://docs.python.org/3/library/tkinter.ttk.html Treeview and Notebook
# https://www.tutorialspoint.com/tkinter-button-commands-with-lambda-in-python

import tkinter as tk
from tkinter import ttk, messagebox
from frames.feature_frames import BaseFeatureFrame
from features.display_tokens.token_report_generator import generate_token_report


class DisplayTokensFrame(BaseFeatureFrame):
    def __init__(self, parent, controller):
        self.tokenizer = None
        self.prompts = []
        self.notebook = None
        self.prompt_tabs = []

        super().__init__(parent, controller, "Display Tokens")

        if (  # get data from controller
            hasattr(self.controller, "random_prompts")
            and self.controller.random_prompts
        ):
            self.prompts = self.controller.random_prompts
        else:
            self.prompts = []

        try:
            import tiktoken  # here for error handling

            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            messagebox.showerror(
                "Tokenizer Error",
                f"Failed to initialize tokenizer: {str(e)}\n\nMake sure tiktoken is installed: pip install tiktoken",
            )

    def create_content(self):
        content_container = ttk.Frame(self.content_frame)
        content_container.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

        try:
            import tiktoken
        except ImportError:
            error_label = ttk.Label( # error handling
                content_container,
                text=f"Tiktoken library is not installed. Please install it with:\npip install tiktoken",
                font=("Helvetica", 16),
                foreground="red",
                wraplength=800,
                justify=tk.CENTER,
            )
            error_label.pack(anchor=tk.CENTER, pady=50)
            return

        if (
            hasattr(self.controller, "random_prompts")
            and self.controller.random_prompts
        ):
            self.prompts = self.controller.random_prompts

        if not self.prompts:
            no_prompts_label = ttk.Label(
                content_container,
                text="No prompts available. Please generate prompts on the Prompts page first.",
                font=("Helvetica", 16),
                foreground="#AAAAAA",
                wraplength=800,
                justify=tk.CENTER,
            )
            no_prompts_label.pack(anchor=tk.CENTER, pady=50)

            goto_prompts_button = ttk.Button(
                content_container,
                text="Go to Prompts Page",
                command=lambda: self.controller.show_frame("PromptsPage"),
            )
            goto_prompts_button.pack(pady=20)
            return

        description_label = ttk.Label(
            content_container,
            text="This page shows how prompts from your dataset are tokenized using the cl100k_base tokenizer (used by GPT-4, ChatGPT).",
            font=("Helvetica", 16),
            foreground="#FFFFFF",
            wraplength=800,
        )
        description_label.pack(anchor=tk.W, pady=(0, 20))

        if self.tokenizer is None: # initialise tokenizer
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                error_label = ttk.Label(
                    content_container,
                    text=f"Error initializing tokenizer: {str(e)}",
                    font=("Helvetica", 16),
                    foreground="red",
                    wraplength=800,
                    justify=tk.CENTER,
                )
                error_label.pack(anchor=tk.CENTER, pady=50)
                return

        self.notebook = ttk.Notebook(content_container) # notebook creation see top of file
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        self.prompt_tabs = []
        for i, prompt in enumerate(self.prompts, 1):
            prompt_frame = ttk.Frame(self.notebook, padding=10)
            self.notebook.add(prompt_frame, text=f"Prompt {i}")
            self.prompt_tabs.append(prompt_frame)

            prompt_label = ttk.Label(
                prompt_frame,
                text="Original Prompt:",
                font=("Helvetica", 14, "bold"),
                foreground="#FFFFFF",
            )
            prompt_label.pack(anchor=tk.W, pady=(0, 5))

            prompt_text = tk.Text(
                prompt_frame,
                wrap=tk.WORD,
                height=4,
                background="#1E1E1E",
                foreground="#FFFFFF",
                font=("Consolas", 12),
                padx=10,
                pady=10,
                relief=tk.FLAT,
                borderwidth=0,
            )
            prompt_text.pack(fill=tk.X, pady=(0, 20))
            prompt_text.insert(tk.END, prompt)
            prompt_text.config(state=tk.DISABLED)  # make read-only (disable)

            tokens_label = ttk.Label(
                prompt_frame,
                text="Tokenization (cl100k_base):",
                font=("Helvetica", 14, "bold"),
                foreground="#FFFFFF",
            )
            tokens_label.pack(anchor=tk.W, pady=(0, 5))

            table_frame = ttk.Frame(prompt_frame) # table frame for the output 
            table_frame.pack(fill=tk.BOTH, expand=True)

            self.create_token_table(table_frame, prompt) # scrolable table better UI

        export_frame = ttk.Frame(content_container)
        export_frame.pack(fill=tk.X, pady=(20, 10))

        export_button = ttk.Button(
            export_frame, text="Download Token Report", command=self.export_report
        )
        export_button.pack(side=tk.RIGHT, padx=10)

    def export_report(self): # save report
        try:
            filename = generate_token_report(self.prompts, self.tokenizer)

            if filename:
                messagebox.showinfo(
                    "Export Successful", f"Token report saved to {filename}"
                )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {str(e)}")

    def create_token_table(self, parent, prompt):
        try:
            table_container = ttk.Frame(parent)
            table_container.pack(fill=tk.BOTH, expand=True, pady=5)
            table_scroll_y = ttk.Scrollbar(table_container, orient="vertical")
            table_scroll_x = ttk.Scrollbar(table_container, orient="horizontal") # enable scrolling

            columns = ("index", "token_text")
            token_table = ttk.Treeview(
                table_container,
                columns=columns,
                show="headings",
                yscrollcommand=table_scroll_y.set,
                xscrollcommand=table_scroll_x.set,
            )

            table_scroll_y.config(command=token_table.yview)
            table_scroll_x.config(command=token_table.xview)
            table_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            table_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
            token_table.pack(fill=tk.BOTH, expand=True)

            token_table.heading("index", text="Index")
            token_table.heading("token_text", text="Token Text")

            token_table.column(
                "index", width=80, minwidth=80, stretch=False, anchor="center"
            )
            token_table.column(
                "token_text", width=600, minwidth=300, stretch=True, anchor="w"
            )

            token_ids = self.tokenizer.encode(prompt)

            token_table.tag_configure("oddrow", background="#2A2A2A")
            token_table.tag_configure("evenrow", background="#333333")

            for i, token_id in enumerate(token_ids):
                token_text = self.tokenizer.decode([token_id])

                if token_text == "\n":
                    token_text = "\\n"
                elif token_text == "\t":
                    token_text = "\\t"
                elif token_text == " ":
                    token_text = "·"  
                elif len(token_text.strip()) == 0 and len(token_text) > 1:
                    token_text = "·" * len(token_text)  

                row_tag = "evenrow" if i % 2 == 0 else "oddrow"
                token_table.insert("", "end", values=(i, token_text), tags=(row_tag,))
                # ^ contrasting colours for clear visibility

            return token_table
        except Exception as e:
            error_label = ttk.Label(
                parent,
                text=f"Error tokenizing prompt: {str(e)}",
                font=("Helvetica", 14),
                foreground="red",
                wraplength=700,
            )
            error_label.pack(fill=tk.BOTH, expand=True, pady=20)
            return None