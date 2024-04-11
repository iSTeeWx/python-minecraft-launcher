import json
import util
import time


def get_asset_index(path: str, data: dict) -> str:
    print('<=== DOWNLOADING ASSETS ===>')
    start_time: float = time.time()
    return_val = download_asset_index(path, data)
    download_assets(path, data)
    print(f'<=== TOOK {time.time() - start_time:.2f}s ===>')

    return f'--assetIndex {return_val}'


def download_assets(path: str, data: dict) -> None:
    index_id: str = data['assets']
    asset_index_path = f'{path}/assets/indexes/{index_id}.json'

    if not util.file_exists(asset_index_path):
        return

    with open(asset_index_path, 'r') as f:
        assets_data: dict = json.load(f)

    resources_url: str = 'https://resources.download.minecraft.net'

    object_amount: int = len(assets_data['objects'])
    amount_failed: int = 0

    for i, asset in enumerate(assets_data['objects']):

        asset_data: dict = assets_data['objects'][asset]
        asset_hash: str = asset_data['hash']
        asset_cut_hash: str = asset_hash[:2]
        asset_url = f'{resources_url}/{asset_cut_hash}/{asset_hash}'
        asset_folder = f'{path}/assets/objects/{asset_cut_hash}'

        if util.verify_file_sha1(f'{asset_folder}/{asset_hash}', asset_hash) == 'good':
            continue

        for _ in range(5):
            if util.download_resource(asset_url, asset_folder, asset_hash) == 200:
                print(f'\r➡️ Downloading asset {asset_hash}: {(i + 1) / object_amount * 100:.0f}%', end='')
                if util.verify_file_sha1(f'{asset_folder}/{asset_hash}', asset_hash) == 'good':
                    break
        else:
            amount_failed += 1

    if amount_failed == 0:
        print(f'\r✅ Downloaded assets')
    else:
        print(f'\r⚠️ Downloaded assets, failed {amount_failed}')


def download_asset_index(path: str, data: dict) -> str:
    """:returns: the id of the assetIndex for example '1.8'"""

    if 'assetIndex' not in data:
        if util.file_exists(f'{path}/assets/indexes/{data["assets"]}.json'):
            print(f'⚠️ Could not download assets index for this version, trying with existing asset index')
        else:
            print(f'⚠️ Could not download assets index for this version, try to launch the vanilla version this client is based on')

        return data['assets']

    index: dict = data['assetIndex']
    index_id: str = index['id']
    index_sha1: str = index['sha1']
    index_size: str = index['size']
    index_url: str = index['url']

    target_dir: str = f'{path}/assets/indexes'
    target_file: str = f'{index_id}.json'
    target_file_path = f'{target_dir}/{target_file}'

    if util.file_exists(target_file_path):
        if util.verify_file_sha1(target_file_path, index_sha1) == 'good' and util.verify_file_size(target_file_path, int(index_size)) == 1:
            print(f'✅ Skipping downloading assets index {index_id}.json as it already exists')
            return index_id

    response: int = util.download_resource(index_url, target_dir, target_file)
    downloaded_file_sha1: str = util.verify_file_sha1(target_file_path, index_sha1)
    downloaded_file_size: int = util.verify_file_size(target_file_path, int(index_size))

    succeeded: bool = downloaded_file_sha1 == 'good' and downloaded_file_size == 1

    if succeeded:
        log_text: str = f'✅ Downloaded assets index {index_id}.json'
    else:
        log_text: str = f'❌ Failed to verify assets index {index_id}.json, hoping for the best ¯\\_(ツ)_/¯'

    if response == 200:
        print(log_text)
        if downloaded_file_sha1 == 'good':
            print(f'\t➡️ File sha1 is a match ({index_sha1})')
        else:
            print(f'\t❌ Failed to verify sha1, expected {index_sha1}, got {downloaded_file_sha1}')
        if downloaded_file_size == 1:
            print(f'\t➡️ File size is a match ({index_size} bytes)')
        else:
            print(f'\t❌ Failed to verify size, expected {index_size} bytes, got {-downloaded_file_size} bytes')
    else:
        print(f'❌ Failed to download assets index for {index_id}, got {response}')

    return index_id
