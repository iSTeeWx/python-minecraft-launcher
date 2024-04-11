import platform
import requests
import zipfile
import hashlib
import json
import os


def pprint(data: dict) -> None:
    print(json.dumps(data, indent=2))


def get_os_name() -> str:
    platform_name: str = platform.system()
    if platform_name == 'Windows':
        return 'windows'
    if platform_name == 'Linux':
        return 'linux'
    if platform_name == 'Darwin':
        return 'osx'


def get_os_arch() -> str:
    if '64' in os.environ.get('PROCESSOR_ARCHITECTURE'):
        return '64'
    return '64'


def extract_resource(file_in: str, directory: str) -> bool:
    """returns True if success, False if fail"""

    ensure_folder_exists(directory)

    if not zipfile.is_zipfile(file_in):
        return False

    with zipfile.ZipFile(file_in, 'r') as zf:
        zf.extractall(directory)

    return True


def download_resource(url: str, target_dir: str, file_name: str) -> int:
    """:returns: 200 if success, status_code if fail"""
    target_location: str = f'{target_dir}/{file_name}'

    ensure_folder_exists(target_dir)

    response: requests.Response = requests.get(url)
    if response.status_code != 200:
        return response.status_code

    with open(target_location, 'wb') as f:
        f.write(response.content)
        return response.status_code


def ensure_folder_exists(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def file_exists(file_path: str) -> bool:
    """returns True if the file exists, else False"""
    return os.path.exists(file_path)


def verify_file_sha1(file_path: str, expected_sha1: str) -> str:
    """returns 'good' if good, '' if not exist, 'file_sha1' if bad"""
    if not file_exists(file_path):
        return ''

    sha1_instance = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while chuck := f.read(8192):
            sha1_instance.update(chuck)

    file_sha1: str = sha1_instance.hexdigest()
    if file_sha1 == expected_sha1:
        return 'good'
    return file_sha1


def verify_file_size(file_path: str, expected_size: int) -> int:
    """returns 1 if good, 0 if not exist, -file_size if bad"""
    if not file_exists(file_path):
        return 0

    file_size = os.path.getsize(file_path)
    if file_size == expected_size:
        return 1
    return -file_size
