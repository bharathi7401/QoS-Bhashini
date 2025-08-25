# ECS Services
resource "aws_ecs_service" "influxdb" {
  name            = "bhashini-qos-influxdb"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.influxdb.arn
  desired_count   = var.desired_capacity
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs.id]
    subnets          = aws_subnet.private[*].id
    assign_public_ip = false
  }

  depends_on = [aws_efs_mount_target.main]

  tags = {
    Name = "bhashini-qos-influxdb-service"
  }
}

resource "aws_ecs_service" "grafana" {
  name            = "bhashini-qos-grafana"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.grafana.arn
  desired_count   = var.desired_capacity
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs.id]
    subnets          = aws_subnet.private[*].id
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.grafana.arn
    container_name   = "grafana"
    container_port   = 3000
  }

  depends_on = [aws_ecs_service.influxdb]

  tags = {
    Name = "bhashini-qos-grafana-service"
  }
}

resource "aws_ecs_service" "data_simulator" {
  name            = "bhashini-qos-data-simulator"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.data_simulator.arn
  desired_count   = var.desired_capacity
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs.id]
    subnets          = aws_subnet.private[*].id
    assign_public_ip = false
  }

  depends_on = [aws_ecs_service.influxdb]

  tags = {
    Name = "bhashini-qos-data-simulator-service"
  }
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "influxdb" {
  family                   = "bhashini-qos-influxdb"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "influxdb"
      image = "influxdb:2.7-alpine"
      
      portMappings = [
        {
          containerPort = 8086
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DOCKER_INFLUXDB_INIT_MODE"
          value = "setup"
        },
        {
          name  = "DOCKER_INFLUXDB_INIT_USERNAME"
          value = "admin"
        },
        {
          name  = "DOCKER_INFLUXDB_INIT_PASSWORD"
          value = "admin123"
        },
        {
          name  = "DOCKER_INFLUXDB_INIT_ORG"
          value = "bhashini"
        },
        {
          name  = "DOCKER_INFLUXDB_INIT_BUCKET"
          value = "qos_metrics"
        },
        {
          name  = "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"
          value = "admin-token-123"
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "influxdb-data"
          containerPath = "/var/lib/influxdb2"
          readOnly      = false
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.influxdb.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  volume {
    name = "influxdb-data"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.main.id
      root_directory = "/influxdb"
    }
  }

  tags = {
    Name = "bhashini-qos-influxdb-task"
  }
}

resource "aws_ecs_task_definition" "grafana" {
  family                   = "bhashini-qos-grafana"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "grafana"
      image = "grafana/grafana:10.2.0"
      
      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "GF_SECURITY_ADMIN_USER"
          value = "admin"
        },
        {
          name  = "GF_SECURITY_ADMIN_PASSWORD"
          value = "admin123"
        },
        {
          name  = "GF_INSTALL_PLUGINS"
          value = "grafana-clock-panel,grafana-worldmap-panel"
        },
        {
          name  = "GF_AUTH_API_KEYS_ENABLED"
          value = "true"
        },
        {
          name  = "GF_USERS_AUTO_ASSIGN_ORG"
          value = "true"
        },
        {
          name  = "GF_USERS_AUTO_ASSIGN_ORG_ROLE"
          value = "Viewer"
        },
        {
          name  = "GF_USERS_ALLOW_SIGN_UP"
          value = "true"
        },
        {
          name  = "GF_USERS_VERIFY_EMAIL_ENABLED"
          value = "false"
        },
        {
          name  = "GF_DEFAULT_ORG_NAME"
          value = "Bhashini"
        },
        {
          name  = "GF_SECURITY_DISABLE_GRAVATAR"
          value = "true"
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "grafana-data"
          containerPath = "/var/lib/grafana"
          readOnly      = false
        },
        {
          sourceVolume  = "grafana-config"
          containerPath = "/etc/grafana/provisioning"
          readOnly      = true
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.grafana.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  volume {
    name = "grafana-data"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.main.id
      root_directory = "/grafana"
    }
  }

  volume {
    name = "grafana-config"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.main.id
      root_directory = "/grafana-config"
    }
  }

  tags = {
    Name = "bhashini-qos-grafana-task"
  }
}

resource "aws_ecs_task_definition" "data_simulator" {
  family                   = "bhashini-qos-data-simulator"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "data-simulator"
      image = "bhashini-qos-data-simulator:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "INFLUXDB_URL"
          value = "http://${aws_ecs_service.influxdb.name}.${aws_ecs_cluster.main.name}:8086"
        },
        {
          name  = "INFLUXDB_TOKEN"
          value = "admin-token-123"
        },
        {
          name  = "INFLUXDB_ORG"
          value = "bhashini"
        },
        {
          name  = "INFLUXDB_BUCKET"
          value = "qos_metrics"
        },
        {
          name  = "SIMULATION_INTERVAL"
          value = "10"
        },
        {
          name  = "LOG_LEVEL"
          value = "INFO"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.data_simulator.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  tags = {
    Name = "bhashini-qos-data-simulator-task"
  }
}
