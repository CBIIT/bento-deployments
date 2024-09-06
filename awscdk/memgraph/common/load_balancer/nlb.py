from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_ec2 as ec2

class NLBResources:
  def createResources(self, ns, config):
    
    # Import VPC
    vpc = ec2.Vpc.from_lookup(self, "VPC",
      vpc_id = config['main']['vpc_id']
    )

    # Create LB
    self.LB = elbv2.NetworkLoadBalancer(self,
       "lb",
       vpc=vpc,
       load_balancer_name="{}-{}-nlb".format(config['main']['resource_prefix'], ns),
       internet_facing=config.getboolean('nlb', 'internet_facing'),
       ip_address_type=elbv2.IpAddressType.DUAL_STACK
       )