#!/usr/bin/env python3
"""Save Yelp Fusion API key to final/.env (not committed to git)."""
import getpass
import re
import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def main():
    if len(sys.argv) > 1:
        key = sys.argv[1].strip()
    else:
        print("Paste your Yelp Fusion API key (input hidden):")
        key = getpass.getpass("YELP_API_KEY: ").strip()

    if not key or len(key) < 20:
        print("That does not look like a valid API key. Get one at:")
        print("  https://www.yelp.com/developers/v3/manage_app")
        sys.exit(1)

    text = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.exists() else ""
    if re.search(r"^YELP_API_KEY=.*$", text, re.MULTILINE):
        text = re.sub(r"^YELP_API_KEY=.*$", f"YELP_API_KEY={key}", text, flags=re.MULTILINE)
    else:
        text = text.rstrip() + f"\nYELP_API_KEY={key}\n"
    ENV_PATH.write_text(text, encoding="utf-8")
    print(f"Saved to {ENV_PATH}. Restart Flask, then check /health for yelp_configured: true")


if __name__ == "__main__":
    main()
