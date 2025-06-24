from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="process_user_profiles_dag",
    description="Pipeline to process user profile data: raw → bronze → silver",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=["user_profiles", "glue"]
) as dag:


    raw_to_bronze = GlueJobOperator(
        task_id="process_user_profiles_raw_to_bronze",
        job_name="process_user_profiles_raw_to_bronze",  
        script_location="s3://aws-glue-assets-752953535939-us-east-1/scripts/process_user_profiles_raw_to_bronze.py",
        region_name="us-east-1",
        iam_role_name="ab-data-platform-glue-service-role",
        create_job_kwargs={
            "GlueVersion": "5.0",
            "NumberOfWorkers": 10,
            "WorkerType": "G.1X",
        },
    )

    bronze_to_silver = GlueJobOperator(
        task_id="process_user_profiles_bronze_to_silver",
        job_name="process_user_profiles_bronze_to_silver",  
        script_location="s3://aws-glue-assets-752953535939-us-east-1/scripts/process_user_profiles_bronze_to_silver.py",
        region_name="us-east-1",
        iam_role_name="ab-data-platform-glue-service-role",
        create_job_kwargs={
            "GlueVersion": "5.0",
            "NumberOfWorkers": 10,
            "WorkerType": "G.1X",
        },
    )

    trigger_enrich_user_profiles = TriggerDagRunOperator(
        task_id="trigger_enrich_user_profiles_dag",
        trigger_dag_id="enrich_user_profiles_dag",
        wait_for_completion=False,
        reset_dag_run=True,
    )    


    raw_to_bronze >> bronze_to_silver >> trigger_enrich_user_profiles
