# display tokens report generator
import datetime
from tkinter import filedialog


def generate_token_report(prompts, tokenizer, filename=None):
    if filename is None:
        # default timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"token_report_{timestamp}.txt"

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Save Token Report As",
        )

        if not filename:
            return None

    with open(filename, "w", encoding="utf-8") as f:
        f.write(
            f"Token Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        f.write(f"Tokenizer: cl100k_base (used by GPT-4 and ChatGPT)\n\n")

        for i, prompt in enumerate(prompts, 1):
            f.write(f"Prompt {i}:\n")
            f.write("-" * 80 + "\n")
            f.write(prompt + "\n")
            f.write("-" * 80 + "\n")

            token_ids = tokenizer.encode(prompt)  # token info
            f.write(f"Total tokens: {len(token_ids)}\n\n")

            f.write("Token breakdown:\n")
            f.write(f"{'Index':<10}{'Token Text':<50}{'Token ID':<10}\n")
            f.write("-" * 70 + "\n")

            for j, token_id in enumerate(token_ids):
                token_text = tokenizer.decode([token_id])

                if token_text == "\n":
                    token_text_display = "\\n"
                elif token_text == "\t":
                    token_text_display = "\\t"
                elif token_text == " ":
                    token_text_display = "·"
                elif len(token_text.strip()) == 0 and len(token_text) > 1:
                    token_text_display = "·" * len(token_text)
                else:
                    token_text_display = token_text

                f.write(f"{j:<10}{token_text_display:<50}{token_id:<10}\n")

            f.write("\n\n")

        # add summary
        total_tokens = sum(len(tokenizer.encode(p)) for p in prompts)
        f.write(f"Summary:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total prompts: {len(prompts)}\n")
        f.write(f"Total tokens across all prompts: {total_tokens}\n")
    return filename
