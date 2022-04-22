import sys
import os

efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)

import mne
from mne_bids import BIDSPath, write_raw_bids, print_dir_tree


def handler(event, context):

    print(os.listdir(efs_path))
    print(os.listdir(os.path.join(efs_path, event['project_directory'])))

    # Convert each ROT .set/.fdt pair into a BIDS-compliant database
    raw_fname = os.path.join(efs_path, event['project_directory'], event['subject_id'], event['raw_file'])
    eog_inds = [64, 65]
    raw = mne.io.read_raw_eeglab(raw_fname,
                                 eog=eog_inds)
    raw.set_montage('standard_1005')

    bids_dataset_path = os.path.join(efs_path, event['project_directory'], event['bids_data_directory'])
    bids_path = BIDSPath(subject=event['subject_id'], datatype=event['datatype'], session=event['session'],
                         task=event['task'], root=bids_dataset_path)
    write_raw_bids(raw, bids_path=bids_path, overwrite=True)

    print(os.listdir(os.path.join(efs_path, event['project_directory'], event['bids_data_directory'])))
