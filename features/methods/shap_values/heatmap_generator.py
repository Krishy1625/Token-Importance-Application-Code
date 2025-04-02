# heatmap generator for shap
# https://matplotlib.org/stable/index.html docs
# https://seaborn.pydata.org/tutorial/color_palettes.html docs
import matplotlib.pyplot as plt
from datetime import datetime


def generate_shap_heatmap(result_data, output_path):
    try:  # get tokens
        tokens_data = result_data.get("tokens", [])
        if not tokens_data:
            print("No token data available")
            return False

        importance_by_position = {}
        for token in tokens_data:
            position = token.get("position")
            importance = token.get("importance", 0)
            token_text = token.get("token", "")
            if position is not None:
                importance_by_position[position] = (importance, token_text)

        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)

        sorted_positions = sorted(importance_by_position.keys())
        display_tokens = []
        importance_values = []

        for pos in sorted_positions:
            importance, token = importance_by_position[pos]
            if token.isspace():
                display_token = "SPACE"
            elif token == "\n":
                display_token = "NEW LINE"
            elif token == "\t":
                display_token = "TAB"
            else:
                display_token = token

            display_tokens.append(display_token)
            importance_values.append(importance)

        cmap = plt.cm.Blues  # colour

        plt.imshow([importance_values], cmap=cmap, aspect="auto")
        plt.colorbar(label="SHAP Value")
        plt.title("Token SHAP Values Heatmap")
        plt.yticks([])

        plt.xticks(range(len(display_tokens)), display_tokens, rotation=45, ha="right")

        plt.subplot(2, 1, 2)

        sorted_token_data = sorted(  # sort tokensby imp
            tokens_data, key=lambda x: x.get("importance", 0), reverse=True
        )

        top_n = min(10, len(sorted_token_data))  # top 10 only
        top_tokens = sorted_token_data[:top_n]

        bar_tokens = []
        bar_values = []
        for token_info in top_tokens:
            token_text = token_info.get("token", "")
            if token_text.isspace():
                token_text = "SPACE"
            elif token_text == "\n":
                token_text = "NEWLINE"
            elif token_text == "\t":
                token_text = "TAB"

            bar_tokens.append(token_text)
            bar_values.append(token_info.get("importance", 0))

        bars = plt.bar(range(len(bar_tokens)), bar_values, color="skyblue")
        plt.xticks(range(len(bar_tokens)), bar_tokens, rotation=45, ha="right")
        plt.ylabel("SHAP Value")
        plt.title("Top Tokens by SHAP Value")

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
            0.5,
            0.01,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Model: {result_data.get('model', 'Unknown')}",
            ha="center",
            fontsize=8,
            bbox=dict(facecolor="white", alpha=0.5),
        )

        plt.tight_layout(rect=[0, 0.03, 1, 1])

        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        return True

    except Exception as e:
        print(f"Error generating SHAP heatmap: {str(e)}")
        return False
