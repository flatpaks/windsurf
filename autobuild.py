#!/usr/bin/env python3

import subprocess
import http.client
import json

# deb download URL
# https://windsurf-stable.codeiumdata.com/linux-x64-deb/stable/ff497a1ec3dde399fde9c001a3e69a58f2739dac/Windsurf-linux-x64-1.10.5.deb

# to get latest url, get windsurf-stable.codeium.com/api/update/linux-x64-deb/stable/latest

# json object looks like this
#    {
#  "url": "https://windsurf-stable.codeiumdata.com/linux-x64-deb/stable/7c493d782a6cad0516e79f070d953687991df4ec/Windsurf-linux-x64-1.10.7.deb",
#  "name": "1.99.3",
#  "version": "7c493d782a6cad0516e79f070d953687991df4ec",
#  "productVersion": "1.99.3",
#  "hash": "af47291be1fc7b6d430e56a2f1cd6d4c1d415c25",
#  "timestamp": 1751502599,
#  "sha256hash": "6de81514272438677bdb080e491bbd5f68ff49ba0548e4627289b5e3f0a227b4",
#  "supportsFastUpdate": true,
#  "windsurfVersion": "1.10.7",
#  "displayName": "Linux x64 for Debian (.deb)"
#}

current = "1.10.5"


def get_deb():
    # poll the update API to get the latest deb package
    conn = http.client.HTTPSConnection('windsurf-stable.codeium.com')
    headers = {"Accpet": "application/json"}
    conn.request('GET',
                 '/api/update/linux-x64-deb/stable/latest',
                 headers=headers)
    response = conn.getresponse()
    rt = response.read().decode("utf-8").replace("'", '"')
    conn.close()
    jdata = json.loads(rt)

    dl_url = jdata.get("url")
    dl_hash = jdata.get("sha256hash")
    dl_ver = jdata.get("windsurfVersion")

    if dl_ver != current:
        print(f"new version {dl_ver}")
        return jdata
    else:
        return None


def update_files(new_ver):
    # update strings in files
    update_files = [
        "autobuild.py", ".github/workflows/build.yml",
        "com.windsurf.editor.yaml"
    ]
    for name in update_files:
        sed_expr = f"sed -e 's,{current},{new_ver},' -i {name}"
        print(sed_expr)
        subprocess.run(sed_expr, shell=True)


def __main__():
    new_ver = get_deb()

    if new_ver is not None:
        update_files(new_ver.get("windsurfVersion"))
    else:
        print("no new version")


if __name__ == "__main__":
    __main__()
