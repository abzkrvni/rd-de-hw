from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import col, to_date, lpad, trim, regexp_replace
from pyspark.sql.types import DecimalType, IntegerType, StringType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

bronze_database = "bronze"
bronze_table = "sales"
silver_database = "silver"
silver_table = "sales"

bronze_table_full = f"`{bronze_database}`.`{bronze_table}`"
silver_table_full = f"`{silver_database}`.`{silver_table}`"

df = spark.read.table(bronze_table_full)

df = df.select(
    col("CustomerId").alias("client_id"),
    col("PurchaseDate").alias("purchase_date_raw"),
    col("Product").alias("product_name"),
    col("Price").alias("price")
)

# date normalization
df = df.withColumn("purchase_date", to_date("purchase_date_raw", "yyyy-MM-d")) \
       .drop("purchase_date_raw")

# clean the values in price column    
df = df.withColumn("price_cleaned",
    regexp_replace(col("price"), "[$,\\s]", ""))
    
# filter out null client_id
df = df.filter((col("client_id").isNotNull()) & (trim(col("client_id")) != ""))

# apply schema
df = df.withColumn("client_id", col("client_id").cast(IntegerType())) \
       .withColumn("product_name", col("product_name").cast(StringType())) \
       .withColumn("price", col("price_cleaned").cast(DecimalType(10, 2))) \
       .drop("price_cleaned")
       
# filter out other irrelevant data
df_clean = df.filter(
    (col("client_id").isNotNull()) &
    (col("product_name").isNotNull()) & (trim(col("product_name")) != "") &
    (col("purchase_date").isNotNull()) &
    (col("price").isNotNull())
)

print(f"Clean rows count: {df_clean.count()}")

df_clean.write.mode("overwrite") \
    .format("parquet") \
    .option("partitionOverwriteMode", "dynamic") \
    .partitionBy("purchase_date") \
    .saveAsTable(silver_table_full)
