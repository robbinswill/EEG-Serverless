from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_s3_notifications as s3_notify,
    aws_lambda_event_sources as events
)


class EegAwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        group = iam.Group(self, 'eeg-test-group')
        user = iam.User(self, 'eeg-test-user')
        user.add_to_group(group)

        bucket = s3.Bucket(self, 'eeg-test-raw-bucket')
        bucket.grant_read_write(user)

        lambda_func = _lambda.Function(self, 'eeg-test-lambdaListener',
                                       runtime=_lambda.Runtime.PYTHON_3_8,
                                       handler='LambdaListener.handler',
                                       code=_lambda.Code.from_asset('lambda'),
                                       environment={'BUCKET_NAME': bucket.bucket_name})

        notification = s3_notify.LambdaDestination(lambda_func)
        notification.bind(self, bucket)

        # trigger lambda when brain-imaging files are added
        s3PutEventSource = events.S3EventSource(bucket,
                                                events=[s3.EventType.OBJECT_CREATED])
        lambda_func.add_event_source(s3PutEventSource)

