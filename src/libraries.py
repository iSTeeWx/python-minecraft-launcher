import util
import time


def get_class_path(path: str, data: dict) -> str:
    """returns the cp jvm argument that has all the libraries"""
    return f'-cp {download_libraries(path, data)}{get_version_jar(path, data)}'


def get_version_jar(path: str, data: dict) -> str:
    """returns the absolute path of the version.jar file"""
    print('<=== DOWNLOADING CLIENT JAR ===>')
    start_time: float = time.time()

    client_id: str = download_client_jar(path, data)

    print(f'<=== TOOK {time.time() - start_time:.2f}s ===>')

    return f'{path}/versions/{client_id}/{client_id}.jar'


def download_client_jar(path: str, data: dict) -> str:
    """:returns: the name of the jar without its extension"""
    jar_name: str = data['id']
    version_folder: str = f'{path}/versions/{jar_name}'

    if util.file_exists(f'{version_folder}/{jar_name}.jar'):
        if 'downloads' in data and 'client' in data['downloads']:
            artifact_sha1: str = data['downloads']['client']['sha1']
            if util.verify_file_sha1(f'{version_folder}/{jar_name}.jar', artifact_sha1) == 'good':
                print(f'✅ Skipping downloading {jar_name}.jar as it already exists')
                return jar_name
            else:
                print('⚠️ Overwriting existing client jar')
                print(f'To prevent this behaviour, remove the "downloads" element in {jar_name}.json')
        else:
            print('⚠️ No data specified to download the client jar')
            print(f'Using existing jar: {version_folder}/{jar_name}.jar')
            return jar_name
    else:
        if 'downloads' in data and 'client' in data['downloads']:
            print('➡️ Downloading client jar')
        else:
            print('❌ No data specified to download the client jar, and no client jar provided')
            return jar_name  # TODO: handle problem

    artifact: dict = data['downloads']['client']
    artifact_sha1: str = artifact['sha1']
    artifact_url: str = artifact['url']

    response = util.download_resource(artifact_url, f'{version_folder}', f'{jar_name}.jar')
    if response == 200:
        if util.verify_file_sha1(f'{version_folder}/{jar_name}.jar', artifact_sha1) == 'good':
            print(f'✅ Downloaded client jar')
            print(f'\t➡️ Version file sha1 is a match ({artifact_sha1})')
        else:
            print(f'❌ Failed to verify {jar_name}.jar, hoping for the best ¯\\_(ツ)_/¯')
            print(f'\t❌ Failed to verify sha1, expected {artifact_sha1}, got {artifact_sha1}')
    else:
        print(f'❌ Failed to download {jar_name}.jar, got {response}')

    return jar_name


def download_libraries(path: str, data: dict) -> str:
    """returns a semicolon separated list of all the libraries absolute path"""
    return_val: str = ''

    print('<=== DOWNLOADING LIBRARIES ===>')
    start_time: float = time.time()

    for lib in data['libraries']:
        return_val += f'{download_library(path, lib)};'

    print(f'<=== TOOK {time.time() - start_time:.2f}s ===>')

    return return_val


def download_library(path: str, lib: dict) -> str:
    """returns the absolute path of the downloaded library if it is not a native"""
    # Download path follows the .m2 (maven) structure
    # <root_location>/<group_id>/<artifact_id>/<artifact_version>/<artifact_id>-<artifact_version>.jar
    # ie: .../com/mojang/netty/1.8.8/netty-1.8.8.jar

    library_name_parts: list = lib['name'].split(':')  # ie: { "com.mojang", "netty", "1.8.8" }
    group_id: str = library_name_parts[0].replace('.', '/')  # ie: com/mojang
    artifact_id: str = library_name_parts[1]  # ie: netty
    artifact_version: str = library_name_parts[2]  # ie: 1.8.8
    library_parent_dir: str = f'{path}/libraries/{group_id}/{artifact_id}/{artifact_version}'

    if 'classifiers' in lib['downloads']:
        artifact_native_id: str = lib['natives'][util.get_os_name()]
        artifact_native_id = artifact_native_id.replace('${arch}', util.get_os_arch())
        artifact: dict = lib['downloads']['classifiers'][artifact_native_id]
        library_file_name: str = f'{artifact_id}-{artifact_version}-{artifact_native_id}.jar'
        library_full_path: str = f'{library_parent_dir}/{library_file_name}'
        return_value: str = ''
    else:
        artifact: dict = lib['downloads']['artifact']
        library_file_name: str = f'{artifact_id}-{artifact_version}.jar'
        library_full_path: str = f'{library_parent_dir}/{library_file_name}'
        return_value: str = library_full_path

    artifact_sha1: str = artifact['sha1']
    artifact_size: str = artifact['size']
    artifact_url: str = artifact['url']

    # Skips download and early returns if the artifact already exists, and its sum and size are good
    if util.verify_file_sha1(library_full_path, artifact_sha1) == 'good' and util.verify_file_size(library_full_path, int(artifact_size)) == 1:
        print(f'✅ Skipping {library_file_name} as it already exists')
        return return_value

    # Downloads the artifact, and early return if the artifact failed to download 5 times
    downloaded_file: int = try_download_artifact(artifact_url, library_file_name, library_parent_dir)
    if downloaded_file != 200:
        return return_value

    downloaded_file_sha1: str = util.verify_file_sha1(library_full_path, artifact_sha1)
    downloaded_file_size: int = util.verify_file_size(library_full_path, int(artifact_size))

    # Used to dictate the text to log
    success: bool = downloaded_file_sha1 == 'good' and downloaded_file_size == 1
    if success:
        log_text: str = f'✅ Downloaded {library_file_name}'
    else:
        log_text: str = f'❌ Failed to verify {library_file_name}, hoping for the best ¯\\_(ツ)_/¯'

    if downloaded_file == 200:
        print(log_text)
        if downloaded_file_sha1 == 'good':
            print(f'\t➡️ File sha1 is a match ({artifact_sha1})')
        else:
            print(f'\t❌ Failed to verify sha1, expected {artifact_sha1}, got {downloaded_file_sha1}')
        if downloaded_file_size == 1:
            print(f'\t➡️ File size is a match ({artifact_size} bytes)')
        else:
            print(f'\t❌ Failed to verify size, expected {artifact_size} bytes, got {-downloaded_file_size} bytes')

    return return_value


def try_download_artifact(artifact_url: str, library_file_name: str, library_parent_dir: str) -> int:
    # Try 5 times to download the artifact
    downloaded_file: int = -1
    for i in range(5):
        downloaded_file = util.download_resource(artifact_url, library_parent_dir, library_file_name)
        if downloaded_file == 200:
            break
        else:
            print(f'❌ Failed to download {library_file_name}, got {downloaded_file}, trying again {4 - i} more times')
    return downloaded_file
