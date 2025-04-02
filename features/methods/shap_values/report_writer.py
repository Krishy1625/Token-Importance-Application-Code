# shaps report writer
def write_shap_importance_report(file_path, result_data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            # header
            f.write("SHAP TOKEN IMPORTANCE ANALYSIS\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Analysis Date: {result_data.get('timestamp', 'Unknown')}\n")
            f.write(f"Model: {result_data.get('model', 'Unknown')}\n\n")

            f.write("ORIGINAL PROMPT:\n")
            f.write("-" * 50 + "\n")
            original_prompt = result_data.get("prompt", "Unknown")
            f.write(f"{original_prompt}\n\n")

            baseline_output = result_data.get("baseline_output", "")

            f.write("BASELINE MODEL OUTPUT (empty prompt):\n")
            f.write("-" * 50 + "\n")
            f.write(f"{baseline_output}\n\n")

            f.write("TOKEN SHAP VALUES:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'TOKEN':<20} {'SHAP VALUE':<15} {'POSITION':<10}\n")
            f.write("-" * 50 + "\n")

            # Get token data
            tokens = result_data.get("tokens", [])

            sorted_tokens = sorted(  # Sort tokens by importance
                tokens, key=lambda x: x.get("importance", 0), reverse=True
            )

            # write each token's data and display of special characters
            for token_data in sorted_tokens:
                token = token_data.get("token", "")
                if token == "\n":
                    token_display = "\\n"
                elif token == "\t":
                    token_display = "\\t"
                elif token.isspace():
                    token_display = "[space]"
                else:
                    token_display = token

                token_display = token_display[:20]  # limit

                importance = token_data.get("importance", 0)
                position = token_data.get("position", 0)

                f.write(f"{token_display:<20} {importance:<15.4f} {position:<10}\n")
        return True
    except Exception as e:  # error handling
        print(f"Error writing SHAP report: {str(e)}")
        return False
