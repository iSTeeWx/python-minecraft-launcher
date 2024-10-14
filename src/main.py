import api
import os


def main() -> None:
    script_path = os.path.abspath(__file__)
    root = os.path.dirname(os.path.dirname(script_path))
    api.start_game(f"{root}/game-dir", "1.8.9")


if __name__ == '__main__':
    main()
