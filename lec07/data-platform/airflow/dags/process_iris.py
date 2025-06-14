from airflow import DAG
from datetime import timedelta
from datetime import datetime
import os
from dbt_operator import DbtOperator
from airflow.operators.python_operator import PythonOperator
from python_scripts.train_model import process_iris_data
from airflow.utils.email import send_email
from pendulum import timezone

# Get variables
ANALYTICS_DB = os.getenv('ANALYTICS_DB', 'analytics')
PROJECT_DIR = os.getenv('AIRFLOW_HOME')+"/dags/dbt/homework"
PROFILE = 'homework'
KYIV_TZ = timezone("Europe/Kiev")

def notify_success(context):
    subject = f"DAG {context['dag'].dag_id} succeeded"
    body = f"Task {context['task_instance'].task_id} in DAG {context['dag'].dag_id} completed successfully."
    send_email(to=["airflow@email.com"], subject=subject, html_content=body)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'process_iris',
    default_args=default_args,
    description='Run transformations on iris dataset and model training using dbt pipelines',
    schedule_interval='0 1 * * *', 
    start_date=datetime(2025, 4, 22, tzinfo=timezone("Europe/Kiev")),
    end_date=datetime(2025, 4, 25, tzinfo=timezone("Europe/Kiev")),  # in this config 3 days are processed due to timezone diffs between airflow default UTC & Kyiv time 
    catchup=True,
    tags=['dbt', 'custom', 'iris'],
    on_success_callback=notify_success,
)

env_vars = {
    'ANALYTICS_DB': ANALYTICS_DB,
    'DBT_PROFILE': PROFILE
}

dbt_vars = {
    'is_test': False,
    'data_date': '{{ ds }}', 
}

# Step 0: Verify all dbt deps are installed
dbt_deps = DbtOperator(
    task_id='dbt_deps',
    command='deps',
    profile=PROFILE,
    project_dir=PROJECT_DIR,
    env_vars=env_vars,
    dag=dag,
)

# Step 1: Run dbt run to execute models (iris dataset transformation)
dbt_run = DbtOperator(
    task_id='dbt_run',
    dag=dag,
    command='run',
    profile=PROFILE,
    project_dir=PROJECT_DIR,
    env_vars=env_vars,
    vars=dbt_vars,
)

# Step 2: Run dbt test to validate results
dbt_test = DbtOperator(
    task_id='dbt_test',
    dag=dag,
    command='test',
    profile=PROFILE,
    project_dir=PROJECT_DIR,
    fail_fast=True,
    env_vars=env_vars,
    vars=dbt_vars,
)

# Step 3: Run model training task
train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=process_iris_data,
    dag=dag,
)


dbt_deps >> dbt_run >> dbt_test >> train_model_task