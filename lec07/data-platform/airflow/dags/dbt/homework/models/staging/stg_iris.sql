with source as (
    select * from {{ source('analytics', 'iris_dataset') }}
)

select
    cast(sepal_length as numeric) as sepal_length,
    cast(sepal_width as numeric) as sepal_width,
    cast(petal_length as numeric) as petal_length,
    cast(petal_width as numeric) as petal_width,
    species
from source