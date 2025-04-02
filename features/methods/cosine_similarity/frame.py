import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from datetime import datetime
from frames.feature_frames import BaseFeatureFrame
from sklearn.metrics.pairwise import cosine_similarity 

# note idx is index

class CosineSimilarityFrame(BaseFeatureFrame):
    def __init__(self, parent, controller):
        self.api_key = controller.api_key # get data (api key from controller + prompts)
        self.prompts = (
            controller.random_prompts if hasattr(controller, "random_prompts") else []
        )
        super().__init__(parent, controller, "Cosine Similarity")

    def create_content(self):
        content_container = ttk.Frame(self.content_frame)
        content_container.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

        description_label = ttk.Label(  # description
            content_container,
            text="Cosine Similarity measures the importance of each token by calculating the cosine similarity between embeddings with and without that token. Higher values indicate more important tokens.",
            font=("Helvetica", 16),
            foreground="#FFFFFF",
            wraplength=800,
        )
        description_label.pack(anchor=tk.W, pady=(0, 20))

        self.status_vars = {}
        self.result_data = {}
        self.prompt_frames = {}

        progress_frame = ttk.Frame(
            content_container
        )  # progress bar frame (not the bar)
        progress_frame.pack(fill=tk.X, pady=10)

        progress_label = ttk.Label(
            progress_frame,
            text="Analysis Progress:",
            font=("Helvetica", 14),
            foreground="#FFFFFF",
        )
        progress_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_var = tk.DoubleVar(value=0.0) # https://stackoverflow.com/questions/73831645/how-tk-doublevar-works & https://tkdocs.com/pyref/doublevar.html
        self.progress_bar = ttk.Progressbar( # https://docs.python.org/3/library/tkinter.ttk.html
            progress_frame,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            mode="determinate",
            length=300,
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        prompts_label = ttk.Label(
            content_container,
            text="Prompts",
            font=("Helvetica", 18, "bold"),
            foreground="#FFFFFF",
        )
        prompts_label.pack(anchor=tk.W, pady=(20, 10))

        for i, prompt in enumerate(self.prompts, 1):
            prompt_frame = ttk.LabelFrame(content_container, text=f"Prompt {i}")
            prompt_frame.pack(fill=tk.X, pady=15, padx=10, expand=False)

            self.prompt_frames[i] = prompt_frame

            preview_text = (
                prompt[:100] + "..." if len(prompt) > 100 else prompt
            )  # show the prompt for ease of use
            preview_label = ttk.Label(
                prompt_frame,
                text=preview_text,
                font=("Helvetica", 12),
                foreground="#AAAAAA",
                wraplength=700,
            )
            preview_label.pack(anchor=tk.W, pady=10, padx=10)

            button_container = ttk.Frame(prompt_frame)
            button_container.pack(fill=tk.X, pady=10, padx=10)

            self.status_vars[i] = tk.StringVar(
                value="Not started"
            )  # status of the computation

            status_frame = ttk.Frame(button_container)
            status_frame.pack(side=tk.LEFT, pady=5)

            status_label = ttk.Label(
                status_frame,
                text="Status:",
                font=("Helvetica", 12),
                foreground="#FFFFFF",
            )
            status_label.pack(side=tk.LEFT, padx=(0, 5))

            status_value = ttk.Label(
                status_frame,
                textvariable=self.status_vars[i],
                font=("Helvetica", 12, "bold"),
                foreground="#AAAAAA",
            )
            status_value.pack(side=tk.LEFT)

            calculate_button = ttk.Button(
                button_container,
                text="Calculate Cosine Similarity",
                command=lambda p=prompt, idx=i: self.calculate_cosine_similarity(
                    p, idx
                ),
            )
            calculate_button.pack(side=tk.RIGHT, padx=5)

            self.status_vars[f"calculate_button_{i}"] = calculate_button

            heatmap_button = ttk.Button( # create Heatmap button (initially disabled)
                button_container,
                text="Create Heatmap",
                state="disabled",
                command=lambda idx=i: self.create_heatmap(idx),
            )
            heatmap_button.pack(side=tk.RIGHT, padx=5)

            self.status_vars[f"heatmap_button_{i}"] = heatmap_button # store the heatmap button reference to enable it later

            download_button = ttk.Button( # download report button (initially disabled)
                button_container,
                text="Download Report",
                state="disabled",
                command=lambda idx=i: self.download_report(idx),
            )
            download_button.pack(side=tk.RIGHT, padx=5)

            self.status_vars[f"download_button_{i}"] = download_button  # store the download button reference to enable it later

            viz_container = ttk.Frame(prompt_frame)
            viz_container.pack(fill=tk.X, pady=10, padx=10)

            self.status_vars[f"viz_container_{i}"] = viz_container

        batch_frame = ttk.Frame(content_container)
        batch_frame.pack(fill=tk.X, pady=20)

        batch_button = ttk.Button(
            batch_frame,
            text="Calculate All Prompts",
            style="Accent.TButton",
            command=self.batch_calculate_all,
        )
        batch_button.pack(side=tk.RIGHT)

    def calculate_cosine_similarity(self, prompt, prompt_idx):# singel prompt calculation
        if not prompt.strip():
            messagebox.showwarning(
                "Empty Prompt", "The prompt is empty. Please enter a valid prompt."
            )
            return

        api_key = self.api_key.get().strip() # check api key
        if not api_key:
            messagebox.showwarning(
                "API Key Required",
                "Please enter your OpenAI API key in the homepage settings.",
            )
            return

        calculate_button = self.status_vars.get(f"calculate_button_{prompt_idx}")
        if calculate_button:   # Disable the calculate button to prevent multiple clicks
            calculate_button.config(state="disabled")

        self.update_status(
            prompt_idx, "Processing...", "#FFA500"
        )  # orange for processing

        self.progress_var.set(0)  # reset progress bar

        thread = threading.Thread(
            target=self._calculate_cosine_similarity_thread, args=(prompt, prompt_idx)
        )
        thread.daemon = True
        thread.start()


    # note that a thread must be created as i am running multiple processes so cosine similarity 
    # calculation is takig place in the background so that the UI is still visible
    def _calculate_cosine_similarity_thread(self, prompt, prompt_idx):
        try:
            api_key = self.api_key.get().strip()
            max_tokens = 50 # remove for longer prompts
            model = "gpt-3.5-turbo"  # fixed model
            embedding_model = "text-embedding-3-small"  # fixed embedding model

            # Display initial status
            self.content_frame.after(
                0,
                lambda: self.update_status(
                    prompt_idx, "Tokenizing prompt...", "#FFA500"
                ),
            )

            # initialize tokenizer
            try:
                import tiktoken
                enc = tiktoken.encoding_for_model(model)
                tokens_ids = enc.encode(prompt)
                tokens = [
                    enc.decode_single_token_bytes(token).decode(
                        "utf-8", errors="ignore"
                    )
                    for token in tokens_ids
                ]

                if len(tokens) > max_tokens:
                    tokens_ids = tokens_ids[:max_tokens]
                    tokens = tokens[:max_tokens]

                self.content_frame.after(
                    0,
                    lambda: self.update_status(
                        prompt_idx, "Getting original embedding...", "#FFA500"
                    ),
                )

                import openai
                from openai import OpenAI

                client = OpenAI(api_key=api_key)

                try:
                    response = client.embeddings.create(
                        input=[prompt], model=embedding_model
                    )
                    import numpy as np

                    original_embedding = np.array(response.data[0].embedding)

                    self.content_frame.after(
                        0,
                        lambda: self.update_status(
                            prompt_idx, "Analyzing token importance...", "#FFA500"
                        ),
                    )

                    token_data = []
                    total_tokens = len(tokens)

                    for i, token in enumerate(tokens):
                        try:
                            progress_percentage = ((i + 1) / total_tokens) * 100
                            self.content_frame.after(
                                0,
                                lambda p=progress_percentage: self.progress_var.set(p),
                            )

                            if token.strip() in ["", " ", ".", ",", "!", "?"]: # exclude tokens for importance calculations, remove if required
                                continue

                            perturbed_tokens = tokens_ids.copy()
                            perturbed_tokens.pop(i)
                            perturbed_text = enc.decode(perturbed_tokens)

                            perturbed_response = client.embeddings.create(
                                input=[perturbed_text], model=embedding_model
                            )
                            perturbed_embedding = np.array(
                                perturbed_response.data[0].embedding
                            )
                            similarity = cosine_similarity(
                                [original_embedding], [perturbed_embedding]
                            )[0][0]
                            importance_score = (
                                1 - similarity
                            )  # Higher score = more important

                            token_data.append(
                                {
                                    "token": token,
                                    "importance": float(importance_score),
                                    "position": i,
                                }
                            )
                        except Exception as token_error:
                            print(f"Error processing token {token}: {str(token_error)}")
                            # Continue with next token instead of failing the entire process

                    if token_data:
                        importance_values = [td["importance"] for td in token_data]
                        min_value = min(importance_values)
                        max_value = max(importance_values)

                        # no division by zero
                        if max_value > min_value:
                            for td in token_data:
                                td["importance"] = (td["importance"] - min_value) / (
                                    max_value - min_value
                                )

                    # Sort results by importance (descending)
                    token_data.sort(key=lambda x: x["importance"], reverse=True)

                    # Generate report
                    timestamp = datetime.now().isoformat() # https://docs.python.org/3/library/time.html
                    report = {
                        "prompt": prompt,
                        "tokens": token_data,
                        "timestamp": timestamp,
                        "model": model,
                        "embedding_model": embedding_model,
                        "api_key": api_key,  
                    }

                    self.result_data[prompt_idx] = report

                    self.content_frame.after( # buffer
                        100, lambda: self.update_ui_after_calculation(prompt_idx, True)
                    )

                except openai.OpenAIError as api_err:
                    raise RuntimeError(f"OpenAI API error: {str(api_err)}")

            except ImportError as imp_err: # error handling
                raise RuntimeError(
                    f"Required package not found: {str(imp_err)}. Please install using pip."
                )
            except Exception as e:
                raise RuntimeError(f"Error processing prompt: {str(e)}")

        except Exception as e:
            error_msg = str(e)
            print(f"Error in calculation thread: {error_msg}")
            self.content_frame.after(
                100,
                lambda: self.update_ui_after_calculation(prompt_idx, False, error_msg),
            )

    def update_status(self, prompt_idx, message, color="#FFFFFF"):
        if prompt_idx in self.status_vars:
            self.status_vars[prompt_idx].set(message)
            self.update_status_color(prompt_idx, color)

    def update_status_color(self, prompt_idx, color):
        if prompt_idx not in self.prompt_frames:
            return

        # use winfo_children instead of winfo_descendants for better compatibility
        # and iterate through children recursively
        # https://www.tutorialspoint.com/getting-every-child-widget-of-a-tkinter-window

        def find_status_label(widget):
            if (
                isinstance(widget, ttk.Label)
                and "textvariable" in widget.config()
                and widget.cget("textvariable") == str(self.status_vars[prompt_idx])
            ):
                widget.configure(foreground=color)
                return True

            for child in widget.winfo_children():
                if find_status_label(child):
                    return True

            return False

        find_status_label(self.prompt_frames[prompt_idx])

    def update_ui_after_calculation(self, prompt_idx, success, error_msg=None):
        calculate_button = self.status_vars.get(f"calculate_button_{prompt_idx}")
        if calculate_button:
            calculate_button.config(state="normal")

        if success: # basically just make the buttons clickable now that the calculation is done
            self.update_status(prompt_idx, "Completed", "#4CAF50") 
            self.progress_var.set(100)

            download_button = self.status_vars.get(f"download_button_{prompt_idx}")
            if download_button:
                download_button.config(state="normal")

            heatmap_button = self.status_vars.get(f"heatmap_button_{prompt_idx}")
            if heatmap_button:
                heatmap_button.config(state="normal")

            self.display_results(prompt_idx)
        else:
            short_error = error_msg
            if len(error_msg) > 50:
                short_error = error_msg[:47] + "..."
            self.update_status(
                prompt_idx, f"Error: {short_error}", "#F44336"
            )  # red for error

            self.progress_var.set(0)

            error_title = "Calculation Error"
            if "API" in error_msg:
                error_title = "API Error"
            elif "token" in error_msg.lower():
                error_title = "Tokenization Error"

            messagebox.showerror(
                error_title, f"{error_msg}\n\nPlease try again or check your settings."
            )

    def display_results(self, prompt_idx):
        viz_container = self.status_vars.get(f"viz_container_{prompt_idx}")
        if not viz_container:
            return

        for widget in viz_container.winfo_children(): # https://www.tutorialspoint.com/getting-every-child-widget-of-a-tkinter-window
            widget.destroy()

        result = self.result_data.get(prompt_idx)
        if not result:
            return

        token_data = result.get("tokens", [])
        if not token_data:
            ttk.Label(
                viz_container,
                text="No token data available",
                font=("Helvetica", 12),
                foreground="#AAAAAA",
            ).pack(pady=10)
            return

        tokens_frame = ttk.Frame(viz_container)
        tokens_frame.pack(fill=tk.X, pady=10)

        header = ttk.Label(
            tokens_frame,
            text="Top tokens by importance:",
            font=("Helvetica", 14, "bold"),
            foreground="#FFFFFF",
        )
        header.pack(anchor=tk.W, pady=(0, 10))

        top_tokens = token_data[:5]  # display the top 5 tokens for screen fitting

        token_display = ttk.Frame(tokens_frame)
        token_display.pack(fill=tk.X, padx=10, pady=5)

        for token_info in top_tokens:
            token = token_info.get("token", "")
            importance = token_info.get("importance", 0)

            blue_intensity = int(255 * (1 - importance))
            color = f"#{blue_intensity:02x}{blue_intensity:02x}FF"

            token_frame = ttk.Frame(token_display)
            token_frame.pack(side=tk.LEFT, padx=5, pady=5)

            token_label = tk.Label(
                token_frame,
                text=token,
                font=("Consolas", 14, "bold"),
                fg="#FFFFFF"
                if importance > 0.5
                else "#000000",  
                bg=color,
                padx=8,
                pady=5,
            )
            token_label.pack(side=tk.TOP)

            score_label = ttk.Label(
                token_frame,
                text=f"{importance:.2f}",
                font=("Consolas", 10),
                foreground="#AAAAAA",
            )
            score_label.pack(side=tk.TOP)

    def download_report(self, prompt_idx):
        result = self.result_data.get(prompt_idx)
        if not result:
            messagebox.showwarning(
                "No Data", "No analysis data available for this prompt."
            )
            return

        file_path = filedialog.asksaveasfilename( # let user save where they want to 
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Token Importance Report",
        )

        if not file_path:
            return  

        try:
            from features.methods.cosine_similarity.report_writer import (
                write_token_importance_report,
            )

            success = write_token_importance_report(file_path, result)

            if success:
                messagebox.showinfo(
                    "Download Complete", f"Report saved successfully to {file_path}"
                )
            else:
                messagebox.showerror(
                    "Error", "Failed to save report. Please try again."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {str(e)}")

    def create_heatmap(self, prompt_idx):
        result = self.result_data.get(prompt_idx)
        if not result:
            messagebox.showwarning(
                "No Data", "No analysis data available for this prompt."
            )
            return

        file_path = (
            filedialog.asksaveasfilename(  # ask user where they wan to store the PNG
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save Heatmap Visualization",
            )
        )

        if not file_path:
            return 
        try:
            from features.methods.cosine_similarity.heatmap_generator import (
                generate_token_heatmap,
            )

            success = generate_token_heatmap(result, file_path)

            if success:
                messagebox.showinfo(
                    "Heatmap Created",
                    f"Heatmap visualization saved successfully to {file_path}",
                )
            else:
                messagebox.showerror(
                    "Error", "Failed to create heatmap. Please try again."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create heatmap: {str(e)}")

    def batch_calculate_all(self):  # all prompts
        confirm = messagebox.askyesno(
            "Batch Process",
            "This will calculate cosine similarity for all prompts. Proceed?",
        )

        if not confirm:
            return

        # get the api key
        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showwarning(
                "API Key Required",
                "Please enter your OpenAI API key in the homepage settings.",
            )
            return

        for i, prompt in enumerate(self.prompts, 1):
            if not prompt.strip():  # empty prompts
                continue

            self.calculate_cosine_similarity(prompt, i)
            time.sleep(0.2)  # delay to avoid freezing
