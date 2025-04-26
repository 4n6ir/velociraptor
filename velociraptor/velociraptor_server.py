from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_ec2 as _ec2,
    aws_iam as _iam,
    aws_route53 as _route53,
    aws_s3 as _s3,
    aws_ssm as _ssm
)

from constructs import Construct

class VelociraptorServer(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    ### S3 ###

        bucket = _s3.Bucket.from_bucket_attributes(
            self, 'bucket',
            bucket_name = 'raptordistributor',
        )

    ### SSM ###

        azid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'azid',
            parameter_name = '/network/publiczone'
        )

        rtbid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'rtbid',
            parameter_name = '/network/publicroute'
        )

        subid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'subid',
            parameter_name = '/network/publicsubnet'
        )

        vpcid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'vpcid',
            parameter_name = '/network/vpc'
        )

    ### VPC ###

        vpc = _ec2.Vpc.from_vpc_attributes(
            self, 'vpc',
            vpc_id = vpcid.string_value,
            availability_zones = [
                azid.string_value
            ],
            public_subnet_ids = [
                subid.string_value
            ],
            public_subnet_route_table_ids = [
                rtbid.string_value
            ]
        )

    ### SG ###

        sg = _ec2.SecurityGroup(
            self, 'sg',
            vpc = vpc,
            allow_all_outbound = True,
            allow_all_ipv6_outbound = True,
            description = 'Velociraptor',
            security_group_name = 'Velociraptor'
        )

        sg.add_ingress_rule(_ec2.Peer.any_ipv4(), _ec2.Port.tcp(80), 'HTTP')
        sg.add_ingress_rule(_ec2.Peer.any_ipv6(), _ec2.Port.tcp(80), 'HTTP')
        sg.add_ingress_rule(_ec2.Peer.any_ipv4(), _ec2.Port.tcp(443), 'HTTPS')
        sg.add_ingress_rule(_ec2.Peer.any_ipv6(), _ec2.Port.tcp(443), 'HTTPS')

    ### AMI ###

        ubuntu = _ec2.MachineImage.generic_linux(
            {
                'us-east-1': 'ami-0c4e709339fa8521a' # Published: 2025-03-05
            }
        )

    ### IAM ###

        role = _iam.Role(
            self, 'role',
            assumed_by = _iam.ServicePrincipal(
                'ec2.amazonaws.com'
            )
        )

        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonSSMManagedInstanceCore'
            )
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    's3:GetObject',
                    's3:PutObject'
                ],
                resources = [
                    bucket.arn_for_objects('*')
                ]
            )
        )

    ### EC2 ###

        instance = _ec2.Instance(
            self, 'instance',
            instance_type = _ec2.InstanceType('t4g.nano'),
            machine_image = ubuntu,
            vpc = vpc,
            role = role,
            security_group = sg,
            require_imdsv2 = True,
            propagate_tags_to_volume_on_creation = True,
            block_devices = [
                _ec2.BlockDevice(
                    device_name = '/dev/sda1',
                    volume = _ec2.BlockDeviceVolume.ebs(
                        10, encrypted = True
                    )
                )
            ]
        )

    ### EIP ###

        eip = _ec2.CfnEIP(
            self, 'eip'
        )

        associate = _ec2.CfnEIPAssociation(
            self, 'associate',
            allocation_id = eip.attr_allocation_id,
            instance_id = instance.instance_id,
        )

    ### ROUTE53 ###

        hostzoneid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'hostzoneid',
            parameter_name = '/network/hostzone'
        )

        hostzone = _route53.HostedZone.from_hosted_zone_attributes(
            self, 'hostzone',
            hosted_zone_id = hostzoneid.string_value,
            zone_name = 'lukach.net'
        )

        arecord = _route53.ARecord(
            self, 'arecord',
            zone = hostzone,
            target = _route53.RecordTarget.from_ip_addresses(
                eip.attr_public_ip
            ),
            record_name = 'velociraptor.lukach.net'
        )

        aaarecord = _route53.AaaaRecord(
            self, 'aaarecord',
            zone = hostzone,
            target = _route53.RecordTarget.from_ip_addresses(
                '2600:1f18:34d5:8d00:dc38:9749:d6ed:3258'
            ),
            record_name = 'velociraptor.lukach.net'
        )
