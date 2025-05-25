from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'debug_dbt_connection',
    default_args=default_args,
    description='Debug dbt connection and environment from Airflow',
    schedule_interval=None,
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['debug', 'dbt'],
)

PROJECT_DIR = os.getenv('AIRFLOW_HOME') + "/dags/dbt/homework"
PROFILE_NAME = 'homework'

# Step 1: Print environment variables
print_env = BashOperator(
    task_id='print_env_vars',
    bash_command='env | grep -E "ETL|DB|POSTGRES|PROFILE"',
    dag=dag,
)

# Step 2: Show dbt version and profile info
dbt_info = BashOperator(
    task_id='dbt_info',
    bash_command=f"""
        dbt --version && \
        dbt debug --project-dir {PROJECT_DIR} --profile {PROFILE_NAME} --profiles-dir ~/.dbt
    """,
    dag=dag,
    env={
        'ANALYTICS_DB': os.getenv('ANALYTICS_DB', 'analytics'),
        'ETL_USER': os.getenv('ETL_USER'),
        'ETL_PASSWORD': os.getenv('ETL_PASSWORD'),
        'POSTGRES_ANALYTICS_HOST': os.getenv('POSTGRES_ANALYTICS_HOST'),
    },
)

print_env >> dbt_info
