# heatmap for cosine sim
# code follows similar style to shap / heatmap_generator
# https://matplotlib.org/stable/index.html docs
# https://seaborn.pydata.org/tutorial/color_palettes.html docs

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime


def generate_token_heatmap(result_data, output_path):
    try:
        tokens_data = result_data.get("tokens", [])

        if not tokens_data:
            print("No token data available")
            return False

        sns.set(style="whitegrid")

        token_map = {}
        for token in tokens_data:
            position = token.get("position")
            importance = token.get("importance", 0)
            text = token.get("token", "")
            if position is not None:
                token_map[position] = {"importance": importance, "text": text}

        plt.figure(figsize=(14, 10))
        plt.subplot(2, 1, 1)

        positions = []
        text_tokens = []
        importance_values = []

        for pos in sorted(token_map.keys()):
            positions.append(pos)
            text = token_map[pos]["text"]
            if text.isspace():
                text = "SPACE"
            text_tokens.append(text)
            importance_values.append(token_map[pos]["importance"])

        importance_matrix = np.array(importance_values).reshape(1, -1)

        ax = sns.heatmap(
            importance_matrix,
            cmap="Blues",
            annot=np.array(text_tokens).reshape(1, -1),
            fmt="",
            cbar_kws={"label": "Importance Score"},
            linewidths=0.5,
        )

        ax.set_yticks([])
        ax.set_ylabel("")

        ax.set_xticks(np.arange(len(positions)) + 0.5)
        ax.set_xticklabels(positions)

        plt.title("Token Importance Heatmap (Cosine Similarity)", fontsize=14)

        plt.subplot(2, 1, 2)

        sorted_tokens = sorted(
            tokens_data, key=lambda x: x.get("importance", 0), reverse=True
        )

        top_n = min(15, len(sorted_tokens))
        top_tokens = sorted_tokens[:top_n]

        token_texts = []
        token_importances = []

        for token in top_tokens:
            text = token.get("token", "")
            importance = token.get("importance", 0)

            if text.isspace():
                if text == " ":
                    text = "SPACE"
                elif text == "\n":
                    text = "NEWLINE"
                elif text == "\t":
                    text = "TAB"
                else:
                    text = f"[whitespace:{len(text)}]"

            token_texts.append(text)
            token_importances.append(importance)

        bars = plt.bar(
            range(len(token_texts)),
            token_importances,
            color=sns.color_palette("Blues_r", n_colors=len(token_texts)),
        )

        plt.xlabel("Tokens")
        plt.ylabel("Importance Score")
        plt.title("Top Tokens by Importance (Cosine Similarity)", fontsize=14)

        plt.xticks(range(len(token_texts)), token_texts, rotation=45, ha="right")

        for bar in bars:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.01,
                f"{height:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        plt.figtext(  # metadata
            0.02,
            0.02,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            fontsize=8,
        )
        plt.figtext(
            0.02, 0.04, f"Model: {result_data.get('model', 'Unknown')}", fontsize=8
        )
        plt.figtext(
            0.02,
            0.06,
            f"Embedding: {result_data.get('embedding_model', 'Unknown')}",
            fontsize=8,
        )

        explanation = (
            "This visualization shows token importance calculated using cosine similarity.\n"
            "Higher values indicate tokens that have more impact on the meaning of the prompt."
        )
        plt.figtext(
            0.5,
            0.01,
            explanation,
            ha="center",
            fontsize=10,
            bbox=dict(facecolor="white", alpha=0.8),
        )

        plt.tight_layout()
        plt.subplots_adjust(bottom=0.15)

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()
        return True

    except Exception as e:
        print(f"Error generating heatmap: {str(e)}")
        return False
