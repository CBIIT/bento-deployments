import yaml
import os

parsed_file = yaml.safe_load(open('deployments.yaml'))

for svc in parsed_file['services']:
    envVarName = svc.upper() + '_IMAGE_VALUE'
    print("{}={}".format(envVarName, parsed_file['services'][svc]['image']))
    
    # os.environ[envVarName] = parsed_file['services'][svc]['image']
