from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, trim, to_date, row_number
from pyspark.sql.types import IntegerType, StringType
from pyspark.sql.window import Window

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

bronze_database = "bronze"
bronze_table = "customers"
silver_database = "silver"
silver_table = "customers"

bronze_table_full = f"`{bronze_database}`.`{bronze_table}`"
silver_table_full = f"`{silver_database}`.`{silver_table}`"

df = spark.read.table(bronze_table_full)

df = df.select(
    col("id").alias("client_id"),
    col("firstname").alias("first_name"),
    col("lastname").alias("last_name"),
    col("email").alias("email"),
    col("registrationdate").alias("registration_date_raw"),
    col("state").alias("state")
)

df = df.withColumn("registration_date", to_date("registration_date_raw", "yyyy-MM-d")) \
       .drop("registration_date_raw")


df = df.withColumn("client_id", col("client_id").cast(IntegerType())) \
       .withColumn("first_name", trim(col("first_name")).cast(StringType())) \
       .withColumn("last_name", trim(col("last_name")).cast(StringType())) \
       .withColumn("email", trim(col("email")).cast(StringType())) \
       .withColumn("state", trim(col("state")).cast(StringType()))

# filtering out irrelevant records
df_clean = df.filter(
    (col("client_id").isNotNull()) &
    (col("email").isNotNull()) & (trim(col("email")) != "") &
    (col("registration_date").isNotNull())
)

# dedup by client_id & registration date
w = Window.partitionBy("client_id").orderBy(col("registration_date").asc())
df_dedup = df_clean.withColumn("row_num", row_number().over(w)).filter(col("row_num") == 1).drop("row_num")

df_dedup.write.mode("overwrite") \
    .format("parquet") \
    .saveAsTable(silver_table_full)

print(f"Silver table `{silver_table_full}` updated. Rows written: {df_dedup.count()}")
