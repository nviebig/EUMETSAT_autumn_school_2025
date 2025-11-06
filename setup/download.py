import os
import s3fs

# === 1. Configuration ===
S3_ENDPOINT_URL = "https://s3.waw3-2.cloudferro.com"
BUCKET_NAME = "training"
# If you want to copy only a subfolder inside the bucket, set PREFIX (no leading slash).
# Example: PREFIX = "some/folder"  or "" to copy the whole bucket root
PREFIX = "static-files"  

# Local destination folder (relative to current working dir)
LOCAL_DIR = "./" 

# === 2. Connect to the open object store ===
fs = s3fs.S3FileSystem(anon=True, client_kwargs={"endpoint_url": S3_ENDPOINT_URL})

# Helper to join s3 paths correctly
def make_s3_path(bucket, key=""):
    if key:
        return f"{bucket}/{key}".rstrip("/")
    return bucket

# === 3. Prepare local folder ===
os.makedirs(LOCAL_DIR, exist_ok=True)
print(f"✅ Local download directory: {os.path.abspath(LOCAL_DIR)}")

# === 4. Walk the bucket (or prefix) and download files ===
root_path = make_s3_path(BUCKET_NAME, PREFIX)
print(f"✅ Connecting anonymously to: {S3_ENDPOINT_URL}")
print(f"Listing and downloading contents from: {root_path}\n")

download_count = 0
for dirpath, dirnames, filenames in fs.walk(root_path):
    # dirpath is like "bucket/prefix/..." -> convert to relative key by stripping "bucket/"
    if dirpath.startswith(f"{BUCKET_NAME}/"):
        rel_dir = dirpath[len(f"{BUCKET_NAME}/"):]
    elif dirpath == BUCKET_NAME:
        rel_dir = ""  # root of bucket
    else:
        # unexpected format - compute relative against PREFIX instead
        rel_dir = dirpath

    #local directory corresponding to this dirpath
    local_subdir = os.path.join(LOCAL_DIR, rel_dir)
    os.makedirs(local_subdir, exist_ok=True)

    for fname in filenames:
        s3_key = f"{rel_dir}/{fname}".lstrip("/")  # key relative to bucket
        s3_path = f"{BUCKET_NAME}/{s3_key}"
        local_path = os.path.join(local_subdir, fname)
       # local_path = os.path.join(local_subdir, fname)

        try:
            print(f"Downloading: s3://{s3_path} -> {local_path}")
            fs.get(s3_path, local_path)   # copies the file
            #fs.get(s3_path, "")   # copies the file
            download_count += 1
        except Exception as e:
            print(f"⚠️ Failed to download {s3_path}: {e}")

print(f"\n✅ Done. {download_count} file(s) downloaded to: {os.path.abspath(LOCAL_DIR)}")

from zipfile import ZipFile as zip
zipName = PREFIX + '/H-SAF_datasets.zip'

try:
    with zip(zipName, 'r') as z:
        for f in z.namelist():
            if f.endswith('/') or f.startswith('__'): # skip folders and __MACOSX
                continue
            target_dir = './HSAF/data/'
            z.extract(f, path=target_dir)
    os.remove(zipName)
except Exception as e:
    print(f"⚠️ Failed to extract file: {e}")
else:
    print(f"✅ HSAF datasets extracted succesfully")