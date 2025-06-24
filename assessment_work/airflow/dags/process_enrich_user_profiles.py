from airflow import DAG
from airflow.providers.amazon.aws.operators.redshift_sql import RedshiftSQLOperator
from datetime import datetime, timedelta
from pathlib import Path

default_args = {
    "owner": "data-team",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

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

    merge_sql_path = Path(__file__).parent / "sql" / "enrich_user_profiles.sql"

    enrich_task = RedshiftSQLOperator(
        task_id="merge_into_gold_user_profiles",
        sql=str(merge_sql_path),
        redshift_conn_id="redshift_conn_id",
    )
    
    enrich_task
