#!/usr/bin/env python3
import os, sys
import logging
import aws_cdk as cdk

#from configparser import ConfigParser
from getArgs import getArgs
# from aws_cdk import core as cdk
# from aws_cdk import core

from app.app_stack import appStack

if __name__=="__main__":
  tierName = getArgs.set_tier(sys.argv[1:])
  if not tierName:
    print('Please specify the tier to build:  awsApp.py -t <tier>')
    sys.exit(1)

  logging.basicConfig(format='%(asctime)s [%(levelname)5s] %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        level=logging.NOTSET)

  

  app = cdk.App()
  #logging.info(f"{os.environ['AWS_DEFAULT_ACCOUNT']} is account, and {os.environ['AWS_DEFAULT_REGION']} is region")

  stack = appStack(
    app,
    tierName,
    env=cdk.Environment(
      account=os.environ["AWS_DEFAULT_ACCOUNT"],
      region=os.environ["AWS_DEFAULT_REGION"],
    ),
  )

  # tags = dict(s.split(':') for s in stack.config[tierName]['tags'].split(","))

  # for tag,value in tags.items():
  #   core.Tags.of(stack).add(tag, value)

  app.synth()