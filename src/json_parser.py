import libraries
import natives
import assets
import json


def load_data(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def get_launch_command(path: str, data: dict) -> str:
    java_path: str = f'java'
    class_path: str = libraries.get_class_path(path, data)
    natives_path: str = natives.get_natives_arg(path, data)
    start_class: str = f'{data["mainClass"]}'

    asset_index = assets.get_asset_index(path, data)
    version: str = f'--version {data["id"]}'
    game_args: str = f'{version} --gameDir {path} --assetsDir {path}/assets {asset_index} --accessToken bogus'

    full_command: str = f'{java_path} {natives_path} {class_path} {start_class} {game_args}'
    return full_command
