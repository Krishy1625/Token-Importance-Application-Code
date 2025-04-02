# data_handler.py

import os
import tkinter.messagebox as messagebox


# make it crash proof
def check_for_custom_dataset():
    custom_set_path = os.path.join(os.getcwd(), "CustomSet.txt")
    if not os.path.exists(custom_set_path):
        try:
            with open(custom_set_path, "w", encoding="utf-8") as f:
                f.write("# Add your custom prompts here (one per line)\n")
        except Exception as e:
            messagebox.showwarning(
                "Warning", f"Failed to create CustomSet.txt: {str(e)}"
            )


def load_custom_dataset():
    custom_prompts = []

    try:
        file_path = os.path.join(os.getcwd(), "CustomSet.txt")

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if line and not line.startswith(
                    "#"
                ):  # useful if u want to add comments in dataset
                    custom_prompts.append(line)

            return custom_prompts
        else:  # creates file u can paste into
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# Add your custom prompts here (one per line)\n")
            return []
    except Exception as e:
        print(f"Error loading custom dataset: {str(e)}")
        return []
