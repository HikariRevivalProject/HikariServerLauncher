from typing import Dict, Optional
import httpx
from hsl.core.exceptions import RequestFailedException
def build_header(cookie: Optional[str], authorization: Optional[str]) -> Dict[str, str]:
    _header = {"Content-Type": "application/json"}
    if cookie:
        _header["Cookie"] = f'17a={cookie}'
    if authorization:
        _header["Authorization"] = authorization
    return _header

async def openfrp_api_request(url: str, *, data: Optional[dict] = None, authorization: Optional[str] = None, cookie: Optional[str] = None) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, headers=build_header(cookie, authorization))
            print(response.text)
            print(response.json())
        except httpx.RequestError:
            raise RequestFailedException(f"Request failed to {url}")
        if response.status_code != 200:
            raise RequestFailedException(f"Request failed to {url}, response status code is {response.status_code}")
        if response.json()['flag'] != True:
            raise RequestFailedException(f"Request failed to {url}, response flag is {response.json()['flag']}")
        return response