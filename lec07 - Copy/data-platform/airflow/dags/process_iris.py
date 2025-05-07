from airflow import DAG
from datetime import timedelta
from datetime import datetime
import os
from dbt_operator import DbtOperator
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator  

# Get environment variables
ANALYTICS_DB = os.getenv('ANALYTICS_DB', 'analytics')
PROJECT_DIR = os.getenv('AIRFLOW_HOME')+"/dags/dbt/my_dbt_project"
PROFILE = 'my_dbt_project'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': True,  # Notify on failure
    'email_on_retry': True,    # Notify on retry
    'email': ['a.bezkorovainyi@gmail.com'],  # Ensure this is correct
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
def run_training_task():
    from python_scripts.train_model import process_iris_data
    process_iris_data()

dag = DAG(
    'process_iris',
    default_args=default_args,
    description='Run transformations on iris dataset and model training using dbt pipelines',
    schedule_interval='0 1 * * *', 
    start_date=datetime(2025, 4, 22),
    end_date=datetime(2025, 4, 24),
    catchup=True,
    tags=['dbt', 'custom', 'iris'],
)

# Environment variable for dbt
env_vars = {
    'ANALYTICS_DB': ANALYTICS_DB,
    'DBT_PROFILE': PROFILE
}

# dbt variables (use execution date for dynamic parameterization)
dbt_vars = {
    'is_test': False,
    'data_date': '{{ ds }}',  # Airflow's execution date (ds)
}

# Step 1: Run dbt run to execute models
dbt_transform = DbtOperator(
    task_id='dbt_transform',
    dag=dag,
    command='run',
    profile=PROFILE,
    project_dir=PROJECT_DIR,
    models=['iris_processed'],
    env_vars=env_vars,
    vars=dbt_vars,
)

train_model = PythonOperator(
    task_id='train_model',
    python_callable=run_training_task,
    dag=dag,
)

# Step 3: Send email notification on success
send_email = EmailOperator(
    task_id='send_email',
    to='a.bezkorovainyi@gmail.com', 
    subject='Airflow DAG: process_iris execution success',
    html_content='<h3>Hi there! Your pipeline has been executed successfully!</h3>',
    dag=dag,
)

# Define the task dependencies
dbt_transform >> train_model >> send_email 
