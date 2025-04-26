from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_ec2 as _ec2,
    aws_s3 as _s3,
    aws_ssm as _ssm
)

from constructs import Construct

class VelociraptorNetwork(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    ### S3 ###

        bucket = _s3.Bucket(
            self, 'bucket',
            bucket_name = 'raptordistributor',
            encryption = _s3.BucketEncryption.S3_MANAGED,
            block_public_access = _s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy = RemovalPolicy.DESTROY,
            auto_delete_objects = True,
            enforce_ssl = True,
            versioned = False
        )

    ### VPC ###

        vpc = _ec2.Vpc(
            self, 'vpc',
            ip_addresses = _ec2.IpAddresses.cidr('10.255.255.0/24'),
            ip_protocol = _ec2.IpProtocol.DUAL_STACK,
            enable_dns_hostnames = True,
            enable_dns_support = True,
            nat_gateways = 0,
            max_azs = 1,
            subnet_configuration = [
                _ec2.SubnetConfiguration(
                    cidr_mask = 28,
                    name = 'Public',
                    subnet_type = _ec2.SubnetType.PUBLIC
                )
            ],
            gateway_endpoints = {
                'DYNAMODB': _ec2.GatewayVpcEndpointOptions(
                    service = _ec2.GatewayVpcEndpointAwsService.DYNAMODB
                ),
                'S3': _ec2.GatewayVpcEndpointOptions(
                    service = _ec2.GatewayVpcEndpointAwsService.S3
                )
            }
        )

        vpcparameter = _ssm.StringParameter(
            self, 'vpcparameter',
            description = 'Public VPC ID',
            parameter_name = '/network/vpc',
            string_value = vpc.vpc_id,
            tier = _ssm.ParameterTier.STANDARD
        )

    ### PUBLIC SUBNETS ###

        publicsubnets = []

        for subnet in vpc.public_subnets:
            subnetid = {}
            subnetid['subnet_id'] = subnet.subnet_id
            subnetid['availability_zone'] = subnet.availability_zone
            subnetid['route_table'] = subnet.route_table
            publicsubnets.append(subnetid)

        publicsubnet = _ssm.StringParameter(
            self, 'publicsubnet',
            description = 'Public Subnet ID',
            parameter_name = '/network/publicsubnet',
            string_value = publicsubnets[0]['subnet_id'],
            tier = _ssm.ParameterTier.STANDARD
        )

        publiczone = _ssm.StringParameter(
            self, 'publiczone',
            description = 'Public Availability Zone',
            parameter_name = '/network/publiczone',
            string_value = publicsubnets[0]['availability_zone'],
            tier = _ssm.ParameterTier.STANDARD
        )

        publicroute = _ssm.StringParameter(
            self, 'publicroute',
            description = 'Public Route ID',
            parameter_name = '/network/publicroute',
            string_value = publicsubnets[0]['route_table'].route_table_id,
            tier = _ssm.ParameterTier.STANDARD
        )
