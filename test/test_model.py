import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(ROOT)
)

from model import TermuxAI


def main():

    ai = TermuxAI()

    tests = [
        "Hello!",
        "Who are you?",
        "What is 25 * 4?",
        "What time is it?",
        "What is the date?",
        "What is Minecraft?",
        "What is Sodium?",
        "Remember that I like Minecraft",
        "What do you know about Minecraft?",
        "Forget that I like Minecraft",
        "Search for Minecraft Sodium",
        "Open Minecraft",
        "I like building things.",
        "Goodbye!",
    ]

    print("=" * 60)
    print("TERMUX AI MODEL TEST")
    print("=" * 60)

    for message in tests:

        print()
        print(f"USER: {message}")

        result = ai.process(
            message
        )

        print(
            f"INTENT: {result['parsed']['intent']}"
        )

        print(
            f"AI: {result['response']}"
        )

    print()
    print("=" * 60)
    print("MODEL TEST COMPLETE ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()