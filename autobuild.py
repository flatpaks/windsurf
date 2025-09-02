#!/usr/bin/env python3

import subprocess
import http.client
import json

# deb download URL
# https://windsurf-stable.codeiumdata.com/linux-x64-deb/stable/ff497a1ec3dde399fde9c001a3e69a58f2739dac/Windsurf-linux-x64-1.12.3.deb

# to get latest url, get windsurf-stable.codeium.com/api/update/linux-x64-deb/stable/latest

# json object looks like this
#    {
#  "url": "https://windsurf-stable.codeiumdata.com/linux-x64-deb/stable/7c493d782a6cad0516e79f070d953687991df4ec/Windsurf-linux-x64-1.12.3.deb",
#  "name": "1.99.3",
#  "version": "7c493d782a6cad0516e79f070d953687991df4ec",
#  "productVersion": "1.99.3",
#  "hash": "af47291be1fc7b6d430e56a2f1cd6d4c1d415c25",
#  "timestamp": 1751502599,
#  "sha256hash": "6de81514272438677bdb080e491bbd5f68ff49ba0548e4627289b5e3f0a227b4",
#  "supportsFastUpdate": true,
#  "windsurfVersion": "1.12.3",
#  "displayName": "Linux x64 for Debian (.deb)"
#}

current = "1.12.3"


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
    url = new_ver.get("url")
    sha = new_ver.get("sha256hash")
    ver = new_ver.get("windsurfVersion")

    update_files = [
        "autobuild.py", ".github/workflows/build.yml",
        "com.windsurf.editor.yaml"
    ]
    # replace download URL
    sed_expr = f"sed -e 's,url: .*,url: {url},' -i com.windsurf.editor.yaml"
    subprocess.run(sed_expr, shell=True)
    # replace sha256sum
    sed_expr = f"sed -e 's,sha256: .*,sha256: {sha},' -i com.windsurf.editor.yaml"
    subprocess.run(sed_expr, shell=True)

    # replace version in files
    for name in update_files:
        sed_expr = f"sed -e 's,{current},{ver},' -i {name}"
        print(sed_expr)
        subprocess.run(sed_expr, shell=True)


def commit(new_ver):
    version = new_ver.get("windsurfVersion")
    statcode = subprocess.run("git status|grep 'nothing to commit'",
                              shell=True)
    if statcode.returncode != 0:
        print("Commiting")
        commit = f"git commit -am 'autobuild for {version}'"
        tagetc = f"git tag {version}; git push -f; git push -f origin {version}"

        commit_out = subprocess.run(commit, shell=True)
        tag_out = subprocess.run(tagetc, shell=True)
        print(f"Commit: {commit_out.returncode}, tag: {tag_out.returncode}")


def __main__():
    new_ver = get_deb()

    if new_ver is not None:
        update_files(new_ver)
        commit(new_ver)
    else:
        print("no new version")


if __name__ == "__main__":
    __main__()
