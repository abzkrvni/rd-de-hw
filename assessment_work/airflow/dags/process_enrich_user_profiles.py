from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="enrich_user_profiles_dag",
    description="Pipeline to enrich user profile data",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=["user_profiles", "glue"]
) as dag:


    gold_table_preparation_S3 = GlueJobOperator(
        task_id="process_enrich_user_profiles",
        job_name="process_enrich_user_profiles",  
        script_location="s3://aws-glue-assets-752953535939-us-east-1/scripts/process_enrich_user_profiles_to_gold.py",
        region_name="us-east-1",
        iam_role_name="ab-data-platform-glue-service-role",
        create_job_kwargs={
            "GlueVersion": "5.0",
            "NumberOfWorkers": 10,
            "WorkerType": "G.1X",
        },
    )

    