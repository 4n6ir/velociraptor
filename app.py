#!/usr/bin/env python3
import os

import aws_cdk as cdk

from velociraptor.velociraptor_network import VelociraptorNetwork
from velociraptor.velociraptor_server import VelociraptorServer
from velociraptor.velociraptor_ubuntu import VelociraptorUbuntu

app = cdk.App()

VelociraptorNetwork(
    app, 'VelociraptorNetwork',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-1'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

VelociraptorServer(
    app, 'VelociraptorServer',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = 'us-east-1'
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

VelociraptorUbuntu(
    app, 'VelociraptorUbuntu',
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