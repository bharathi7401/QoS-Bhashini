# Outputs for Bhashini QoS Monitoring Stack

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.main.arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "Application Load Balancer ARN"
  value       = aws_lb.main.arn
}

output "grafana_target_group_arn" {
  description = "Grafana target group ARN"
  value       = aws_lb_target_group.grafana.arn
}

output "efs_file_system_id" {
  description = "EFS file system ID"
  value       = aws_efs_file_system.main.id
}

output "efs_dns_name" {
  description = "EFS DNS name"
  value       = aws_efs_file_system.main.dns_name
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log group names"
  value = {
    influxdb      = aws_cloudwatch_log_group.influxdb.name
    grafana       = aws_cloudwatch_log_group.grafana.name
    data_simulator = aws_cloudwatch_log_group.data_simulator.name
  }
}

output "security_groups" {
  description = "Security group IDs"
  value = {
    alb = aws_security_group.alb.id
    ecs = aws_security_group.ecs.id
  }
}

output "grafana_access_info" {
  description = "Grafana access information"
  value = {
    url      = "http://${aws_lb.main.dns_name}"
    username = "admin"
    password = "admin123"
  }
}

output "influxdb_access_info" {
  description = "InfluxDB access information"
  value = {
    url      = "http://${aws_ecs_service.influxdb.name}.${aws_ecs_cluster.main.name}:8086"
    username = "admin"
    password = "admin123"
    token    = "admin-token-123"
    org      = "bhashini"
    bucket   = "qos_metrics"
  }
}

output "data_simulator_access_info" {
  description = "Data simulator access information"
  value = {
    health_url = "http://${aws_ecs_service.data_simulator.name}.${aws_ecs_cluster.main.name}:8000/health"
    influxdb_url = "http://${aws_ecs_service.influxdb.name}.${aws_ecs_cluster.main.name}:8086"
  }
}
