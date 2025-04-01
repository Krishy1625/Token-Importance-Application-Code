# app.py
# glues the frames
# has msgs for features
# used code / information from
# https://python-course.eu/tkinter/variable-classes-in-tkinter.php
# https://www.geeksforgeeks.org/python-setting-and-retrieving-values-of-tkinter-variable/
# https://www.w3schools.com/python/python_json.asp


import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import random

from frames.homepage_frame import HomepageFrame
from frames.prompts_frame import PromptsFrame
from frames.features_frame import FeaturesFrame
from features import FEATURE_FRAMES
from utils.themes import apply_theme, show_success_message
from utils.data_handler import load_custom_dataset, check_for_custom_dataset


class TokenImportanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Token Importance Application")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)

        apply_theme(self.root)  # dark mode

        self.setup_custom_styles()

        self.api_key = (
            tk.StringVar()
        )  # https://www.askpython.com/python-modules/tkinter/stringvar-with-examples

        self.selected_dataset = tk.StringVar(value="CustomSet")  # currently custom set

        self.num_prompts = tk.IntVar(
            value=3
        )  # https://python-course.eu/tkinter/variable-classes-in-tkinter.php

        # default no. of prompts is 3

        self.show_key = tk.BooleanVar(
            value=False
        )  # toggle for showing/hiding the API key

        self.config_file = os.path.join(
            os.getcwd(), ".api_config.json"
        )  # save user setting for convinience

        self.datasets = ["CustomSet"]

        check_for_custom_dataset()

        self.random_prompts = []  # store random prompts

        self.display_tokens_enabled = tk.BooleanVar(value=True)

        self.method_cosine = tk.BooleanVar(value=True)

        self.method_shap = tk.BooleanVar(value=True)

        # Token pruning variables removed

        self.load_config()  # load settings from previous sessions

        self.container = ttk.Frame(self.root)  #  hold all different screens
        self.container.pack(fill=tk.BOTH, expand=True)

        self.frames = {}  # dictionary to keep track of all our UI screens/frames

        self.init_frames()  # Set up the initial frames (just homepage for now)

        self.show_frame("Homepage")  # first page

    def setup_custom_styles(self):  # button styling
        style = ttk.Style()
        style.configure(
            "FeatureBg.TFrame",
            background="#1E1E1E",
            borderwidth=1,
            relief="solid",
        )
        style.configure(
            "TokensFrame.TFrame", background="#1E1E1E", borderwidth=1, relief="solid"
        )

    def init_frames(self):  # set ui frames
        self.frames["Homepage"] = HomepageFrame(
            self.container,
            self,  # pass the main app as controller
            self.api_key,
            self.selected_dataset,
            self.num_prompts,
            self.show_key,
        )

        # rest of the frames made when needed

    def load_config(self):  # get the previous settings from config file
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
            self.api_key.set(config.get("api_key", ""))  # get api key else empty string
            self.selected_dataset.set("CustomSet")
            self.num_prompts.set(config.get("num_prompts", 3))
        else:
            pass  # well ideally could run app without crash but if need put in something

    def save_config(self):  # save settings for convinience
        if not self.api_key.get().strip():
            messagebox.showwarning(
                "Warning",
                "API Key cannot be empty, if you only want the tokenisation then put anything and continue.",
            )
            return False

        config = {
            "api_key": self.api_key.get(),
            "dataset": "CustomSet",  # always CustomSet for now
            "num_prompts": self.num_prompts.get(),
        }

        try:
            with open(
                self.config_file, "w"
            ) as f:  # write the settings to the config file
                json.dump(config, f)

            # let the user know it worked
            show_success_message(self.root, "Configuration saved successfully.")
            return True
        except Exception as e:  # something wrong happened
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            return False

    def generate_random_prompts(self):  # get random prompts
        self.random_prompts = []

        try:
            custom_prompts = load_custom_dataset()

            if custom_prompts and len(custom_prompts) > 0:
                available_prompts = custom_prompts
            else:  # no custom prompts found - show empty list
                available_prompts = []
                messagebox.showinfo(
                    "Information",
                    "CustomSet.txt is empty or not found. No prompts to display.",
                )

            if len(available_prompts) < self.num_prompts.get():
                available_prompts_sample = available_prompts
            else:
                available_prompts_sample = random.sample(
                    available_prompts, self.num_prompts.get()
                )
            for prompt in available_prompts_sample:
                self.random_prompts.append(prompt)

        except Exception as e:  # error handling for dataset
            self.random_prompts = []
            messagebox.showwarning(
                "Dataset Error",
                f"Error loading custom dataset: {str(e)}\nNo prompts to display.",
            )

    def show_frame(self, frame_id):  # switch frames
        for name, frame in self.frames.items():
            frame.pack_forget()

        if frame_id not in self.frames:  # create intitial frames 1st time
            if frame_id == "PromptsPage":
                self.generate_random_prompts()
                self.frames[frame_id] = PromptsFrame(
                    self.container, self, self.random_prompts, self.num_prompts
                )
            elif frame_id == "FeaturesPage":
                self.frames[frame_id] = FeaturesFrame(  # pass feat settings
                    self.container,
                    self,
                    self.display_tokens_enabled,
                    self.method_cosine,
                    self.method_shap,
                    # Removed prune_enabled and prune_threshold_var
                )
            elif frame_id in FEATURE_FRAMES:  # spec frames
                frame_class = FEATURE_FRAMES[frame_id]
                self.frames[frame_id] = frame_class(self.container, self)

        self.frames[frame_id].pack(fill=tk.BOTH, expand=True)

        if frame_id == "Homepage":  # upd title
            self.root.title("Token Importance Application - Homepage")
        elif frame_id == "PromptsPage":
            self.root.title("Token Importance Application - Prompts")
        elif frame_id == "FeaturesPage":
            self.root.title("Token Importance Application - Features")
        else:  # feat specific titles
            frame_title = getattr(
                self.frames[frame_id], "title_text", frame_id.replace("_", " ").title()
            )
            self.root.title(f"Token Importance Application - {frame_title}")

    def open_feature_page(self, feature_id):  # spec analysis frame
        if feature_id in self.frames:
            self.frames[feature_id].destroy()
            del self.frames[feature_id]
        self.show_frame(feature_id)

    def go_to_prompts_page(self):
        if not self.api_key.get().strip():
            messagebox.showwarning(
                "Warning",
                "API Key cannot be empty, if you only want the tokenisation then put anything and continue.",
            )
            return

        if self.save_config():
            self.generate_random_prompts()

            if "PromptsPage" in self.frames:
                self.frames["PromptsPage"].destroy()  # rem existing frames
                del self.frames["PromptsPage"]

            self.show_frame("PromptsPage")

    def go_to_features_page(self):
        self.show_frame("FeaturesPage")

    def go_to_homepage(self):
        self.show_frame("Homepage")

    def refresh_prompts(self):  # if ya dont like the prompt
        self.generate_random_prompts()

        if "PromptsPage" in self.frames:
            self.frames["PromptsPage"].destroy()
            del self.frames["PromptsPage"]

        self.show_frame("PromptsPage")

        # Let the user know it worked
        show_success_message(self.root, "Generated new prompts successfully.")

    # waiting msgs
    def run_analysis(self):
        if not any([self.method_cosine.get(), self.method_shap.get()]):
            messagebox.showwarning(
                "No Methods Selected", "Please enable at least one analysis method."
            )
            return
        messagebox.showinfo(
            "Processing",
            "Analysis has started. This may take some time depending on the selected options.",
        )
        show_success_message(self.root, "Analysis completed successfully!")