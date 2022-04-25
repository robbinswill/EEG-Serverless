"""
Function used to perform aggregate analysis
Currently a placeholder
"""

import sys
import os

# Mount the Elastic Filesystem packages (installed to /mnt/python/mne) to this function's site-packages
efs_path = '/mnt/python'
python_pkg_path = os.path.join(efs_path, "mne/lib/python3.8/site-packages")
sys.path.append(python_pkg_path)


def handler(event, context):
    pass
