```
Spark job. Taking dataset from Yellow Taxi,
processing and uploading to 
PostgreSQL 9.4.24 (Greenplum Database 6.17.1) using pyspark.
```

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as f
from pyspark.sql.types import *


def save_to_psql(host: str, port: int, db_name: str, username: str, password: str, df: DataFrame, table_name: str):
    df.write \
        .format("jdbc") \
        .option("url", f"jdbc:postgresql://{host}:{port}/{db_name}") \
        .option("dbtable", f"public.{table_name}") \
        .option("user", f"{username}") \
        .option("password", f"{password}") \
        .option("driver", 'org.postgresql.Driver') \
        .mode("overwrite") \
        .save()


spark = SparkSession.builder\
        .master("local[*]") \
        .config("spark.jars", "./jars/postgresql-9.4.1207.jar") \
        .appName('First spark job by rpuropuu') \
        .getOrCreate()

trips_schema = StructType([
    StructField('vendor_id', StringType(), True),
    StructField('tpep_pickup_datetime', TimestampType(), True),
    StructField('tpep_dropoff_datetime', TimestampType(), True),
    StructField('passenger_count', IntegerType(), True),
    StructField('trip_distance', DoubleType(), True),
    StructField('ratecode_id', IntegerType(), True),
    StructField('store_and_fwd_flag', StringType(), True),
    StructField('pulocation_id', IntegerType(), True),
    StructField('dolocation_id', IntegerType(), True),
    StructField('payment_type', IntegerType(), True),
    StructField('fare_amount', DoubleType(), True),
    StructField('extra', DoubleType(), True),
    StructField('mta_tax', DoubleType(), True),
    StructField('tip_amount', DoubleType(), True),
    StructField('tolls_amount', DoubleType(), True),
    StructField('improvement_surcharge', DoubleType(), True),
    StructField('total_amount', DoubleType(), True),
    StructField('congestion_surcharge', DoubleType()),
])

# pd_csv = pd.read_csv('https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2020-04.csv')
csv_file = './data/yellow_tripdata_2020-04.csv'
df = spark.read.csv(csv_file, header=True, schema=trips_schema)

datamart = df \
    .where(f.weekofyear(df['tpep_pickup_datetime']) > 13) \
    .groupBy(f.weekofyear(df['tpep_pickup_datetime']).alias('week_of_year'),
             df['payment_type']) \
    .agg(f.sum(df['total_amount']).alias('sum_amount'), f.avg(df['tip_amount']).alias("avg_tips")) \
    .select(f.col('week_of_year'),
            f.col('payment_type'),
            f.col('sum_amount'),
            f.col('avg_tips')) \
    .orderBy(f.col('week_of_year'))

final_datamart = datamart.withColumn('ratio_tips', (100 * datamart['avg_tips']) / datamart['sum_amount'])# .drop('avg_tips')

# final_datamart.show()

psql_host = 'your_host_name'
psql_port = your_port
psql_db = 'your_database'
psql_user = 'your_login'
psql_password = 'your_password'

save_to_psql(
    host=psql_host,
    port=psql_port,
    db_name=psql_db,
    username=psql_user,
    password=psql_password,
    df=final_datamart,
    table_name='derun_rpuropuu_dev'
)
