#!/usr/bin/env python3
import os

import aws_cdk as cdk

from velociraptor.velociraptor_host import VelociraptorHost
from velociraptor.velociraptor_stack import VelociraptorStack

app = cdk.App()

VelociraptorHost(
    app, 'VelociraptorHost',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-1'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

VelociraptorStack(
    app, 'VelociraptorStack',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-1'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('Alias','lukach.net')
cdk.Tags.of(app).add('GitHub','https://github.com/jblukach/velociraptor')

app.synth()