from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

raw_database = "ab-data-platform_database" 
raw_table = "user_profiles"
bronze_database = "bronze"
bronze_table = "user_profiles"

raw_table_full = f"`{raw_database}`.`{raw_table}`"
bronze_table_full = f"`{bronze_database}`.`{bronze_table}`"

df_raw = spark.read.table(raw_table_full)

for c in df_raw.columns:
    df_raw = df_raw.withColumn(c, col(c).cast("string"))

df_raw.write.mode("overwrite").format("parquet").saveAsTable(bronze_table_full)

print(f"Bronze table `{bronze_table_full}` created. Rows: {df_raw.count()}")
