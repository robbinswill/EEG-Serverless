from constructs import Construct
from aws_cdk import (
    Stack,
    Size,
    Duration,
    RemovalPolicy,
    CfnOutput,
    custom_resources as cr,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_codebuild as codebuild
)


class EegAwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, 'eeg-test-vpc', max_azs=2, nat_gateways=1)

        ec2SecurityGroup = ec2.SecurityGroup(self, 'eeg-test-ec2SG', vpc=vpc, security_group_name='eeg-test-ec2SG')
        lambdaSecurityGroup = ec2.SecurityGroup(self, 'eeg-test-lambdaSG', vpc=vpc, security_group_name='eeg-test-lambdaSG')
        efsSecurityGroup = ec2.SecurityGroup(self, 'eeg-test-efsSG', vpc=vpc, security_group_name='eeg-test-efsSG')

        ec2SecurityGroup.connections.allow_to(efsSecurityGroup, ec2.Port.tcp(2049))
        lambdaSecurityGroup.connections.allow_to(efsSecurityGroup, ec2.Port.tcp(2049))

        fs = efs.FileSystem(self, 'eeg-test-efs',
                            vpc=vpc,
                            security_group=efsSecurityGroup,
                            throughput_mode=efs.ThroughputMode.PROVISIONED,
                            provisioned_throughput_per_second=Size.mebibytes(10),
                            removal_policy=RemovalPolicy.DESTROY)

        efsAccessPoint = efs.AccessPoint(self, 'eeg-test-accesspoint',
                                         file_system=fs,
                                         path='/lambda',
                                         posix_user=efs.PosixUser(gid='1000', uid='1000'),
                                         create_acl=efs.Acl(owner_gid='1000', owner_uid='1000', permissions='777'))

        executeBidsConverter = _lambda.Function(self, 'eeg-test-lambdaBidsConverter',
                                                runtime=_lambda.Runtime.PYTHON_3_8,
                                                handler='bids.lambda_handler',
                                                code=_lambda.Code.from_asset("./lambda"),
                                                vpc=vpc,
                                                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
                                                security_groups=[lambdaSecurityGroup],
                                                timeout=Duration.minutes(2),
                                                memory_size=4096,
                                                reserved_concurrent_executions=10,
                                                filesystem=_lambda.FileSystem.from_efs_access_point(efsAccessPoint, '/mnt/python'))
        executeBidsConverter.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonElasticFileSystemClientFullAccess"))



        codeBuildProject = codebuild.Project(self, 'eeg-test-codebuildProject',
                                             project_name="eeg-test-codebuildProject",
                                             description="Installs Python libraries to EFS.",
                                             vpc=vpc,
                                             build_spec=codebuild.BuildSpec.from_object({
                                                 'version': '0.1',
                                                 'phases': {
                                                     'build': {
                                                         'commands': [
                                                             'echo "Installing virtual environment..."',
                                                             'mkdir -p $CODEBUILD_EFS1/lambda',
                                                             'echo "Clearing previous environment, if it exists..."',
                                                             'rm -rf $CODEBUILD_EFS1/lambda/mne',
                                                             'python3 -m venv $CODEBUILD_EFS1/lambda/mne',
                                                             'source $CODEBUILD_EFS1/lambda/mne/bin/activate && pip3 install mne && pip3 install mne-bids',
                                                             'echo "Changing folder permissions..."',
                                                             'chown -R 1000:1000 $CODEBUILD_EFS1/lambda/'
                                                         ]
                                                     }
                                                 }
                                             }),
                                             environment=codebuild.BuildEnvironment(build_image=codebuild.LinuxBuildImage.from_docker_registry('lambci/lambda:build-python3.8'),
                                                                                    compute_type=codebuild.ComputeType.LARGE,
                                                                                    privileged=True),
                                             security_groups=[ec2SecurityGroup],
                                             subnet_selection=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
                                             timeout=Duration.minutes(30))

        cfnProject: codebuild.CfnProject
        cfnProject = codeBuildProject.node.default_child
        cfnProject.file_system_locations = [codebuild.CfnProject.ProjectFileSystemLocationProperty(
            identifier='efs1',
            location=fs.file_system_id + ".efs." + Stack.of(self).region + ".amazonaws.com:/",
            mount_point='/mnt/python',
            type='EFS',
            mount_options="nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2"
        )]
        cfnProject.logs_config = {
            "cloudWatchLogs": {
                "status": "ENABLED"
            }
        }

        # Trigger the CodeBuild project to install Python packages to the EFS
        triggerBuildProject = cr.AwsCustomResource(self, 'eeg-test-triggerCodeBuild',
                                                   on_create=cr.AwsSdkCall(service='CodeBuild',
                                                                           action='startBuild',
                                                                           parameters={
                                                                               "projectName": codeBuildProject.project_name
                                                                           },
                                                                           physical_resource_id=cr.PhysicalResourceId.from_response('build.id')),
                                                   policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                                                       resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
                                                   ))

        codeBuildProject.node.add_dependency(efsAccessPoint)

        CfnOutput(self, 'LambdaFunctionName', value=executeBidsConverter.function_name)
