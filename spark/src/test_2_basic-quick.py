from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, broadcast

spark = SparkSession.builder \
    .appName("Level2_BasicTest") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.memory", "512m") \
    .config("spark.eventLog.enabled", "true") \
    .config("spark.eventLog.dir", "/opt/spark-events") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

data = [(i, f"user_{i % 100}", i % 10, float(i * 1.5))
        for i in range(1, 100_001)]
df = spark.createDataFrame(data, ["id", "user", "category", "amount"])

print("\n" + "="*60)
print(">>> OPEN http://localhost:4040 NOW")
print(">>> STAGE 1 starting — groupBy aggregation")
print("="*60 + "\n")

# Action 1 — triggers Stage 1
result = df.groupBy("category") \
    .agg(count("id").alias("count")) \
    .orderBy("category")
result.show()

print("\n>>> SLEEPING 60s — explore Stage 1 in the UI now")
print(">>> http://localhost:4040/stages/")

print("\n>>> STAGE 2 starting — simple count")
total = df.count()
print(f"Total: {total:,}")

print("\n>>> SLEEPING 60s — explore Stage 2 in the UI now")

print("\n>>> STAGE 3 starting — broadcast join")
customers = spark.createDataFrame(
    [(i, f"name_{i}") for i in range(100)], ["category", "label"]
)
joined = df.join(broadcast(customers), "category")
print(f"Joined rows: {joined.count():,}")

print("\n>>> SLEEPING 60s — explore Stage 3 (broadcast join) in the UI")

spark.stop()
print("Done.")