import subprocess

import json_parser


def start_game(directory: str, version_name: str) -> None:
    data: dict = json_parser.load_data(f'{directory}/versions/{version_name}/{version_name}.json')
    command: str = json_parser.get_launch_command(directory, data)

    print(command)
    subprocess.Popen(command, cwd=directory)
