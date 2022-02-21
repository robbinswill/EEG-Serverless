#!/usr/bin/env python3
import os

import aws_cdk as cdk
from eeg_aws.eeg_aws_stack import EegAwsStack

app = cdk.App()
EegAwsStack(app, "EegAwsStack",
    env=cdk.Environment(account='817836876404', region='us-east-1'))

app.synth()
