import requests
from rich.progress import Progress

async def downloadfile(url: str, path: str, timeout: int = 10, params = None) -> bool:
    print(f'Start downloading {url} to {path}...')
    
    # 发起 GET 请求
    response = requests.get(url, stream=True, params=params, timeout=timeout)
    response.raise_for_status()  # 检查请求是否成功

    total_size = int(response.headers.get('Content-Length', 0))  # 获取总大小

    with open(path, 'wb') as file:
        with Progress() as progress:
            task = progress.add_task("Downloading...", total=total_size)
            try:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    progress.update(task, advance=len(data))
            except requests.exceptions.RequestException as e:
                print(f'Download failed: {e}')
                return False
            except Exception as e:
                print(f'Download failed: {e}')
                return False
    return True