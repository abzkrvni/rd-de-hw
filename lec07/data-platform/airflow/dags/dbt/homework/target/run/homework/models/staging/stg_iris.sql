
  create view "analytics"."analytics"."stg_iris__dbt_tmp"
    
    
  as (
    with source as (
    select * from "analytics"."analytics"."iris_dataset"
)

select
    cast(sepal_length as numeric) as sepal_length,
    cast(sepal_width as numeric) as sepal_width,
    cast(petal_length as numeric) as petal_length,
    cast(petal_width as numeric) as petal_width,
    species
from source
  );