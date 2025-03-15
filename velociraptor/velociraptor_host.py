from aws_cdk import (
    Stack,
    aws_ec2 as _ec2,
    aws_iam as _iam,
    aws_s3 as _s3,
    aws_ssm as _ssm
)

from constructs import Construct

class VelociraptorHost(Stack):

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
            parameter_name = '/network/az'
        )

        eipid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'eipid',
            parameter_name = '/network/eip'
        )

        rtbid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'rtbid',
            parameter_name = '/network/rtb'
        )

        sgid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'sgid',
            parameter_name = '/network/sg'
        )

        subid = _ssm.StringParameter.from_string_parameter_attributes(
            self, 'subid',
            parameter_name = '/network/subnet'
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

        sg = _ec2.SecurityGroup.from_security_group_id(
            self, 'sg',
            security_group_id = sgid.string_value,
            mutable = False
        )

    ### AMI ###

        ubuntu = _ec2.MachineImage.generic_linux(
            {
                'us-east-1': 'ami-0a7a4e87939439934' # Published: 2025-01-15
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
            instance_type = _ec2.InstanceType('t4g.small'),
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
                        8, encrypted = True
                    )
                ),
                _ec2.BlockDevice(
                    device_name = '/dev/sdf',
                    volume = _ec2.BlockDeviceVolume.ebs(
                        12, encrypted = True
                    )
                )
            ]
        )

        parameter = _ssm.StringParameter(
            self, 'parameter',
            description = 'EC2 Instance ID',
            parameter_name = '/network/ec2',
            string_value = instance.instance_id,
            tier = _ssm.ParameterTier.STANDARD
        )

    ### EIP ###
            
        associate = _ec2.CfnEIPAssociation(
            self, 'associate',
            allocation_id = eipid.string_value,
            instance_id = instance.instance_id,
        )
