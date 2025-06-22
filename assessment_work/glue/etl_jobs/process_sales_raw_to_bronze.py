import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import boto3

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

bucket_name = "ab-data-platform-data-lake-752953535939"
raw_prefix = "raw/"
bronze_sales_path = f"s3://{bucket_name}/bronze/bronze_sales/" 

s3 = boto3.client("s3")
objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=raw_prefix)

csv_files = [f"s3://{bucket_name}/{obj['Key']}" 
             for obj in objects.get("Contents", []) 
             if obj["Key"].endswith(".csv")]

if not csv_files:
    print("No CSV files found in raw/")
    job.commit()
    sys.exit(0)

df_list = []
for path in csv_files:
    df = spark.read.option("header", "true").csv(path)
    for col_name in df.columns:
        df = df.withColumn(col_name, df[col_name].cast("string"))
    df_list.append(df)

final_df = df_list[0]
for df in df_list[1:]:
    final_df = final_df.unionByName(df, allowMissingColumns=True)

final_df.write.mode("overwrite").parquet(bronze_sales_path)

print("Data written to bronze/sales/")
job.commit()
