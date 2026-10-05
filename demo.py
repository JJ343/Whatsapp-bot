"""Offline demo: chat with the bot in your terminal, no WhatsApp needed.

Usage:
    python demo.py
    python demo.py --lang es
"""

import argparse
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from bot_logic import get_menu, get_user_lang, process_message

DEMO_SCRIPT = [
    ("user", "hola"),
    ("user", "2"),
    ("user", "cotizar"),
    ("user", "Juan, HP Pavilion 15, CDMX, budget 3000 MXN"),
    ("user", "4"),
    ("user", "menu"),
    ("user", "english"),
    ("user", "2"),
]


def run_scripted() -> None:
    user = "demo-user"
    print("=== Scripted demo (no WhatsApp required) ===\n")
    for role, text in DEMO_SCRIPT:
        print(f"You: {text}")
        reply = process_message(user, text)
        print(f"Bot [{get_user_lang(user)}]:\n{reply}\n")
        print("-" * 60)


def run_interactive(default_lang: str = "en") -> None:
    user = "local-user"
    print("=== Interactive demo ===")
    print("Type messages like in WhatsApp. Commands: menu, quit.\n")
    print(get_menu(default_lang))
    while True:
        try:
            text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if text.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break
        if not text:
            continue
        print(f"\nBot:\n{process_message(user, text)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline WhatsApp bot demo")
    parser.add_argument("--lang", default="en", choices=["en", "es"])
    parser.add_argument("--scripted", action="store_true",
                        help="Run the scripted conversation and exit")
    args = parser.parse_args()

    if args.scripted:
        run_scripted()
    else:
        # Show the scripted version first so reviewers see value in 10 seconds,
        # then drop into interactive mode.
        run_scripted()
        run_interactive(args.lang)
