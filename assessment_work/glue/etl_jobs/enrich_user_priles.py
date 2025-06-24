from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import coalesce, col, trim, split, when
from pyspark.sql.types import StringType

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

silver_db = "silver"
customers_table = "customers"
user_profiles_table = "user_profiles"


gold_s3_path = "s3://ab-data-platform-data-lake-752953535939/gold/user_profiles_enriched/"

customers_df = spark.read.table(f"`{silver_db}`.`{customers_table}`")
user_profiles_df = spark.read.table(f"`{silver_db}`.`{user_profiles_table}`")

customers_df = customers_df.select(
    col("client_id"),
    trim(col("first_name")).alias("first_name"),
    trim(col("last_name")).alias("last_name"),
    trim(col("email")).alias("email"),
    trim(col("state")).alias("state"),
    col("registration_date")
)

user_profiles_df = user_profiles_df.select(
    col("email").alias("profile_email"),
    trim(col("full_name")).alias("full_name"),
    trim(col("state")).alias("profile_state"),
    col("birth_date"),
    trim(col("phone_number")).alias("phone_number")
)

joined_df = customers_df.join(
    user_profiles_df,
    customers_df.email == user_profiles_df.profile_email,
    "left"
)

name_split = split(col("full_name"), " ")

joined_df = joined_df.withColumn(
    "profile_first_name",
    when(col("full_name").isNotNull(), name_split.getItem(0)).otherwise(None)
).withColumn(
    "profile_last_name",
    when(col("full_name").isNotNull(), name_split.getItem(1)).otherwise(None)
)

enriched_df = joined_df.select(
    col("client_id"),
    col("email"),
    coalesce(col("first_name"), col("profile_first_name")).alias("first_name"),
    coalesce(col("last_name"), col("profile_last_name")).alias("last_name"),
    coalesce(col("state"), col("profile_state")).alias("state"),
    col("registration_date"),
    col("birth_date"),
    col("phone_number")
)


enriched_df.write \
    .mode("overwrite") \
    .format("parquet") \
    .option("path", gold_s3_path) \
    .saveAsTable("gold.user_profiles_enriched")

print(f"Enriched user profiles written to {gold_s3_path}. Rows: {enriched_df.count()}")
