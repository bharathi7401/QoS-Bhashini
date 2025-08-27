#!/usr/bin/env python3
"""
Database Backup and Restore Script
This script provides backup and restore functionality for the Business Intelligence system
"""

import sqlite3
import mysql.connector
import json
import logging
import os
import shutil
import gzip
import tarfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackupRestore:
    """Handles database backup and restore operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_dir = Path(config.get('backup_dir', 'backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
    def backup_sqlite(self, db_path: str, backup_name: Optional[str] = None) -> str:
        """Backup SQLite database"""
        try:
            if not os.path.exists(db_path):
                raise FileNotFoundError(f"SQLite database not found: {db_path}")
            
            # Generate backup name if not provided
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"sqlite_backup_{timestamp}.db"
            
            backup_path = self.backup_dir / backup_name
            
            # Create backup
            shutil.copy2(db_path, backup_path)
            
            # Compress backup
            compressed_path = f"{backup_path}.gz"
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            os.remove(backup_path)
            
            logger.info(f"SQLite backup created: {compressed_path}")
            return str(compressed_path)
            
        except Exception as e:
            logger.error(f"Failed to backup SQLite database: {e}")
            raise
    
    def restore_sqlite(self, backup_path: str, target_path: str) -> bool:
        """Restore SQLite database from backup"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Decompress backup if it's gzipped
            if backup_path.endswith('.gz'):
                temp_path = backup_path[:-3]
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = temp_path
            
            # Restore database
            shutil.copy2(backup_path, target_path)
            
            # Clean up temporary file
            if backup_path != target_path and os.path.exists(temp_path):
                os.remove(temp_path)
            
            logger.info(f"SQLite database restored to: {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore SQLite database: {e}")
            return False
    
    def backup_mysql(self, mysql_config: Dict[str, Any], backup_name: Optional[str] = None) -> str:
        """Backup MySQL database using mysqldump"""
        try:
            # Generate backup name if not provided
            if not backup_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"mysql_backup_{timestamp}.sql"
            
            backup_path = self.backup_dir / backup_name
            
            # Build mysqldump command
            cmd = [
                'mysqldump',
                f"--host={mysql_config['host']}",
                f"--user={mysql_config['user']}",
                f"--password={mysql_config['password']}",
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                '--add-drop-database',
                '--create-options',
                mysql_config['database']
            ]
            
            # Execute mysqldump
            import subprocess
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                raise Exception(f"mysqldump failed: {result.stderr}")
            
            # Compress backup
            compressed_path = f"{backup_path}.gz"
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            os.remove(backup_path)
            
            logger.info(f"MySQL backup created: {compressed_path}")
            return str(compressed_path)
            
        except Exception as e:
            logger.error(f"Failed to backup MySQL database: {e}")
            raise
    
    def restore_mysql(self, backup_path: str, mysql_config: Dict[str, Any]) -> bool:
        """Restore MySQL database from backup"""
        try:
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Decompress backup if it's gzipped
            if backup_path.endswith('.gz'):
                temp_path = backup_path[:-3]
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(temp_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path = temp_path
            
            # Build mysql command
            cmd = [
                'mysql',
                f"--host={mysql_config['host']}",
                f"--user={mysql_config['user']}",
                f"--password={mysql_config['password']}",
                mysql_config['database']
            ]
            
            # Execute mysql restore
            import subprocess
            with open(backup_path, 'r') as f:
                result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                raise Exception(f"MySQL restore failed: {result.stderr}")
            
            # Clean up temporary file
            if backup_path != temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            
            logger.info(f"MySQL database restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore MySQL database: {e}")
            return False
    
    def create_backup_archive(self, backup_files: List[str], archive_name: Optional[str] = None) -> str:
        """Create a tar.gz archive of backup files"""
        try:
            # Generate archive name if not provided
            if not archive_name:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archive_name = f"backup_archive_{timestamp}.tar.gz"
            
            archive_path = self.backup_dir / archive_name
            
            # Create tar.gz archive
            with tarfile.open(archive_path, 'w:gz') as tar:
                for backup_file in backup_files:
                    if os.path.exists(backup_file):
                        tar.add(backup_file, arcname=os.path.basename(backup_file))
            
            logger.info(f"Backup archive created: {archive_path}")
            return str(archive_path)
            
        except Exception as e:
            logger.error(f"Failed to create backup archive: {e}")
            raise
    
    def extract_backup_archive(self, archive_path: str, extract_dir: Optional[str] = None) -> List[str]:
        """Extract backup files from archive"""
        try:
            if not os.path.exists(archive_path):
                raise FileNotFoundError(f"Archive file not found: {archive_path}")
            
            # Set extract directory
            if not extract_dir:
                extract_dir = self.backup_dir / "extracted"
            
            Path(extract_dir).mkdir(exist_ok=True)
            
            # Extract archive
            extracted_files = []
            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(extract_dir)
                extracted_files = tar.getnames()
            
            logger.info(f"Backup archive extracted to: {extract_dir}")
            return [os.path.join(extract_dir, f) for f in extracted_files]
            
        except Exception as e:
            logger.error(f"Failed to extract backup archive: {e}")
            raise
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob('*'):
                if backup_file.is_file():
                    # Get file info
                    stat = backup_file.stat()
                    file_info = {
                        'name': backup_file.name,
                        'path': str(backup_file),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'type': self._get_backup_type(backup_file.name)
                    }
                    
                    # Filter by type if specified
                    if not backup_type or file_info['type'] == backup_type:
                        backups.append(file_info)
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def _get_backup_type(self, filename: str) -> str:
        """Determine backup type from filename"""
        if 'sqlite' in filename.lower():
            return 'sqlite'
        elif 'mysql' in filename.lower():
            return 'mysql'
        elif 'archive' in filename.lower():
            return 'archive'
        else:
            return 'unknown'
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> int:
        """Remove backups older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob('*'):
                if backup_file.is_file():
                    stat = backup_file.stat()
                    if datetime.fromtimestamp(stat.st_mtime) < cutoff_date:
                        os.remove(backup_file)
                        removed_count += 1
                        logger.info(f"Removed old backup: {backup_file.name}")
            
            logger.info(f"Cleaned up {removed_count} old backups")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0
    
    def verify_backup(self, backup_path: str, backup_type: str) -> bool:
        """Verify backup file integrity"""
        try:
            if not os.path.exists(backup_path):
                return False
            
            if backup_type == 'sqlite':
                return self._verify_sqlite_backup(backup_path)
            elif backup_type == 'mysql':
                return self._verify_mysql_backup(backup_path)
            elif backup_type == 'archive':
                return self._verify_archive_backup(backup_path)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify backup: {e}")
            return False
    
    def _verify_sqlite_backup(self, backup_path: str) -> bool:
        """Verify SQLite backup file"""
        try:
            # Decompress if needed
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open('/tmp/temp_verify.db', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                verify_path = '/tmp/temp_verify.db'
            else:
                verify_path = backup_path
            
            # Try to open database
            conn = sqlite3.connect(verify_path)
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            conn.close()
            
            # Clean up temp file
            if backup_path.endswith('.gz') and os.path.exists('/tmp/temp_verify.db'):
                os.remove('/tmp/temp_verify.db')
            
            return len(tables) > 0
            
        except Exception as e:
            logger.error(f"SQLite backup verification failed: {e}")
            return False
    
    def _verify_mysql_backup(self, backup_path: str) -> bool:
        """Verify MySQL backup file"""
        try:
            # Decompress if needed
            if backup_path.endswith('.gz'):
                with gzip.open(backup_path, 'rb') as f_in:
                    with open('/tmp/temp_verify.sql', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                verify_path = '/tmp/temp_verify.sql'
            else:
                verify_path = backup_path
            
            # Check file content
            with open(verify_path, 'r') as f:
                content = f.read()
            
            # Look for key MySQL backup indicators
            has_create_table = 'CREATE TABLE' in content
            has_insert = 'INSERT INTO' in content
            
            # Clean up temp file
            if backup_path.endswith('.gz') and os.path.exists('/tmp/temp_verify.sql'):
                os.remove('/tmp/temp_verify.sql')
            
            return has_create_table and has_insert
            
        except Exception as e:
            logger.error(f"MySQL backup verification failed: {e}")
            return False
    
    def _verify_archive_backup(self, backup_path: str) -> bool:
        """Verify archive backup file"""
        try:
            # Try to open archive
            with tarfile.open(backup_path, 'r:gz') as tar:
                members = tar.getmembers()
                return len(members) > 0
                
        except Exception as e:
            logger.error(f"Archive backup verification failed: {e}")
            return False
    
    def generate_backup_report(self) -> Dict[str, Any]:
        """Generate backup status report"""
        try:
            backups = self.list_backups()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'backup_directory': str(self.backup_dir),
                'total_backups': len(backups),
                'backup_types': {},
                'total_size': 0,
                'oldest_backup': None,
                'newest_backup': None,
                'backup_list': []
            }
            
            for backup in backups:
                # Count by type
                backup_type = backup['type']
                if backup_type not in report['backup_types']:
                    report['backup_types'][backup_type] = 0
                report['backup_types'][backup_type] += 1
                
                # Calculate total size
                report['total_size'] += backup['size']
                
                # Track oldest and newest
                if not report['oldest_backup'] or backup['modified'] < report['oldest_backup']:
                    report['oldest_backup'] = backup['modified'].isoformat()
                
                if not report['newest_backup'] or backup['modified'] > report['newest_backup']:
                    report['newest_backup'] = backup['modified'].isoformat()
                
                # Add to backup list
                report['backup_list'].append({
                    'name': backup['name'],
                    'type': backup['type'],
                    'size_mb': round(backup['size'] / (1024 * 1024), 2),
                    'modified': backup['modified'].isoformat()
                })
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate backup report: {e}")
            return {}

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Database Backup and Restore Tool')
    parser.add_argument('action', choices=['backup', 'restore', 'list', 'cleanup', 'verify', 'report'],
                       help='Action to perform')
    parser.add_argument('--type', choices=['sqlite', 'mysql', 'all'], default='all',
                       help='Type of backup to perform')
    parser.add_argument('--source', help='Source database path or MySQL config file')
    parser.add_argument('--target', help='Target path for restore')
    parser.add_argument('--days', type=int, default=30, help='Days to keep backups (for cleanup)')
    parser.add_argument('--config', default='backup_config.json', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            'backup_dir': 'backups',
            'sqlite_databases': ['profiling.db', 'value_estimates.db', 'recommendations.db'],
            'mysql_config': {
                'host': 'localhost',
                'user': 'bi_user',
                'password': 'bi_password',
                'database': 'bi_profiling'
            }
        }
    
    # Create backup/restore instance
    backup_tool = DatabaseBackupRestore(config)
    
    try:
        if args.action == 'backup':
            if args.type == 'sqlite' or args.type == 'all':
                for db_path in config.get('sqlite_databases', []):
                    if os.path.exists(db_path):
                        backup_tool.backup_sqlite(db_path)
            
            if args.type == 'mysql' or args.type == 'all':
                backup_tool.backup_mysql(config['mysql_config'])
            
            if args.type == 'all':
                # Create archive of all backups
                backups = backup_tool.list_backups()
                backup_files = [b['path'] for b in backups if b['type'] in ['sqlite', 'mysql']]
                if backup_files:
                    backup_tool.create_backup_archive(backup_files)
        
        elif args.action == 'restore':
            if not args.source:
                print("Error: --source required for restore action")
                return
            
            if args.type == 'sqlite':
                if not args.target:
                    args.target = 'profiling.db'
                backup_tool.restore_sqlite(args.source, args.target)
            
            elif args.type == 'mysql':
                backup_tool.restore_mysql(args.source, config['mysql_config'])
        
        elif args.action == 'list':
            backups = backup_tool.list_backups()
            print(f"\nFound {len(backups)} backups:")
            for backup in backups:
                print(f"  {backup['name']} ({backup['type']}) - {backup['size']} bytes - {backup['modified']}")
        
        elif args.action == 'cleanup':
            removed = backup_tool.cleanup_old_backups(args.days)
            print(f"Removed {removed} old backups")
        
        elif args.action == 'verify':
            if not args.source:
                print("Error: --source required for verify action")
                return
            
            backup_type = backup_tool._get_backup_type(args.source)
            is_valid = backup_tool.verify_backup(args.source, backup_type)
            print(f"Backup verification: {'PASSED' if is_valid else 'FAILED'}")
        
        elif args.action == 'report':
            report = backup_tool.generate_backup_report()
            print(json.dumps(report, indent=2))
    
    except Exception as e:
        logger.error(f"Action failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
