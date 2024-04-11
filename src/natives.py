import util
import time


def get_natives_arg(path: str, data: dict) -> str:
    return f'-Djava.library.path="{get_natives(path, data)}"'


def get_natives(path: str, data: dict) -> str:
    version: str = data['id']
    extract_natives(path, data)

    return f'{path}/versions/{version}/{version}-natives'


def extract_natives(path: str, data: dict) -> None:
    version: str = data['id']
    natives_path: str = f'{path}/versions/{version}/{version}-natives'
    print('<=== EXTRACTING NATIVES ===>')
    start_time: float = time.time()

    for lib in data['libraries']:
        if 'downloads' not in lib or 'classifiers' not in lib['downloads']:
            continue

        classifier_id: str = lib['natives'][util.get_os_name()]
        classifier_id = classifier_id.replace('${arch}', util.get_os_arch())

        # See libraries to get the logic
        native_name_parts: list[str] = lib['name'].split(':')
        native_group_id: str = native_name_parts[0].replace('.', '/')
        native_artifact_name: str = native_name_parts[1]
        native_artifact_version: str = native_name_parts[2]
        native_file_name: str = f'{native_artifact_name}-{native_artifact_version}-{classifier_id}.jar'
        native_path: str = f'{native_group_id}/{native_artifact_name}/{native_artifact_version}/{native_file_name}'

        native_zip_path: str = f'{path}/libraries/{native_path}'

        if util.extract_resource(native_zip_path, natives_path):
            print(f'✅ Extracted {lib["name"].split(":")[1]}-{lib["name"].split(":")[2]}')
        else:
            print(f'❌ Failed to extract {lib["name"].split(":")[1]}-{lib["name"].split(":")[2]}')

    print(f'<=== TOOK {time.time() - start_time:.2f}s ===>')
