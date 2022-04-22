import sys
import os
from pip import _internal

efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)

import mne
from mne_bids import BIDSPath, read_raw_bids, print_dir_tree, make_report


def handler(event, context):

    # Get the root to the BIDS dataset, print directory tree and make report
    bids_root = os.path.join(efs_path, "ROT", "ROT_bids")
    print_dir_tree(bids_root)
    print(make_report(bids_root))

    # Declare hyperparameters

    # Try reading-in a subject using MNE_BIDS
    # bids_layout = BIDSLayout(bids_root)
    # bids_layout.get_subjects()
    # bids_layout.get_sessions()

    _internal.main(['list'])
    print(sys.path)
