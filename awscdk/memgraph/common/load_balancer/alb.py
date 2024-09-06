from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_ec2 as ec2

class ALBResources:
  def createResources(self, ns, config):
    
    # Import VPC
    vpc = ec2.Vpc.from_lookup(self, "VPC",
      vpc_id = config['main']['vpc_id']
    )

    # Create LB
    self.LB = elbv2.ApplicationLoadBalancer(self,
       "lb",
       vpc=vpc,
       load_balancer_name="{}-{}-alb".format(config['main']['resource_prefix'], ns),
       internet_facing=config.getboolean('alb', 'internet_facing')
       )