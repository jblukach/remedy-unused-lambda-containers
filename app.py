#!/usr/bin/env python3
import os

import aws_cdk as cdk

from remedy_unused_lambda_containers.remedy_unused_lambda_containers_stack import RemedyUnusedLambdaContainersStack

app = cdk.App()

RemedyUnusedLambdaContainersStack(
    app, 'RemedyUnusedLambdaContainersStack',
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('unused-lambda-containers','unused-lambda-containers')

app.synth()
