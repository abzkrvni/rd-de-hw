from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

raw_database = "ab-data-platform_database"
raw_table = "customers"
bronze_database = "bronze"
bronze_table = "customers"

raw_table_full = f"`{raw_database}`.`{raw_table}`"
bronze_table_full = f"`{bronze_database}`.`{bronze_table}`"

raw_df = spark.read.table(raw_table_full)

for c in raw_df.columns:
    raw_df = raw_df.withColumn(c, col(c).cast("string"))

raw_df.write.mode("overwrite").format("parquet").saveAsTable(bronze_table_full)
