import requests
SOURCE = r'http://hsl.hikari.bond/hsl.json'
def checkUpdate(version):
    r = requests.get(SOURCE)
    if r.status_code == 200:
        latest = r.json()['version']
        if version < latest:
            return True, latest
        else:
            return False, latest
