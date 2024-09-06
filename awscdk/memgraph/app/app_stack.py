#import os, sys
#from configparser import ConfigParser
from aws_cdk import Stack
from constructs import Construct
# from common.load_balancer import alb as alb
from common.load_balancer import lbSelection as lb

class appStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #ALB = alb.ALBResources.createResources(self, construct_id)
        LB = lb.LBSelection.createResources(self, construct_id)