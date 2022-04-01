import json
import subprocess


def invoke_lambda_handler():

    data = {'project_directory': 'N400_CORE',
            'raw_data_directory': 'raw',
            'bids_data_directory': 'BIDS_dataset',
            'subject_id': '5',
            'raw_file': '5_N400.set',
            'session': '1',
            'run': 1,
            'datatype': 'eeg',
            'task': 'wordpair'}
    lambda_payload = json.dumps(data)

    subprocess.run(["aws", "lambda", "invoke",
                    "--function-name", "EegAwsStack-eegtestlambdaBidsConverterA46A12B6-Pb3y45iZUfd2",
                    "--region", "us-east-1",
                    "--payload", lambda_payload,
                    "response.json"])


if __name__ == '__main__':
    invoke_lambda_handler()
