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
        print(f"Found latest version: {data['tag_name']}")
        
    except Exception as e:
        # --- 2. Fallback to specific tag if API fails ---
        print(f"API failed ({e}). Using fallback tag: {fallback_tag}")
        download_url = f"https://github.com/{user}/{repo}/archive/refs/tags/{fallback_tag}.zip"

    # --- 3. Download ---
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(output, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Downloaded to {output}")

payload = json.loads(sys.argv[1])
data1 = payload["data1"]
print(data1)
print(type(data1))
targets = [tuple(x) for x in data1]
print(targets)
print(type(targets))
pass_payload= payload["data"]

for user, repo, tag in targets:
    # Check if file exists before calling
    if not os.path.exists(filename):
        print(f"File '{filename}' not found. Starting download...")
        download_latest(user, repo, tag, output=filename)
        print("-" * 30)
    else:
        print(f"Skipping: '{filename}' already exists.")
        break

if os.path.exists(filename):
    with zipfile.ZipFile(filename, 'r') as z:
        z.extractall("extracted")
        test_file = [f for f in z.namelist() if f.endswith("text.py")]

        if test_file:
            script_path = os.path.join("extracted", test_file[0])
            script_dir = os.path.dirname(script_path)
            print(f"Running {test_file[0]}...")
            subprocess.run([sys.executable, os.path.basename(script_path),json.dumps(pass_payload)], cwd=script_dir)
        else:
            print("text.py not found inside the zip.")
else:
    print(f"'{filename}' not found. Nothing to extract.")
