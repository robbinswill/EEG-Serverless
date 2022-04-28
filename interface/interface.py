"""
Interface to test deployed Lambda functions.
Subject IDs and experiment attributes are hardcoded for now.
Function name should be saved to a config file.
"""

import json
import boto3


def invoke_bids_converter():

    # List of subject IDs
    # subject_ids = ['ROT1', 'ROT2', 'ROT3', 'ROT4', 'ROT5', 'ROT6', 'ROT9', 'ROT10', 'ROT11', 'ROT12']
    subject_ids = ['ROT1', 'ROT2']

    # List of sessions
    sessions = ['pre', 'post']

    # Each .set file follows the pattern ROT<X><pre/post>.set, where X is the subject ID number and the session
    # can be either pre or post
    # Now, invoke the BIDS converter Lambda asynchronously to batch convert all subjects

    for id in subject_ids:
        for ses in sessions:
            # Construct the .set filename
            filename = id + ses + ".set"

            # Generate the payload parameters
            params = {
                "project_directory": "ROT",
                "subject_id": id,
                "raw_file": filename,
                "bids_data_directory": "ROT_bids",
                "session": ses,
                "run": 1,
                "datatype": "eeg",
                "task": "default"
            }
            lambda_payload = json.dumps(params)

            # Start the boto3 client and then invoke the Lambda
            client = boto3.client('lambda')

            # Run Lambdas sequentially to avoid race condition
            response = client.invoke(
                FunctionName='EegServerlessStack-eegserverlesslambdaBidsConverte-urQC2Ia7S0SC',
                InvocationType='RequestResponse',
                Payload=lambda_payload
            )
            print(response)


if __name__ == '__main__':
    invoke_bids_converter()
