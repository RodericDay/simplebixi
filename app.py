import time
import urllib.request

import json
import xml.dom.minidom
import xml.etree.ElementTree


def try_type(string):
    try:
        n = float(string)
        if n.is_integer():
            return int(n)
        return n
    except TypeError:
        return None
    except ValueError:
        if string in ["true", "false"]:
            return bool(string)
        return string

def update():
    url = "https://montreal.bixi.com/data/bikeStations.xml"
    with urllib.request.urlopen(url) as stream, open("stations.xml", 'w') as fp:
        string = xml.dom.minidom.parse(stream).toprettyxml()
        fp.write(string)
    return update_json()

def update_json():
    with open("stations.json", 'wb') as fp:
        stations = xml.etree.ElementTree.parse('stations.xml').getroot()
        d = [{tag.tag: try_type(tag.text) for tag in station} for station in stations]
        b = json.dumps(d, indent=4, sort_keys=True, ensure_ascii=False).encode('utf8')
        fp.write(b)
    return b

last_call = time.time() - 120
def app(environ, start_response):
    global last_call
    if (time.time() - last_call) > 60:
        print("Fetching from server...")
        last_call = time.time()
        data = update()
    else:
        print("Using local cache...")
        with open("stations.json", 'rb') as fp:
            data = fp.read()

    start_response("200 OK", [
      ("Content-Type", "application/json; charset=UTF-8"),
      ("Content-Length", str(len(data))),
      ("Access-Control-Allow-Origin", "*"),
    ])
    return iter([data])
