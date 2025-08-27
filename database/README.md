# Database Management System

This directory contains the database management tools for the Business Intelligence system, including initialization, migration, backup, and restore functionality.

## Overview

The database management system provides:
- **Database Initialization**: SQL scripts to create the complete schema
- **Migration Tools**: Convert between SQLite and MySQL databases
- **Backup & Restore**: Automated backup creation and restoration
- **Configuration Management**: Centralized configuration for all database operations

## Directory Structure

```
database/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── backup_config.json                 # Backup configuration
├── profiling-db-init.sql              # Database initialization script
├── migrate-sqlite-to-mysql.py         # Migration script
└── backup-restore.py                  # Backup and restore tool
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

#### For MySQL:
```bash
mysql -u root -p < profiling-db-init.sql
```

#### For SQLite:
```bash
sqlite3 profiling.db < profiling-db-init.sql
```

### 3. Create Initial Backup

```bash
python backup-restore.py backup --type all
```

## Database Schema

The system uses the following core tables:

### Customer Profiles
- **customer_profiles**: Main customer information
- **profile_history**: Audit trail for profile changes

### Value Estimation
- **value_estimates**: Business value calculations
- **value_trends**: Historical value metrics

### Recommendations
- **recommendations**: Optimization suggestions
- **recommendation_feedback**: User feedback on recommendations
- **implementation_tracking**: Implementation status

### Templates
- **sector_kpi_templates**: Sector-specific KPI definitions
- **use_case_templates**: Use case implementation patterns
- **dashboard_templates**: Grafana dashboard templates

## Database Migration

### SQLite to MySQL Migration

```bash
python migrate-sqlite-to-mysql.py
```

**Prerequisites:**
- MySQL server running
- User with appropriate permissions
- Updated configuration in the script

**Migration Process:**
1. Connects to both databases
2. Creates MySQL tables with proper data types
3. Migrates all data
4. Creates indexes and constraints
5. Generates migration report

### Configuration

Update the MySQL configuration in the migration script:

```python
mysql_config = {
    'host': 'localhost',
    'user': 'bi_user',
    'password': 'bi_password',
    'database': 'bi_profiling',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
```

## Backup and Restore

### Creating Backups

```bash
# Backup all databases
python backup-restore.py backup --type all

# Backup only SQLite databases
python backup-restore.py backup --type sqlite

# Backup only MySQL database
python backup-restore.py backup --type mysql
```

### Restoring from Backups

```bash
# Restore SQLite database
python backup-restore.py restore --type sqlite --source backup_file.db.gz --target profiling.db

# Restore MySQL database
python backup-restore.py restore --type mysql --source backup_file.sql.gz
```

### Backup Management

```bash
# List all backups
python backup-restore.py list

# Verify backup integrity
python backup-restore.py verify --source backup_file.db.gz

# Clean up old backups (keep last 30 days)
python backup-restore.py cleanup --days 30

# Generate backup report
python backup-restore.py report
```

## Configuration

### Backup Configuration

Edit `backup_config.json` to customize:

- **Backup Directory**: Where backups are stored
- **Retention Policy**: How long to keep backups
- **Compression**: Enable/disable compression
- **Notifications**: Email/Slack alerts
- **Schedules**: Automated backup timing

### Example Configuration

```json
{
  "backup_dir": "backups",
  "retention_days": 30,
  "compression": true,
  "schedules": {
    "daily": {
      "enabled": true,
      "time": "02:00",
      "type": "all"
    }
  }
}
```

## Automated Backups

### Cron Job Setup

Add to your crontab for automated daily backups:

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/project && python database/backup-restore.py backup --type all

# Weekly cleanup on Sundays at 3 AM
0 3 * * 0 cd /path/to/project && python database/backup-restore.py cleanup --days 30
```

### Systemd Timer (Alternative)

Create `/etc/systemd/system/bi-backup.timer`:

```ini
[Unit]
Description=BI System Daily Backup
Requires=bi-backup.service

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Create `/etc/systemd/system/bi-backup.service`:

```ini
[Unit]
Description=BI System Backup Service
Type=oneshot
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 database/backup-restore.py backup --type all

[Install]
WantedBy=multi-user.target
```

## Monitoring and Alerts

### Backup Monitoring

The system provides monitoring capabilities:

- **Backup Duration**: Track backup performance
- **Backup Size**: Monitor storage usage
- **Verification Results**: Ensure backup integrity
- **Failure Alerts**: Get notified of backup issues

### Integration with Existing Monitoring

Export metrics to Prometheus:

```python
from prometheus_client import Counter, Histogram, Gauge

backup_duration = Histogram('backup_duration_seconds', 'Backup duration in seconds')
backup_size = Gauge('backup_size_bytes', 'Backup size in bytes')
backup_failures = Counter('backup_failures_total', 'Total backup failures')
```

## Troubleshooting

### Common Issues

#### Migration Failures
- **Connection Issues**: Check MySQL server status and credentials
- **Permission Errors**: Ensure user has CREATE, INSERT, INDEX privileges
- **Data Type Issues**: Review data type mappings in migration script

#### Backup Failures
- **Disk Space**: Check available storage in backup directory
- **Permission Issues**: Ensure write access to backup directory
- **Compression Errors**: Verify gzip support and available memory

#### Restore Failures
- **File Corruption**: Verify backup file integrity
- **Schema Mismatch**: Ensure target database schema is compatible
- **Data Conflicts**: Check for existing data that might conflict

### Debug Mode

Enable verbose logging:

```bash
export PYTHONPATH=/path/to/project
python -u database/backup-restore.py backup --type all 2>&1 | tee backup.log
```

### Log Files

Check log files for detailed error information:
- Application logs in the backup directory
- System logs: `journalctl -u bi-backup.service`

## Performance Considerations

### Backup Performance
- **Parallel Backups**: Configure multiple backup processes
- **Chunked Backups**: Split large databases into manageable chunks
- **Compression**: Balance between speed and storage efficiency

### Migration Performance
- **Batch Processing**: Process data in batches to manage memory
- **Index Management**: Create indexes after data migration
- **Transaction Control**: Use appropriate transaction sizes

## Security

### Access Control
- **Database Users**: Use dedicated users with minimal required privileges
- **File Permissions**: Restrict access to backup files
- **Network Security**: Secure database connections

### Encryption
- **Backup Encryption**: Enable encryption for sensitive data
- **Transport Security**: Use SSL/TLS for database connections
- **Key Management**: Secure encryption key storage

## Development

### Adding New Database Types

1. Extend the `DatabaseBackupRestore` class
2. Implement backup/restore methods
3. Add verification logic
4. Update configuration schema

### Testing

Run the test suite:

```bash
pytest database/tests/ -v
```

### Code Quality

Format and lint code:

```bash
black database/
flake8 database/
mypy database/
```

## Support

### Getting Help
- Check the troubleshooting section above
- Review log files for error details
- Consult the main project documentation

### Contributing
- Follow the project's coding standards
- Add tests for new functionality
- Update documentation for changes

## License

This database management system is part of the Business Intelligence project and follows the same license terms.
