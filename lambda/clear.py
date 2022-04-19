import sys
import os
import shutil

efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)


def handler(event, context):
    # Deletes a potentially non-empty BIDS dataset, located at ROT/ROT_bids/
    path_to_bids = os.path.join(efs_path, "ROT", "ROT_bids")
    shutil.rmtree(path_to_bids, ignore_errors=True)
