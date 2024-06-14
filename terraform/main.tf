module "alb" {
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/loadbalancer?ref=v1.18"
  vpc_id = var.vpc_id
  alb_log_bucket_name = module.s3.bucket_name
  env = terraform.workspace
  alb_internal = var.internal_alb
  alb_type = var.lb_type
  alb_subnet_ids = local.alb_subnet_ids
  tags = var.tags
  stack_name = var.stack_name
  alb_certificate_arn = data.aws_acm_certificate.amazon_issued.arn
  program = "fnl"
  resource_prefix = "${var.stack_name}-${terraform.workspace}"
}

module "s3" {
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/s3?ref=v1.18"
  bucket_name = local.alb_log_bucket_name
  env = terraform.workspace
  tags = var.tags
  s3_force_destroy = var.s3_force_destroy
  days_for_archive_tiering = 125
  days_for_deep_archive_tiering = 180
  s3_enable_access_logging = false
  s3_access_log_bucket_id = ""
  resource_prefix = "${var.stack_name}-${terraform.workspace}"
}

module "ecs" {
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/ecs?ref=v1.18"
  stack_name = var.stack_name
  tags = var.tags
  vpc_id = var.vpc_id
  add_opensearch_permission = var.add_opensearch_permission
  ecs_subnet_ids = var.private_subnet_ids
  application_url = local.application_url
  env = terraform.workspace
  microservices = var.microservices
  alb_https_listener_arn = module.alb.alb_https_listener_arn
  target_account_cloudone = var.target_account_cloudone
  allow_cloudwatch_stream = var.allow_cloudwatch_stream
  central_ecr_account_id  = data.aws_caller_identity.current.account_id
  resource_prefix = "${var.stack_name}-${terraform.workspace}"
}

#create ecr
module "ecr" {
   count = var.create_ecr_repos ? 1: 0
   source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/ecr?ref=v1.18"
   stack_name = var.stack_name
   ecr_repo_names = var.ecr_repo_names
   tags = var.tags
   create_env_specific_repo = var.create_env_specific_repo
   env = terraform.workspace
   enable_ecr_replication = var.enable_ecr_replication
   replication_destination_registry_id = var.replication_destination_registry_id
   replication_source_registry_id = var.replication_source_registry_id 
   allow_ecr_replication = var.allow_ecr_replication
}

#create opensearch
module "opensearch" {
  count = var.create_opensearch_cluster ? 1: 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/opensearch?ref=neo4j"
  stack_name = var.stack_name
  tags = var.tags
  opensearch_instance_type = var.opensearch_instance_type
  env = terraform.workspace
  opensearch_subnet_ids = var.private_subnet_ids
  opensearch_version = var.opensearch_version
  automated_snapshot_start_hour =  var.automated_snapshot_start_hour
  opensearch_ebs_volume_size    =  var.opensearch_ebs_volume_size
  opensearch_instance_count     =  var.opensearch_instance_count
  opensearch_log_types           = ["INDEX_SLOW_LOGS"]
  create_os_service_role        = var.create_os_service_role
  multi_az_enabled = var.multi_az_enabled
  vpc_id = var.vpc_id
  opensearch_autotune_rollback_type = "NO_ROLLBACK"
  create_cloudwatch_log_policy = var.create_cloudwatch_log_policy
}

module "dns" {
  count = var.create_dns_record ? 1: 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/route53?ref=neo4j"
  env = terraform.workspace
  alb_zone_id = module.alb.alb_zone_id
  alb_dns_name = module.alb.alb_dns_name
  application_subdomain = var.application_subdomain
  domain_name = var.domain_name
}

module "neo4j" {
  count = var.create_db_instance ? 1: 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/neo4j?ref=neo4j"
  env = terraform.workspace
  vpc_id = var.vpc_id
  db_subnet_id = var.db_subnet_id
  db_instance_volume_size = var.db_instance_volume_size
  public_ssh_key_ssm_parameter_name = var.public_ssh_key_ssm_parameter_name
  stack_name = var.stack_name
  db_private_ip = var.db_private_ip
  database_instance_type = var.database_instance_type
  tags = var.tags
  database_name = var.neo4j_database_name
}


module "user_neo4j" {
  count = var.create_db_instance ? 1: 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/neo4j?ref=neo4j"
  env = terraform.workspace
  vpc_id = var.vpc_id
  db_subnet_id = var.db_subnet_id
  db_instance_volume_size = var.db_instance_volume_size
  public_ssh_key_ssm_parameter_name = var.public_ssh_key_ssm_parameter_name
  stack_name = var.stack_name
  db_private_ip = var.user_neo4j_db_private_ip
  database_instance_type = var.database_instance_type
  tags = var.tags
  database_name = "neo4j-user"
  create_instance_profile = false
  create_security_group = false
  create_bootstrap_script = false
  db_iam_profile_name = var.db_iam_profile_name
  db_security_group_name = var.db_security_group_name
  db_boostrap_ssm_document  = var.db_boostrap_ssm_document
}


#aurora
module "aurora" {
  count = var.create_aurora_rds ? 1: 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/aurora?ref=neo4j"
  env    =  terraform.workspace
  stack_name = var.stack_name
  tags = var.tags
  vpc_id = var.vpc_id
  db_engine_mode = var.db_engine_mode
  db_engine_version = var.db_engine_version
  db_instance_class = var.db_instance_class
  db_engine_type = var.db_engine_type
  master_username = var.master_username
  allowed_ip_blocks = var.allowed_ip_blocks
  db_subnet_ids = var.db_subnet_ids
  database_name = var.database_name
}

#cloudfront
module "cloudfront" {
  count = var.create_cloudfront ? 1 : 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/cloudfront?ref=cds-stage"
  alarms = var.alarms
  domain_name = var.domain_name
  cloudfront_distribution_bucket_name = var.cloudfront_distribution_bucket_name
  cloudfront_slack_channel_name =  var.cloudfront_slack_channel_name
  env = terraform.workspace
  stack_name = var.stack_name
  slack_secret_name = var.slack_secret_name
  tags = var.tags
  create_files_bucket = var.create_files_bucket
  target_account_cloudone = var.target_account_cloudone
  public_key_path = file("${path.module}/workspace/gmb/gmb_public_key.pem")
}

module "s3-replication-source" {
  count = var.create_s3_replication ? 1 : 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/s3-replication-source?ref=neo4j"
  destination_bucket_name = var.destination_bucket_name 
  env =  terraform.workspace
  source_bucket_name = var.source_bucket_name
  stack_name = var.stack_name
  tags = var.tags
  target_account_cloudone = var.target_account_cloudone
  create_source_bucket = var.create_source_bucket 
  replication_destination_account_id = var.replication_destination_account_id
}

module "s3-replication-destination" {
  count = var.enable_s3_replication ? 1 : 0
  source = "git::https://github.com/CBIIT/datacommons-devops.git//terraform/modules/s3-replication-destination?ref=neo4j"
  destination_bucket_name = var.destination_bucket_name 
  tags = var.tags
  replication_role_arn = var.replication_role_arn
  create_destination_bucket = var.create_destination_bucket
}
