import sys
import os

efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)

import mne
from mne_bids import BIDSPath, write_raw_bids


def handler(event, context):

    data_raw_file = os.path.join(efs_path, event['project_directory'], event['raw_data_directory'],
                                 event['subject_id'], event['raw_file'])
    raw = mne.io.read_raw_eeglab(data_raw_file)

    bids_dataset_path = os.path.join(efs_path, event['project_directory'], event['bids_data_directory'])
    bids_path = BIDSPath(subject=event['subject_id'], session=event['session'], run=event['run'],
                         datatype=event['datatype'], task=event['task'], root=bids_dataset_path)
    write_raw_bids(raw, bids_path=bids_path)

    return {
        'statusCode': 200,
        'body': 'bids.lambda_handler'
    }
