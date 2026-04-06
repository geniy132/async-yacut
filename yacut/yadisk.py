import os
import asyncio
import aiohttp

from dotenv import load_dotenv
from http import HTTPStatus

from .constants import API_HOST, API_VERSION

load_dotenv()
DISK_TOKEN = os.environ.get('DISK_TOKEN')
AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}
UPLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def upload_single_file(session, file_name, file_content):
    from .views import get_or_create_url

    path = f'app:/{file_name}'
    params = {'path': path, 'overwrite': 'true'}

    async with session.get(
        UPLOAD_LINK_URL, headers=AUTH_HEADERS, params=params
    ) as response:
        if response.status != HTTPStatus.OK:
            return f'Ошибка получения ссылки для {file_name}:{response.status}'
        data = await response.json()
        href = data.get('href')

    async with session.put(href, data=file_content) as upload_response:
        if upload_response.status == HTTPStatus.CREATED:
            async with session.get(
                DOWNLOAD_URL,
                headers=AUTH_HEADERS,
                params={'path': path}
            ) as download_response:
                if download_response.status == HTTPStatus.OK:
                    direct_url = (await download_response.json()).get('href')
                    obj, _ = get_or_create_url(direct_url)
                    return f'{file_name}|{obj.to_dict()["short_link"]}'
            return f'Файл {file_name} загружен, но ссылка не получена.'
        return f'Ошибка загрузки {file_name}: {upload_response.status}'


async def upload_all_files(files_to_upload):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for name, content in files_to_upload:
            tasks.append(upload_single_file(session, name, content))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
