# themes .py
# themes to make gui look better (dark)

# refs :
#  https://tkdocs.com/tutorial/styles.html
# https://docs.python.org/3/library/tkinter.ttk.html

import tkinter as tk
from tkinter import ttk


class ModernDarkTheme(ttk.Style):
    def __init__(self):
        super().__init__()
        self.theme_create(
            "ModernDark",
            parent="alt",
            settings={
                ".": {
                    "configure": {
                        "background": "#121212",
                        "foreground": "#FFFFFF",
                        "bordercolor": "#333333",
                        "darkcolor": "#333333",
                        "lightcolor": "#444444",
                        "troughcolor": "#333333",
                        "fieldbackground": "#1E1E1E",
                        "font": ("Helvetica", 14),
                        "borderwidth": 1,
                    }
                },
                "TFrame": {
                    "configure": {
                        "background": "#121212",
                        "borderwidth": 0,
                    }
                },
                "TLabel": {
                    "configure": {
                        "background": "#121212",
                        "foreground": "#FFFFFF",
                        "font": ("Helvetica", 14),
                    }
                },
                "TButton": {
                    "configure": {
                        "background": "#007BFF",
                        "foreground": "#FFFFFF",
                        "padding": (10, 8),
                        "font": ("Helvetica", 14, "bold"),
                        "borderwidth": 0,
                    },
                    "map": {
                        "background": [("active", "#0069D9"), ("disabled", "#444444")],
                        "foreground": [("disabled", "#888888")],
                    },
                },
                "Accent.TButton": {
                    "configure": {
                        "background": "#6C3CE9",
                        "foreground": "#FFFFFF",
                        "padding": (14, 10),
                        "font": ("Helvetica", 16, "bold"),
                        "borderwidth": 0,
                    },
                    "map": {
                        "background": [("active", "#5731BC"), ("disabled", "#444444")],
                        "foreground": [("disabled", "#888888")],
                    },
                },
                "TEntry": {
                    "configure": {
                        "fieldbackground": "#1E1E1E",
                        "foreground": "#FFFFFF",
                        "bordercolor": "#444444",
                        "lightcolor": "#444444",
                        "darkcolor": "#444444",
                        "insertcolor": "#FFFFFF",
                        "padding": 8,
                        "font": ("Helvetica", 14),
                    }
                },
                "TCheckbutton": {
                    "configure": {
                        "background": "#121212",
                        "foreground": "#FFFFFF",
                        "font": ("Helvetica", 14),
                    },
                    "map": {
                        "background": [("active", "#121212")],
                        "foreground": [("disabled", "#888888")],
                    },
                },
                "TCombobox": {
                    "configure": {
                        "fieldbackground": "#1E1E1E",
                        "foreground": "#FFFFFF",
                        "background": "#1E1E1E",
                        "bordercolor": "#444444",
                        "lightcolor": "#444444",
                        "darkcolor": "#444444",
                        "arrowcolor": "#FFFFFF",
                        "padding": 8,
                        "font": ("Helvetica", 14),
                    },
                    "map": {
                        "fieldbackground": [("readonly", "#1E1E1E")],
                        "foreground": [("readonly", "#FFFFFF")],
                        "selectbackground": [("readonly", "#1E1E1E")],
                        "selectforeground": [("readonly", "#FFFFFF")],
                    },
                },
                "TLabelframe": {
                    "configure": {
                        "background": "#121212",
                        "foreground": "#FFFFFF",
                        "bordercolor": "#444444",
                        "lightcolor": "#444444",
                        "darkcolor": "#444444",
                        "borderwidth": 1,
                        "relief": "solid",
                        "padding": 15,
                    }
                },
                "TLabelframe.Label": {
                    "configure": {
                        "background": "#121212",
                        "foreground": "#FFFFFF",
                        "font": ("Helvetica", 16, "bold"),
                    }
                },
            },
        )
        self.theme_use("ModernDark")


def apply_theme(root):  # dark theme apply
    root.configure(background="#121212")

    style = ttk.Style()
    existing_themes = style.theme_names()

    if "ModernDark" not in existing_themes:  # check if alr being used
        ModernDarkTheme()
    else:
        style.theme_use("ModernDark")

    return root


def show_success_message(root, message):  # success msg popup match theme
    success_window = tk.Toplevel(root)
    success_window.title("Success")
    success_window.geometry("400x200")
    success_window.configure(bg="#121212")
    success_window.transient(root)
    success_window.grab_set()

    x = root.winfo_x() + (root.winfo_width() // 2) - 200
    y = root.winfo_y() + (root.winfo_height() // 2) - 100
    success_window.geometry(f"+{x}+{y}")

    success_frame = tk.Frame(success_window, bg="#121212")
    success_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    success_canvas = tk.Canvas(
        success_frame, width=50, height=50, bg="#121212", highlightthickness=0
    )
    success_canvas.pack(pady=(10, 20))
    success_canvas.create_oval(5, 5, 45, 45, outline="#4CAF50", width=3)
    success_canvas.create_line(15, 25, 25, 35, 38, 15, fill="#4CAF50", width=3)

    message_label = tk.Label(
        success_frame, text=message, bg="#121212", fg="#FFFFFF", font=("Helvetica", 14)
    )
    message_label.pack(pady=10)

    ok_button = tk.Button(
        success_frame,
        text="OK",
        command=success_window.destroy,
        bg="#6C3CE9",
        fg="#FFFFFF",
        font=("Helvetica", 12, "bold"),
        padx=20,
        pady=5,
        relief=tk.FLAT,
        activebackground="#5731BC",
        activeforeground="#FFFFFF",
    )
    ok_button.pack(pady=10)

    success_window.after(3000, success_window.destroy)
