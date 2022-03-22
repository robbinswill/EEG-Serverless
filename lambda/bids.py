import sys
import os

efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)

import mne
import json
from mne_bids import BIDSPath, write_raw_bids


def lambda_handler(event, context):


    


    # sample_data_raw_file = os.path.join(efs_path, 'sub_01', 'sample_audvis_filt-0-40_raw.fif')
    # raw = mne.io.read_raw_fif(sample_data_raw_file)
    #
    # bids_dataset_path = os.path.join(efs_path, 'bids_dataset')
    # bids_path = BIDSPath(subject='01', session='01', run=1,
    #                      datatype='meg', task='testtask', root=bids_dataset_path)
    # write_raw_bids(raw, bids_path=bids_path)

    # print(event['key1'])

    return {
        'statusCode': 200,
        'body': 'bids.lambda_handler'
    }
