#########################
# Database security group
#########################
module "postgresql_security_group" {
  source  = "terraform-aws-modules/security-group/aws//modules/postgresql"
  version = "5.1.0"

  name = "database_sg"
  vpc_id = module.vpc.vpc_id

  ingress_cidr_blocks = ["0.0.0.0/0"]
}


####################################
# Variables common to both instnaces
####################################
locals {
  port              = "5432"
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.micro"
  allocated_storage = 5
  storage_encrypted = false
}


###########
# Master DB
###########
resource "random_password" "password" {
  length  = 16
  special = false
}

module "db" {
  source = "terraform-aws-modules/rds/aws"
  version = "6.2.0"

  identifier = "lambda-postgres"

  engine             = local.engine
  engine_version     = local.engine_version
  instance_class     = local.instance_class
  create_db_instance = var.create_db_instance
  allocated_storage  = local.allocated_storage
  storage_encrypted  = local.storage_encrypted

  db_name  = "lambda"
  username = "lambda"
  password = random_password.password.result
  port     = "5432"

  vpc_security_group_ids = [module.postgresql_security_group.security_group_id]

  maintenance_window     = "Mon:00:00-Mon:03:00"
  backup_window          = "03:00-06:00"

  # Backups are required in order to create a replica
  backup_retention_period = 1

  # DB subnet group
  subnet_ids = module.vpc.database_subnets

  create_db_option_group    = false
  create_db_parameter_group = false
}

############
# Replica DB
############
# module "replica" {
#   source = "terraform-aws-modules/rds/aws"
#   version = "~> 2.0"
#
#   identifier = "lambda-replica-postgres"
#
#   # Source database. For cross-region use this_db_instance_arn
#   replicate_source_db = module.db.this_db_instance_id
#
#   engine            = local.engine
#   engine_version    = local.engine_version
#   instance_class    = local.instance_class
#   create_db_instance = var.create_replica_db_instance
#   allocated_storage = local.allocated_storage
#
#   username = ""
#   password = ""
#   port     = local.port
#
#   vpc_security_group_ids = ["${module.postgresql_security_group.this_security_group_id}"]
#
#   maintenance_window = "Tue:00:00-Tue:03:00"
#   backup_window      = "03:00-06:00"
#
#   # disable backups to create DB faster
#   backup_retention_period = 0
#
#   # Not allowed to specify a subnet group for replicas in the same region
#   create_db_subnet_group = false
#
#   create_db_option_group    = false
#   create_db_parameter_group = false
# }
