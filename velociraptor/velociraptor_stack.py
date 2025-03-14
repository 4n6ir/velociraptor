from aws_cdk import (
    Stack,
    aws_ec2 as _ec2,
    aws_ssm as _ssm
)

from constructs import Construct

class VelociraptorStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    ### VPC ###

        vpc = _ec2.Vpc(
            self, 'vpc',
            ip_addresses = _ec2.IpAddresses.cidr('10.255.255.0/24'),
            max_azs = 1,
            nat_gateways = 0,
            enable_dns_hostnames = True,
            enable_dns_support = True,
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

    ### SUBNET ###

        subnetids = []
        for subnet in vpc.public_subnets: # vpc.private_subnets
            subnetid = {}
            subnetid['subnet_id'] = subnet.subnet_id
            subnetid['availability_zone'] = subnet.availability_zone
            subnetid['route_table'] = subnet.route_table
            subnetids.append(subnetid)

        subnetparameter = _ssm.StringParameter(
            self, 'subnetparameter',
            description = 'Public Subnet ID',
            parameter_name = '/network/subnet',
            string_value = subnetids[0]['subnet_id'],
            tier = _ssm.ParameterTier.STANDARD
        )

        azparameter = _ssm.StringParameter(
            self, 'azparameter',
            description = 'Availability Zone',
            parameter_name = '/network/az',
            string_value = subnetids[0]['availability_zone'],
            tier = _ssm.ParameterTier.STANDARD
        )

        rtbparameter = _ssm.StringParameter(
            self, 'rtbparameter',
            description = 'Route Table ID',
            parameter_name = '/network/rtb',
            string_value = subnetids[0]['route_table'].route_table_id,
            tier = _ssm.ParameterTier.STANDARD
        )

    ### NACL ###

        nacl = _ec2.NetworkAcl(
            self, 'nacl',
            vpc = vpc
        )

        nacl.add_entry(
            'ingress100',
            rule_number = 100,
            cidr = _ec2.AclCidr.ipv4('0.0.0.0/0'),
            traffic = _ec2.AclTraffic.all_traffic(),
            rule_action = _ec2.Action.ALLOW,
            direction = _ec2.TrafficDirection.INGRESS
        )

        nacl.add_entry(
            'egress100',
            rule_number = 100,
            cidr = _ec2.AclCidr.ipv4('0.0.0.0/0'),
            traffic = _ec2.AclTraffic.all_traffic(),
            rule_action = _ec2.Action.ALLOW,
            direction = _ec2.TrafficDirection.EGRESS
        )

    ### SECURITY GROUP ###

        sg = _ec2.SecurityGroup(
            self, 'sg',
            vpc = vpc,
            allow_all_outbound = True,
            description = 'Outbount Internet Access',
            security_group_name = 'Outbount Internet Access'
        )

        sgparameter = _ssm.StringParameter(
            self, 'sgparameter',
            description = 'Security Group ID',
            parameter_name = '/network/sg',
            string_value = sg.security_group_id,
            tier = _ssm.ParameterTier.STANDARD
        )

    ### STATIC IP ###

        eip = _ec2.CfnEIP(
            self, 'eip'
        )

        eipparameter = _ssm.StringParameter(
            self, 'eipparameter',
            description = 'Static EIP Address',
            parameter_name = '/network/eip',
            string_value = eip.attr_allocation_id,
            tier = _ssm.ParameterTier.STANDARD
        )
