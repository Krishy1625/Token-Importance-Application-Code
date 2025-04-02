from frames.feature_frames import BaseFeatureFrame
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from datetime import datetime
import tiktoken
import random
from openai import OpenAI

# code from cosine similarity frame was used for consistency 
# PLEASE NOTE: The code that I have used in this file is adapted from the work of SHAP and TokenSHAP
# and therefore will contain code that belongs to them:
# TokenSHAP -> https://github.com/ronigold/TokenSHAP
# SHAP -> https://github.com/shap/shap

# Additional Resources I used
# https://platform.openai.com/docs/guides/prompt-engineering
# https://christophm.github.io/interpretable-ml-book/shapley.html
# https://www.aidancooper.co.uk/how-shapley-values-work/
# https://docs.python.org/3/library/threading.html
# 


class ShapValuesFrame(BaseFeatureFrame):
    def __init__(self, parent, controller):
        self.api_key = controller.api_key
        self.prompts = (
            controller.random_prompts if hasattr(controller, "random_prompts") else []
        )
        self.coalition_cache = {}  # cache for coalition outputs to reduce API call usage
        super().__init__(parent, controller, "SHAP Values")

    def create_content(self):
        content_container = ttk.Frame(self.content_frame)
        content_container.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)

        description_label = ttk.Label(
            content_container,
            text="SHAP (SHapley Additive exPlanations) Values measure each token's contribution to the model output by calculating its Shapley value, which represents its average marginal contribution across all possible combinations of tokens.",
            font=("Helvetica", 16),
            foreground="#FFFFFF",
            wraplength=800,
        )
        description_label.pack(anchor=tk.W, pady=(0, 20))

        self.status_vars = {} # status
        self.result_data = {}

        self.prompt_frames = {} # for each prompt

        progress_frame = ttk.Frame(content_container)
        progress_frame.pack(fill=tk.X, pady=10)

        progress_label = ttk.Label(
            progress_frame,
            text="Analysis Progress:",
            font=("Helvetica", 14),
            foreground="#FFFFFF",
        )
        progress_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            mode="determinate",
            length=300,
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        prompts_label = ttk.Label( # prompt section
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

            preview_text = prompt[:100] + "..." if len(prompt) > 100 else prompt
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

            self.status_vars[i] = tk.StringVar(value="Not started")

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

            calculate_button = ttk.Button( # calculate individual SHAP
                button_container,
                text="Calculate SHAP Values",
                command=lambda p=prompt, idx=i: self.calculate_shap_values(p, idx),
            )
            calculate_button.pack(side=tk.RIGHT, padx=5)

            self.status_vars[f"calculate_button_{i}"] = calculate_button

            heatmap_button = ttk.Button(
                button_container,
                text="Create Heatmap",
                state="disabled",
                command=lambda idx=i: self.create_heatmap(idx),
            )
            heatmap_button.pack(side=tk.RIGHT, padx=5)

            self.status_vars[f"heatmap_button_{i}"] = heatmap_button

            download_button = ttk.Button(
                button_container,
                text="Download Report",
                state="disabled",
                command=lambda idx=i: self.download_report(idx),
            )
            download_button.pack(side=tk.RIGHT, padx=5)

            self.status_vars[f"download_button_{i}"] = download_button

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

    def calculate_shap_values(self, prompt, prompt_idx):
        if not prompt.strip():
            messagebox.showwarning(
                "Empty Prompt", "The prompt is empty. Please enter a valid prompt."
            )
            return

        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showwarning(
                "API Key Required",
                "Please enter your OpenAI API key in the homepage settings.",
            )
            return

        calculate_button = self.status_vars.get(f"calculate_button_{prompt_idx}")
        if calculate_button:
            calculate_button.config(state="disabled")

        self.update_status(
            prompt_idx, "Processing...", "#FFA500"
        )  # Orange for processing

        self.progress_var.set(0)

        thread = threading.Thread( # THIS IS VERY IMPORTANT so UI can run, and calculation in bg
            target=self._calculate_shap_values_thread, args=(prompt, prompt_idx)
        )
        thread.daemon = True
        thread.start()

    def _calculate_shap_values_thread(self, prompt, prompt_idx):
        try:
            api_key = self.api_key.get().strip()
            max_tokens = None  # can set to something else like 15 compromising speed
            model = "gpt-3.5-turbo"

            self.content_frame.after(
                0, lambda: self.update_status(prompt_idx, "Tokenizing...", "#FFA500")
            )

            enc = tiktoken.encoding_for_model(model)
            tokens_ids = enc.encode(prompt)
            tokens = [
                enc.decode_single_token_bytes(token).decode("utf-8", errors="ignore")
                for token in tokens_ids
            ]

            if max_tokens and len(tokens) > max_tokens:  
                tokens_ids = tokens_ids[:max_tokens]
                tokens = tokens[:max_tokens]

            client = OpenAI(api_key=api_key)

            baseline_key = "baseline_empty" # caching
            baseline_output = self.coalition_cache.get(baseline_key)

            if not baseline_output:
                baseline_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": ""},
                    ],
                    max_tokens=20,
                    temperature=0,
                )
                baseline_output = baseline_response.choices[0].message.content
                self.coalition_cache[baseline_key] = baseline_output

            full_prompt_hash = hash(prompt)
            full_key = f"full_{full_prompt_hash}"
            full_output = self.coalition_cache.get(full_key)

            if not full_output:
                full_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=20,
                    temperature=0,
                )
                full_output = full_response.choices[0].message.content
                self.coalition_cache[full_key] = full_output

            self.content_frame.after(
                0,
                lambda: self.update_status(
                    prompt_idx, "Analyzing tokens...", "#FFA500"
                ),
            )
            significant_token_indices = []
            common_tokens = [ # will be removed but commend out if not needed
                " ",
                ".",
                ",",
                "!",
                "?",
                ":",
                ";",
                ")",
                "(",
                '"',
                "'",
                "-",
                "_",
                "the",
                "a",
                "an",
                "and",
                "of",
                "to",
                "in",
                "is",
                "that",
                "for",
            ]

            for i, token in enumerate(tokens): # skip common tokens for less api calls
                if token.lower() in common_tokens or not token.strip():
                    continue
                significant_token_indices.append(i)

            max_significant_tokens = None
            if (
                max_significant_tokens
                and len(significant_token_indices) > max_significant_tokens
            ):
                significant_token_indices = significant_token_indices[
                    :max_significant_tokens
                ]  # 8  further reduced

            total_tokens = len(significant_token_indices) # reduced sampling - target only 15-20 API calls total
            max_samples = 20  # even fewer samples

            # Determine optimal coalition sampling strategy
            coalition_samples = {}  # Focus mainly on single-token and two-token effects

            coalition_samples[0] = 1   #  check for empty coalition

            coalition_samples[total_tokens - 1] = 1  # focus on single token removals (most informative)

            remaining_samples = max_samples - 2 # add a few random small and medium-sized coalitions

            if total_tokens > 2: # distribute remaining samples with focus on small coalitions
                coalition_samples[1] = min(total_tokens, remaining_samples // 2) # single token
                remaining_samples -= coalition_samples.get(1, 0)

                if remaining_samples > 0 and total_tokens > 3:
                    mid_sizes = list(range(2, total_tokens - 1))
                    for size in mid_sizes:
                        if remaining_samples > 0:
                            coalition_samples[size] = 1
                            remaining_samples -= 1

            contribution_counts = {i: 0 for i in significant_token_indices} # tracking initialisation
            contribution_sums = {i: 0.0 for i in significant_token_indices}

            total_iterations = sum(coalition_samples.values()) # calc total iter
            progress_step = 100.0 / total_iterations if total_iterations > 0 else 100
            current_progress = 0

            for size, num_samples in coalition_samples.items(): # coalition size
                for _ in range(num_samples):
                    if size == 0:
                        coalition = []
                    elif size == total_tokens:
                        coalition = significant_token_indices.copy()
                    else:
                        coalition = random.sample(significant_token_indices, size)

                    included_tokens = []
                    for i, token_id in enumerate(tokens_ids):
                        if i in coalition or i not in significant_token_indices:
                            included_tokens.append(token_id)

                    coalition_text = enc.decode(included_tokens)

                    coalition_key = frozenset(coalition)
                    coalition_hash = hash(coalition_key)
                    cache_key = f"coalition_{coalition_hash}"

                    if cache_key in self.coalition_cache:
                        coalition_output = self.coalition_cache[cache_key]
                    else:
                        coalition_response = client.chat.completions.create(
                            model=model,
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a helpful assistant.",
                                },
                                {"role": "user", "content": coalition_text},
                            ],
                            max_tokens=20,
                            temperature=0,
                        )
                        coalition_output = coalition_response.choices[0].message.content
                        self.coalition_cache[cache_key] = coalition_output

                    # calculate coalition effect using simple length comparison for speed
                    # This is faster than TF-IDF for real quick results but less accurate
                    coalition_effect = abs(
                        len(baseline_output) - len(coalition_output)
                    ) / max(len(baseline_output), len(coalition_output), 1)

                    if size < total_tokens:
                        missing_tokens = [
                            t for t in significant_token_indices if t not in coalition
                        ]

                        for token_idx in missing_tokens:# for each token not in coalition, check its marginal contribution
                            if contribution_counts.get(token_idx, 0) >= 3:
                                continue

                            new_coalition = coalition + [token_idx]
                            new_coalition_key = frozenset(new_coalition)
                            new_coalition_hash = hash(new_coalition_key)
                            new_cache_key = f"coalition_{new_coalition_hash}"

                            if new_cache_key in self.coalition_cache:
                                new_coalition_output = self.coalition_cache[
                                    new_cache_key
                                ]
                            else:
                                included_tokens = []
                                for i, token_id in enumerate(tokens_ids):
                                    if (
                                        i in new_coalition
                                        or i not in significant_token_indices
                                    ):
                                        included_tokens.append(token_id)

                                new_coalition_text = enc.decode(included_tokens)

                                new_coalition_response = client.chat.completions.create(
                                    model=model,
                                    messages=[
                                        {
                                            "role": "system",
                                            "content": "You are a helpful assistant.",
                                        },
                                        {"role": "user", "content": new_coalition_text},
                                    ],
                                    max_tokens=20,
                                    temperature=0,
                                )
                                new_coalition_output = new_coalition_response.choices[
                                    0
                                ].message.content
                                self.coalition_cache[new_cache_key] = (
                                    new_coalition_output
                                )

                            new_coalition_effect = abs(
                                len(baseline_output) - len(new_coalition_output)
                            ) / max(len(baseline_output), len(new_coalition_output), 1)

                            marginal_contribution = (
                                new_coalition_effect - coalition_effect
                            )

                            contribution_counts[token_idx] = (
                                contribution_counts.get(token_idx, 0) + 1
                            )
                            contribution_sums[token_idx] = (
                                contribution_sums.get(token_idx, 0)
                                + marginal_contribution
                            )

                    current_progress += progress_step
                    self.content_frame.after(
                        0, lambda p=current_progress: self.progress_var.set(min(p, 100))
                    )

            token_data = []
            for idx in significant_token_indices:
                count = contribution_counts.get(idx, 0)
                if count > 0:
                    avg_contribution = contribution_sums.get(idx, 0) / count
                    token_data.append(
                        {
                            "token": tokens[idx],
                            "importance": float(avg_contribution),
                            "position": idx,
                        }
                    )
                else: # if cant analyse
                    token_data.append(
                        {
                            "token": tokens[idx],
                            "importance": 0.0,
                            "position": idx,
                        }
                    )

            for i, token in enumerate(tokens): # skipped tokens
                if i not in significant_token_indices:
                    token_data.append(
                        {
                            "token": token,
                            "importance": 0.0,
                            "position": i,
                        }
                    )

            if token_data: #normalize using min max 
                importance_values = [td["importance"] for td in token_data]
                min_value = min(importance_values)
                max_value = max(importance_values)

                if max_value > min_value:
                    for td in token_data:
                        td["importance"] = (td["importance"] - min_value) / (
                            max_value - min_value
                        )

            # sort by importance
            token_data.sort(key=lambda x: x["importance"], reverse=True)

            report = {
                "prompt": prompt,
                "tokens": token_data,
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "baseline_output": baseline_output,
                "full_output": full_output,
                "api_key": api_key,
            }

            self.result_data[prompt_idx] = report # store results

            self.content_frame.after(
                100,
                lambda: self.update_ui_after_calculation(prompt_idx, True),
            )

        except Exception as e:
            error_msg = str(e)
            print(f"Error in calculation thread: {error_msg}")  # print to terminal
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

        if success:
            self.update_status(prompt_idx, "Completed", "#4CAF50")  # Green for success
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

            messagebox.showerror("Calculation Error", f"{error_msg}")

    def display_results(self, prompt_idx): # visuals container 
        viz_container = self.status_vars.get(f"viz_container_{prompt_idx}")
        if not viz_container:
            return

        for widget in viz_container.winfo_children(): # clear prev results
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

        top_tokens = token_data[:5]

        token_display = ttk.Frame(tokens_frame)
        token_display.pack(fill=tk.X, padx=10, pady=5)

        for token_info in top_tokens: # colour correspond to importance
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
                font=("Consofiledialoglas", 10),
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

        # Ask user for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save SHAP Values Report",
        )

        if not file_path: # cancel by user
            return  

        try:
            from features.methods.shap_values.report_writer import (
                write_shap_importance_report,
            )

            success = write_shap_importance_report(file_path, result)

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

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save SHAP Heatmap Visualization",
        )

        if not file_path:
            return  # user canceled

        try:
            from features.methods.shap_values.heatmap_generator import (
                generate_shap_heatmap,
            )

            success = generate_shap_heatmap(result, file_path)

            if success:
                messagebox.showinfo(
                    "Heatmap Created",
                    f"SHAP heatmap visualization saved successfully to {file_path}",
                )
            else:
                messagebox.showerror(
                    "Error", "Failed to create heatmap. Please try again."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create heatmap: {str(e)}")

    def batch_calculate_all(self):
        confirm = messagebox.askyesno(
            "Batch Process",
            "This will calculate SHAP values for all prompts. This process can be time-consuming. Proceed?",
        )

        if not confirm:
            return

        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showwarning(
                "API Key Required",
                "Please enter your OpenAI API key in the homepage settings.",
            )
            return

        for i, prompt in enumerate(self.prompts, 1):
            if not prompt.strip():
                continue

            self.calculate_shap_values(prompt, i) # avoid freezing else you will have issues with threading
            time.sleep(0.5)
