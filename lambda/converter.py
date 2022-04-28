"""
Takes collected raw EEG data and uses MNE to generate the raw object then mne_bids to write the raw data
into a BIDS-compliant dataset
"""

import sys
import os

# Mount the Elastic Filesystem packages (installed to /mnt/python/mne) to this function's site-packages
efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)

import mne
from mne_bids import BIDSPath, write_raw_bids, print_dir_tree


# Lambda handler, parameters passed into event Json object
def handler(event, context):

    # Convert each ROT .set/.fdt pair into a BIDS-compliant database
    raw_fname = os.path.join(efs_path, event['project_directory'], event['subject_id'], event['raw_file'])
    eog_inds = [64, 65]
    raw = mne.io.read_raw_eeglab(raw_fname,
                                 eog=eog_inds)
    raw.set_montage('standard_1005')

    # Create the BIDS dataset path, then use the BIDSPath object to write the raw data into the BIDS dataset
    bids_dataset_path = os.path.join(efs_path, event['project_directory'], event['bids_data_directory'])
    bids_path = BIDSPath(subject=event['subject_id'], datatype=event['datatype'], session=event['session'],
                         task=event['task'], root=bids_dataset_path)
    write_raw_bids(raw, bids_path=bids_path, overwrite=True)

    # Recursively print the directory tree of the BIDS dataset (for logging)
    print_dir_tree(bids_dataset_path)
