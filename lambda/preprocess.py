import sys
import os

efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)

from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report


def handler(event, context):

    # Get the root to the BIDS dataset, print directory tree and make report
    bids_root = os.path.join(efs_path, "ROT", "ROT_bids")
    print_dir_tree(bids_root)
    print(make_report(bids_root))

    
