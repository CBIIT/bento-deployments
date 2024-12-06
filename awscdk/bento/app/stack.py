import boto3
from configparser import ConfigParser
from constructs import Construct

from aws_cdk import Stack
from aws_cdk import RemovalPolicy
from aws_cdk import SecretValue
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_opensearchservice as opensearch
from aws_cdk import aws_kms as kms
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_certificatemanager as cfm
# from aws_cdk import aws_cloudfront as cloudfront

from services import frontend, backend, files, authn, authz

class Stack(Stack):
    def __init__(self, scope: Construct, **kwargs) -> None:
        super().__init__(scope, **kwargs)

        ### Read config
        config = ConfigParser()
        config.read('config.ini')
        
        self.namingPrefix = "{}-{}".format(config['main']['resource_prefix'], config['main']['tier'])

        if config.has_option('main', 'subdomain'):
            self.app_url = "https://{}.{}".format(config['main']['subdomain'], config['main']['domain'])
        else:
            self.app_url = "https://{}".format(config['main']['domain'])
        
        ### Import VPC
        self.VPC = ec2.Vpc.from_lookup(self, "VPC",
            vpc_id = config['main']['vpc_id']
        )

        ### Opensearch Cluster
        if config['os']['endpoint_type'] == 'vpc':
            vpc = self.VPC
            vpc_subnets=[{
                'subnets': [self.VPC.private_subnets[0]],
            }]
        else:
            vpc = None
            vpc_subnets=[{}]

        self.osDomain = opensearch.Domain(self,
            "opensearch",
            version=opensearch.EngineVersion.open_search(config['os']['version']),
            vpc=vpc,
            #access_policies=[self.osPolicyStatement],
            
            zone_awareness=opensearch.ZoneAwarenessConfig(
                enabled=False
            ),
            capacity=opensearch.CapacityConfig(
                data_node_instance_type=config['os']['data_node_instance_type'],
                multi_az_with_standby_enabled=False
            ),
            vpc_subnets=vpc_subnets,
            removal_policy=RemovalPolicy.DESTROY,
            #advanced_options={"override_main_response_version" : "true"}
        )

        # ### Cloudfront
        # self.cf_distribution = cloudfront.Distribution(self, "cf_distro",
        #     default_behavior=cloudfront.BehaviorOptions(
        #         origin=origins.S3Origin(s3_bucket),
        #     )
        # )
        
        ### Secrets
        # Read in cloudfront private key
        with open("private_key.pem", "r") as file:
            cf_private_key = file.read()

        print(cf_private_key)

        self.secret = secretsmanager.Secret(self, "Secret",
            secret_name="{}/{}/{}".format(config['main']['resource_prefix'], config['main']['tier'], "test"),
            secret_object_value={
                "neo4j_user": SecretValue.unsafe_plain_text(config['db']['neo4j_user']),
                "neo4j_pass": SecretValue.unsafe_plain_text(config['db']['neo4j_pass']),
                "es_host": SecretValue.unsafe_plain_text(self.osDomain.domain_endpoint),
                "cf_private_key": SecretValue.unsafe_plain_text(cf_private_key),
            }
        )

        ### ALB
        self.ALB = elbv2.ApplicationLoadBalancer(self,
            "alb",
            vpc=self.VPC,
            internet_facing=config.getboolean('alb', 'internet_facing')
        )

        self.ALB.add_redirect(
            source_protocol=elbv2.ApplicationProtocol.HTTP,
            source_port=80,
            target_protocol=elbv2.ApplicationProtocol.HTTPS,
            target_port=443)

        # Get certificate ARN for specified domain name
        client = boto3.client('acm')
        response = client.list_certificates(
            CertificateStatuses=[
                'ISSUED',
            ],
        )

        for cert in response["CertificateSummaryList"]:
            if ('*.{}'.format(config['main']['domain']) in cert.values()):
                certARN = cert['CertificateArn']

        alb_cert = cfm.Certificate.from_certificate_arn(self, "alb-cert",
            certificate_arn=certARN)
        
        self.listener = self.ALB.add_listener("PublicListener",
            certificates=[
                alb_cert
            ],
            port=443)

        # Add a fixed error message when browsing an invalid URL
        self.listener.add_action("ECS-Content-Not-Found",
            action=elbv2.ListenerAction.fixed_response(200,
                message_body="The requested resource is not available"))

        ### ECS Cluster
        self.kmsKey = kms.Key(self, "ECSExecKey")

        self.ECSCluster = ecs.Cluster(self,
            "ecs",
            vpc=self.VPC,
            execute_command_configuration=ecs.ExecuteCommandConfiguration(
                kms_key=self.kmsKey
            ),
        )

        ### Fargate
        # Frontend Service
        frontend.frontendService.createService(self, config)

        # Backend Service
        backend.backendService.createService(self, config)

        # Files Service
        files.filesService.createService(self, config)

        # AuthN Service
        authn.authnService.createService(self, config)

        # AuthZ Service
        authz.authzService.createService(self, config)