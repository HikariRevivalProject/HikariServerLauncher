import requests
SOURCE = r'http://hsl.hikari.bond/source.json'
def getSource():
    try:
        r = requests.get(SOURCE)
        return r.json()
    except:
        return None
