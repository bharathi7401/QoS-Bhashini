#!/usr/bin/env python3
"""
Database Migration Script: SQLite to MySQL
This script migrates the Business Intelligence system from SQLite to MySQL
"""

import sqlite3
import mysql.connector
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles migration from SQLite to MySQL"""
    
    def __init__(self, sqlite_path: str, mysql_config: Dict[str, Any]):
        self.sqlite_path = sqlite_path
        self.mysql_config = mysql_config
        self.sqlite_conn = None
        self.mysql_conn = None
        
    def connect_sqlite(self) -> bool:
        """Connect to SQLite database"""
        try:
            if not os.path.exists(self.sqlite_path):
                logger.error(f"SQLite database not found: {self.sqlite_path}")
                return False
                
            self.sqlite_conn = sqlite3.connect(self.sqlite_path)
            self.sqlite_conn.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.sqlite_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    def connect_mysql(self) -> bool:
        """Connect to MySQL database"""
        try:
            self.mysql_conn = mysql.connector.connect(**self.mysql_config)
            logger.info(f"Connected to MySQL database: {self.mysql_config['database']}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            return False
    
    def get_sqlite_tables(self) -> List[str]:
        """Get list of tables from SQLite database"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row['name'] for row in cursor.fetchall()]
            logger.info(f"Found {len(tables)} tables in SQLite: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Failed to get SQLite tables: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get table schema from SQLite"""
        try:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row['name'],
                    'type': row['type'],
                    'notnull': bool(row['notnull']),
                    'default': row['dflt_value'],
                    'pk': bool(row['pk'])
                })
            
            # Get sample data for type inference
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample_row = cursor.fetchone()
            
            return {
                'table_name': table_name,
                'columns': columns,
                'sample_row': sample_row
            }
        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            return {}
    
    def convert_sqlite_type_to_mysql(self, sqlite_type: str) -> str:
        """Convert SQLite data type to MySQL equivalent"""
        sqlite_type = sqlite_type.upper()
        
        type_mapping = {
            'INTEGER': 'INT',
            'INT': 'INT',
            'BIGINT': 'BIGINT',
            'REAL': 'DOUBLE',
            'FLOAT': 'FLOAT',
            'DOUBLE': 'DOUBLE',
            'TEXT': 'TEXT',
            'VARCHAR': 'VARCHAR(255)',
            'CHAR': 'CHAR(1)',
            'BLOB': 'LONGBLOB',
            'BOOLEAN': 'BOOLEAN',
            'DATETIME': 'DATETIME',
            'TIMESTAMP': 'TIMESTAMP',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'DECIMAL': 'DECIMAL(15,4)',
            'NUMERIC': 'DECIMAL(15,4)'
        }
        
        # Handle specific cases
        if 'VARCHAR' in sqlite_type:
            return sqlite_type
        elif 'CHAR' in sqlite_type:
            return sqlite_type
        elif 'DECIMAL' in sqlite_type:
            return sqlite_type
        elif 'NUMERIC' in sqlite_type:
            return sqlite_type
        
        return type_mapping.get(sqlite_type, 'TEXT')
    
    def create_mysql_table(self, schema: Dict[str, Any]) -> bool:
        """Create MySQL table based on SQLite schema"""
        try:
            table_name = schema['table_name']
            columns = schema['columns']
            
            # Build CREATE TABLE statement
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
            
            column_definitions = []
            primary_keys = []
            
            for column in columns:
                col_name = column['name']
                col_type = self.convert_sqlite_type_to_mysql(column['type'])
                col_notnull = "NOT NULL" if column['notnull'] else "NULL"
                col_default = ""
                
                if column['default'] is not None:
                    if isinstance(column['default'], str):
                        col_default = f"DEFAULT '{column['default']}'"
                    else:
                        col_default = f"DEFAULT {column['default']}"
                
                col_def = f"    {col_name} {col_type} {col_notnull} {col_default}".strip()
                column_definitions.append(col_def)
                
                if column['pk']:
                    primary_keys.append(col_name)
            
            # Add primary key constraint
            if primary_keys:
                column_definitions.append(f"    PRIMARY KEY ({', '.join(primary_keys)})")
            
            create_sql += ",\n".join(column_definitions)
            create_sql += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
            
            # Execute CREATE TABLE
            cursor = self.mysql_conn.cursor()
            cursor.execute(create_sql)
            self.mysql_conn.commit()
            
            logger.info(f"Created MySQL table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create MySQL table {schema['table_name']}: {e}")
            return False
    
    def migrate_table_data(self, table_name: str) -> bool:
        """Migrate data from SQLite table to MySQL"""
        try:
            # Get data from SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                logger.info(f"No data to migrate for table: {table_name}")
                return True
            
            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]
            placeholders = ', '.join(['%s'] * len(columns))
            
            # Prepare INSERT statement
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Migrate data
            mysql_cursor = self.mysql_conn.cursor()
            migrated_count = 0
            
            for row in rows:
                try:
                    # Convert row to list of values
                    values = list(row)
                    
                    # Handle special data types
                    for i, value in enumerate(values):
                        if isinstance(value, str) and value.startswith('[') and value.endswith(']'):
                            # JSON array - keep as is for MySQL
                            pass
                        elif value == '':
                            # Empty string to NULL for numeric fields
                            values[i] = None
                    
                    mysql_cursor.execute(insert_sql, values)
                    migrated_count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate row in {table_name}: {e}")
                    continue
            
            self.mysql_conn.commit()
            logger.info(f"Migrated {migrated_count} rows from {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate data for table {table_name}: {e}")
            return False
    
    def create_mysql_indexes(self, table_name: str) -> bool:
        """Create indexes for MySQL table"""
        try:
            # Get indexes from SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = sqlite_cursor.fetchall()
            
            mysql_cursor = self.mysql_conn.cursor()
            
            for index_info in indexes:
                index_name = index_info['name']
                
                # Skip primary key indexes
                if index_name.startswith('sqlite_autoindex_'):
                    continue
                
                # Get index columns
                sqlite_cursor.execute(f"PRAGMA index_info({index_name})")
                index_columns = sqlite_cursor.fetchall()
                
                if index_columns:
                    column_names = [col['name'] for col in sorted(index_columns, key=lambda x: x['cid'])]
                    
                    # Create index
                    create_index_sql = f"CREATE INDEX {index_name} ON {table_name} ({', '.join(column_names)})"
                    
                    try:
                        mysql_cursor.execute(create_index_sql)
                        logger.info(f"Created index {index_name} on {table_name}")
                    except Exception as e:
                        logger.warning(f"Failed to create index {index_name}: {e}")
            
            self.mysql_conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create indexes for table {table_name}: {e}")
            return False
    
    def migrate_views(self) -> bool:
        """Migrate SQLite views to MySQL"""
        try:
            # Get views from SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view'")
            views = sqlite_cursor.fetchall()
            
            if not views:
                logger.info("No views to migrate")
                return True
            
            mysql_cursor = self.mysql_conn.cursor()
            
            for view in views:
                view_name = view['name']
                view_sql = view['sql']
                
                # Convert SQLite-specific syntax to MySQL
                mysql_view_sql = self.convert_view_sql_to_mysql(view_sql)
                
                try:
                    # Drop view if exists
                    mysql_cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                    
                    # Create view
                    mysql_cursor.execute(mysql_view_sql)
                    logger.info(f"Created view: {view_name}")
                    
                except Exception as e:
                    logger.warning(f"Failed to create view {view_name}: {e}")
            
            self.mysql_conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate views: {e}")
            return False
    
    def convert_view_sql_to_mysql(self, sqlite_sql: str) -> str:
        """Convert SQLite view SQL to MySQL syntax"""
        # Basic conversions
        mysql_sql = sqlite_sql
        
        # Replace SQLite-specific functions
        replacements = {
            'datetime(\'now\')': 'NOW()',
            'date(\'now\')': 'CURDATE()',
            'time(\'now\')': 'CURTIME()',
            'strftime(\'%Y-%m-%d\', \'now\')': 'DATE(NOW())',
            'strftime(\'%H:%M:%S\', \'now\')': 'TIME(NOW())'
        }
        
        for old, new in replacements.items():
            mysql_sql = mysql_sql.replace(old, new)
        
        return mysql_sql
    
    def migrate_stored_procedures(self) -> bool:
        """Migrate SQLite stored procedures to MySQL"""
        try:
            # Note: SQLite doesn't have stored procedures like MySQL
            # This is a placeholder for future implementation
            logger.info("Stored procedures migration not implemented (SQLite doesn't support them)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate stored procedures: {e}")
            return False
    
    def migrate_triggers(self) -> bool:
        """Migrate SQLite triggers to MySQL"""
        try:
            # Get triggers from SQLite
            sqlite_cursor = self.sqlite_conn.cursor()
            sqlite_cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
            triggers = sqlite_cursor.fetchall()
            
            if not triggers:
                logger.info("No triggers to migrate")
                return True
            
            mysql_cursor = self.mysql_conn.cursor()
            
            for trigger in triggers:
                trigger_name = trigger['name']
                trigger_sql = trigger['sql']
                
                # Convert SQLite trigger syntax to MySQL
                mysql_trigger_sql = self.convert_trigger_sql_to_mysql(trigger_sql)
                
                try:
                    # Drop trigger if exists
                    mysql_cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                    
                    # Create trigger
                    mysql_cursor.execute(mysql_trigger_sql)
                    logger.info(f"Created trigger: {trigger_name}")
                    
                except Exception as e:
                    logger.warning(f"Failed to create trigger {trigger_name}: {e}")
            
            self.mysql_conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate triggers: {e}")
            return False
    
    def convert_trigger_sql_to_mysql(self, sqlite_sql: str) -> str:
        """Convert SQLite trigger SQL to MySQL syntax"""
        # Basic conversions
        mysql_sql = sqlite_sql
        
        # Replace SQLite-specific syntax
        replacements = {
            'NEW.': 'NEW.',
            'OLD.': 'OLD.',
            'BEGIN': 'BEGIN',
            'END': 'END'
        }
        
        # Note: This is a simplified conversion
        # Complex triggers may need manual review
        return mysql_sql
    
    def run_migration(self) -> bool:
        """Run the complete migration process"""
        try:
            logger.info("Starting SQLite to MySQL migration...")
            
            # Connect to databases
            if not self.connect_sqlite():
                return False
            
            if not self.connect_mysql():
                return False
            
            # Get tables to migrate
            tables = self.get_sqlite_tables()
            if not tables:
                logger.error("No tables found to migrate")
                return False
            
            # Migrate each table
            for table_name in tables:
                logger.info(f"Migrating table: {table_name}")
                
                # Get table schema
                schema = self.get_table_schema(table_name)
                if not schema:
                    continue
                
                # Create MySQL table
                if not self.create_mysql_table(schema):
                    continue
                
                # Migrate data
                if not self.migrate_table_data(table_name):
                    continue
                
                # Create indexes
                if not self.create_mysql_indexes(table_name):
                    continue
                
                logger.info(f"Successfully migrated table: {table_name}")
            
            # Migrate views
            self.migrate_views()
            
            # Migrate triggers
            self.migrate_triggers()
            
            # Migrate stored procedures
            self.migrate_stored_procedures()
            
            logger.info("Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        
        finally:
            # Clean up connections
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.mysql_conn:
                self.mysql_conn.close()
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate a migration report"""
        try:
            report = {
                'migration_date': datetime.now().isoformat(),
                'source_database': self.sqlite_path,
                'target_database': self.mysql_config['database'],
                'tables_migrated': [],
                'errors': [],
                'warnings': []
            }
            
            # Get migration status for each table
            tables = self.get_sqlite_tables()
            for table_name in tables:
                try:
                    # Check if table exists in MySQL
                    mysql_cursor = self.mysql_conn.cursor()
                    mysql_cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                    mysql_exists = mysql_cursor.fetchone() is not None
                    
                    # Check row counts
                    sqlite_cursor = self.sqlite_conn.cursor()
                    sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    sqlite_count = sqlite_cursor.fetchone()[0]
                    
                    mysql_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    mysql_count = mysql_cursor.fetchone()[0]
                    
                    report['tables_migrated'].append({
                        'table_name': table_name,
                        'sqlite_row_count': sqlite_count,
                        'mysql_row_count': mysql_count,
                        'migration_successful': mysql_exists and mysql_count == sqlite_count
                    })
                    
                except Exception as e:
                    report['errors'].append(f"Error checking table {table_name}: {e}")
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate migration report: {e}")
            return {}

def main():
    """Main migration function"""
    # Configuration
    sqlite_path = "profiling.db"  # Path to SQLite database
    mysql_config = {
        'host': 'localhost',
        'user': 'bi_user',
        'password': 'bi_password',
        'database': 'bi_profiling',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    # Check if SQLite database exists
    if not os.path.exists(sqlite_path):
        logger.error(f"SQLite database not found: {sqlite_path}")
        logger.info("Please ensure the SQLite database exists before running migration")
        return
    
    # Create migrator and run migration
    migrator = DatabaseMigrator(sqlite_path, mysql_config)
    
    if migrator.run_migration():
        # Generate and save migration report
        report = migrator.generate_migration_report()
        
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Migration report saved to: {report_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("MIGRATION SUMMARY")
        print("="*50)
        print(f"Source: {sqlite_path}")
        print(f"Target: {mysql_config['database']}")
        print(f"Tables migrated: {len(report.get('tables_migrated', []))}")
        print(f"Errors: {len(report.get('errors', []))}")
        print(f"Warnings: {len(report.get('warnings', []))}")
        print("="*50)
        
    else:
        logger.error("Migration failed!")
        exit(1)

if __name__ == "__main__":
    main()
