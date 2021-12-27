from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_events as _events,
    aws_events_targets as _targets,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs
)

from constructs import Construct

class RemedyUnusedLambdaContainersStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        role = _iam.Role(
            self, 'role', 
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )
        
        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )
        
        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'ec2:DescribeRegions',
                    'ecr:BatchDeleteImage',
                    'ecr:DescribeRepositories',
                    'ecr:ListImages',
                    'lambda:ListFunctions'
                ],
                resources = ['*']
            )
        )

        remedy = _lambda.Function(
            self, 'remedy',
            code = _lambda.Code.from_asset('remedy'),
            handler = 'remedy.handler',
            runtime = _lambda.Runtime.PYTHON_3_9,
            architecture = _lambda.Architecture.ARM_64,
            timeout = Duration.seconds(900),
            memory_size = 128,
            role = role
        )
       
        logs = _logs.LogGroup(
            self, 'logs',
            log_group_name = '/aws/lambda/'+remedy.function_name,
            retention = _logs.RetentionDays.ONE_DAY,
            removal_policy = RemovalPolicy.DESTROY
        )

        event = _events.Rule(
            self, 'event',
            schedule = _events.Schedule.cron(
                minute = '0',
                hour = '11',
                month = '*',
                week_day = '*',
                year = '*'
            )
        )
        event.add_target(_targets.LambdaFunction(remedy))