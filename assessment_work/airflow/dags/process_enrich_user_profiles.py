import boto3
import json
import traceback
from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from datetime import datetime, timedelta

redshift_workgroup_name = "ab-data-platform-workgroup"
DB_NAME = "dev"
S3_LOG_BUCKET = "ab-data-platform-airflow-752953535939" # S3 bucket for logs
POLL_INTERVAL = 10

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def get_sql_from_s3(bucket: str, key: str) -> str:
    """
    Fetches a SQL query from an S3 bucket.
    """
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    return obj['Body'].read().decode('utf-8')

def log_task_status_to_s3(context, status):
    """
    Logs the status of an Airflow task to an S3 bucket.
    Includes error details if the task failed.
    This function is reused from our previous successful DAG.
    """
    s3 = boto3.client("s3")

    dag_id = context['dag'].dag_id
    task_id = context['task'].task_id

    execution_date = context['execution_date'].isoformat()
    log_timestamp = datetime.now().isoformat()
    dag_run_id = context['dag_run'].run_id

    log_data = {
        "dag_id": dag_id,
        "task_id": task_id,
        "execution_date": execution_date,
        "timestamp": log_timestamp,
        "status": status,
        "dag_run_id": dag_run_id,
    }

    if status == "FAILED":
        exception = context.get('exception')
        log_data["error_message"] = str(exception) if exception else "No specific exception message found."
        log_data["full_traceback"] = traceback.format_exc() if exception else "No traceback available."

    s3_key = f"logs/{dag_id}/{task_id}/{execution_date}_{status}.json"

    try:
        s3.put_object(
            Bucket=S3_LOG_BUCKET,
            Key=s3_key,
            Body=json.dumps(log_data, indent=4).encode("utf-8"),
            ContentType="application/json"
        )
        print(f"Successfully logged task status '{status}' to S3: s3://{S3_LOG_BUCKET}/{s3_key}")
    except Exception as e:
        print(f"Error logging task status to S3: {e}")

with DAG(
    dag_id="enrich_user_profiles_dag",
    description="Enrich user profile data into gold from silver",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    max_active_runs=1,
    tags=["customers", "redshift"]
) as dag:

    sql_query = get_sql_from_s3(S3_LOG_BUCKET, "dags/sql/enrich_user_profiles.sql")

    enrich_task = RedshiftDataOperator(
        task_id="merge_into_gold_user_profiles",
        workgroup_name=redshift_workgroup_name,
        database=DB_NAME,
        sql=sql_query,
        poll_interval=POLL_INTERVAL,
        wait_for_completion=True,
        on_success_callback=lambda context: log_task_status_to_s3(context, "SUCCESS"),
        on_failure_callback=lambda context: log_task_status_to_s3(context, "FAILED"),
    )

