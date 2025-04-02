# cosine report writer
def write_token_importance_report(file_path, result_data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("TOKEN IMPORTANCE ANALYSIS\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Analysis Date: {result_data.get('timestamp', 'Unknown')}\n")
            f.write(f"Model: {result_data.get('model', 'Unknown')}\n")
            f.write(
                f"Embedding Model: {result_data.get('embedding_model', 'Unknown')}\n\n"
            )

            f.write("ORIGINAL PROMPT:\n")
            f.write("-" * 50 + "\n")
            original_prompt = result_data.get("prompt", "Unknown")
            f.write(f"{original_prompt}\n\n")

            original_response = result_data.get("original_response", "")
            if original_response:
                f.write("ORIGINAL API RESPONSE:\n")
                f.write("-" * 50 + "\n")
                f.write(f"{original_response}\n\n")

            f.write("TOKEN IMPORTANCE ANALYSIS:\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'TOKEN':<20} {'IMPORTANCE':<15} {'POSITION':<10}\n")
            f.write("-" * 50 + "\n")

            tokens = result_data.get("tokens", [])

            sorted_tokens = sorted(
                tokens, key=lambda x: x.get("importance", 0), reverse=True
            )

            for token_data in sorted_tokens:
                token = token_data.get("token", "").replace("\n", "\\n")[:20]
                importance = token_data.get("importance", 0)
                position = token_data.get("position", 0)

                f.write(f"{token:<20} {importance:<15.4f} {position:<10}\n")

            try:
                import tiktoken
                from openai import OpenAI

                enc = tiktoken.encoding_for_model(
                    result_data.get("model", "gpt-3.5-turbo")
                )
                token_ids = enc.encode(original_prompt)
                original_tokens = [
                    enc.decode_single_token_bytes(token).decode(
                        "utf-8", errors="ignore"
                    )
                    for token in token_ids
                ]

                f.write(
                    "\nPROMPTS WITH INDIVIDUAL TOKENS REMOVED AND THEIR RESPONSES:\n"
                )
                f.write("=" * 50 + "\n\n")

                api_key = result_data.get("api_key", "")
                can_get_responses = bool(api_key)

                if not can_get_responses:
                    f.write(
                        "NOTE: API responses not available - API key not provided in result data.\n\n"
                    )

                client = None
                if can_get_responses:
                    try:
                        client = OpenAI(api_key=api_key)
                    except Exception as e:
                        f.write(
                            f"ERROR: Could not initialize OpenAI client: {str(e)}\n\n"
                        )
                        can_get_responses = False

                for token_data in sorted_tokens:
                    token_text = token_data.get("token", "")
                    position = token_data.get("position")
                    importance = token_data.get("importance", 0)

                    if position is None:
                        continue

                    new_tokens = original_tokens.copy()
                    if position < len(new_tokens):
                        display_token = token_text.replace("\n", "\\n").replace(
                            "\t", "\\t"
                        )
                        if display_token.isspace():
                            display_token = f"[whitespace]"

                        new_prompt = "".join(new_tokens)

                        f.write(
                            f"TOKEN REMOVED: '{display_token}' (Position: {position}, Importance: {importance:.4f})\n"
                        )
                        f.write("-" * 50 + "\n")
                        f.write(f"MODIFIED PROMPT:\n{new_prompt}\n\n")

                        if can_get_responses and client:
                            try:
                                response = client.chat.completions.create(
                                    model=result_data.get("model", "gpt-3.5-turbo"),
                                    messages=[{"role": "user", "content": new_prompt}],
                                    temperature=0,
                                )

                                response_text = response.choices[0].message.content
                                f.write(f"API RESPONSE WITH TOKEN REMOVED:\n")
                                f.write("-" * 50 + "\n")
                                f.write(f"{response_text}\n\n")

                            except Exception as e:
                                f.write(f"ERROR GETTING RESPONSE: {str(e)}\n\n")

                        f.write("=" * 50 + "\n\n")

            except ImportError as e:
                f.write(
                    f"\nNote: Could not generate prompts with tokens removed - required package not found: {str(e)}.\n"
                )
            except Exception as e:
                f.write(f"\nError generating prompts with tokens removed: {str(e)}\n")

        return True
    except Exception as e:
        print(f"Error writing report: {str(e)}")
        return False
