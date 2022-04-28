"""
This code attempts to implement the preprocessing logic written by Dr. Aaron J. Newman, NeuroCognitive Imaging Lab, Dalhousie University
Original script name is "MNE_ROT_1 copy.ipynb".
The code taken from that script begins underneath the "Declare hyperparameters" comment.
"""

import sys
import os

# Mount the Elastic Filesystem packages (installed to /mnt/python/mne) to this function's site-packages
efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)

import mne
from bids import BIDSLayout
import numpy as np


def handler(event, context):

    # Get the root to the BIDS dataset, print directory tree and make report
    bids_root = os.path.join(efs_path, event['project_directory'], event['bids_data_directory'])

    # Use the BIDSLayout object of the PyBids package to retrieve subjects from the BIDS dataset
    bids_layout = BIDSLayout(bids_root)

    # Declare hyperparameters
    eog_inds = [64, 65]
    tmin = -0.2
    tmax = 1.0
    baseline = (None, 0)
    reject = dict(eeg=200e-6, eog=200e-6)
    l_freq = 0.1
    h_freq = 40.0
    l_trans_bandwidth = 'auto'
    h_trans_bandwidth = 'auto'
    filter_length = 'auto'
    ica_random_state = 42
    n_max_ecg = 3
    n_max_eog = 3
    n_components = 0.99

    # Read-in a subject using the BIDSLayout object by first getting the full filename, then generate the MNE Raw object
    sub_raw_fname = bids_layout.get(event['subject_id'], extension='.set', return_type='filename', session='pre')
    raw = mne.io.read_raw_eeglab(sub_raw_fname[0], eog=eog_inds, preload=True)
    print(raw.get_montage())
    print(raw.info['ch_names'])
    print(raw.info)
    print(raw.annotations)

    # Apply a bandpass filter
    raw.filter(l_freq, h_freq, l_trans_bandwidth=l_trans_bandwidth, h_trans_bandwidth=h_trans_bandwidth,
               filter_length=filter_length, method='fft', n_jobs=6)

    # Event processing
    print_event_labels = {"prt/Rus/unamb": 111, "prt/Eng/unamb": 122,
                          "prt/Rus/same/first": 114, "prt/Rus/same/last": 141,
                          "prt/both/same": 244, "prt/both/confl": 233,
                          "prt/both/confl/first": 234, "prt/both/confl/last": 243}

    audio_event_pairs = {'aud/match/Rus/only': [111, 21], 'aud/mismatch/Rus/only': [111, 22],
                         'aud/match/Eng/only': [122, 11], 'aud/mismatch/Eng/only': [122, 12],
                         'aud/match/Eng/same': [244, 11], 'aud/mismatch/Eng/same': [244, 12],
                         'aud/match/Rus/same': [244, 21], 'aud/mismatch/Rus/same': [244, 22],
                         'aud/match/Eng/confl/full': [233, 11], 'aud/mismatch/Eng/confl/full': [233, 12],
                         'aud/match/Eng/confl/part': [234, 11], 'aud/mismatch/Eng/confl/part': [234, 12],
                         'aud/match/Rus/confl/full': [233, 21], 'aud/mismatch/Rus/confl/full': [233, 22],
                         'aud/match/Rus/confl/part': [234, 21], 'aud/mismatch/Rus/confl/part': [234, 22]}

    audio_event_labels = {'aud/match/Rus/only': 1000, 'aud/mismatch/Rus/only': 1001,
                          'aud/match/Eng/only': 1002, 'aud/mismatch/Eng/only': 1003,
                          'aud/match/Eng/same': 1004, 'aud/mismatch/Eng/same': 1005,
                          'aud/match/Rus/same': 1006, 'aud/mismatch/Rus/same': 1007,
                          'aud/match/Eng/confl/full': 1008, 'aud/mismatch/Eng/confl/full': 1009,
                          'aud/match/Eng/confl/part': 1010, 'aud/mismatch/Eng/confl/part': 1011,
                          'aud/match/Rus/confl/full': 1012, 'aud/mismatch/Rus/confl/full': 1013,
                          'aud/match/Rus/confl/part': 1014, 'aud/mismatch/Rus/confl/part': 1015}

    event_id = {**print_event_labels, **audio_event_labels}
    events = mne.events_from_annotations(raw=raw)[0]
    print(events)

    code_tmin = -1
    code_tmax = 0

    events_adj = np.empty([0, 3], dtype=int)

    for key, value in audio_event_pairs.items():
        events_tmp, lag_tmp = mne.event.define_target_events(events, value[1], value[0],
                                                             raw.info['sfreq'], code_tmin, code_tmax,
                                                             new_id=audio_event_labels[key],
                                                             fill_na=None)
        if len(events_tmp) > 0:
            events_adj = np.append(events_adj, events_tmp, axis=0)

    print_codes = []
    for value in print_event_labels.values():
        if int(value) > 100:
            print_codes.append(int(value))
    print_events = events[:][np.where(np.isin(events[:, 2], print_codes))]

    events_adj = np.concatenate((events_adj, print_events), axis=0)
    order = np.argsort(events_adj[:, 0])
    events_adj = events_adj[order]

    # Epoching
    picks_eeg = mne.pick_types(raw.info, eeg=True, eog=True, stim=False, exclude=[])

    epochs = mne.Epochs(raw, events_adj, event_id, tmin, tmax, proj=False, picks=picks_eeg, baseline=baseline, preload=True)
    print(epochs)
