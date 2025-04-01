#  This is main.py
#  Main entry point for the Application


import tkinter as tk
import os
import sys
from app import TokenImportanceApp
from utils.themes import apply_theme


def main():  # entry point for the application!
    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )  ## https://www.geeksforgeeks.org/python-os-path-abspath-method-with-example/
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    root = tk.Tk()  # root window creation

    apply_theme(root)  # apply dark theme to the root window

    app = TokenImportanceApp(root)  # create the app

    # gui positioning
    window_width = 1400
    window_height = 900
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
