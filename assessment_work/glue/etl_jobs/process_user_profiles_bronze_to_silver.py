from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, trim
from pyspark.sql.types import IntegerType, StringType, DateType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

bronze_db = "bronze"
bronze_table = "user_profiles"
silver_db = "silver"
silver_table = "user_profiles"

bronze_table_full = f"`{bronze_db}`.`{bronze_table}`"
silver_table_full = f"`{silver_db}`.`{silver_table}`"

df = spark.read.table(bronze_table_full)

df_transformed = df.select(
    trim(col("email")).cast(StringType()).alias("email"),
    trim(col("full_name")).cast(StringType()).alias("full_name"),
    trim(col("state")).cast(StringType()).alias("state"),
    col("birth_date").cast(DateType()).alias("birth_date"),
    trim(col("phone_number")).cast(StringType()).alias("phone_number")
)

df_transformed.write.mode("overwrite").format("parquet").saveAsTable(silver_table_full)

print(f"Silver table `{silver_table_full}` created. Rows: {df_transformed.count()}")
