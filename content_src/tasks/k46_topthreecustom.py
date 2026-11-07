from kursad import inputs, SRC

ID = 'k46'
NAME = 'Top three customers'
LANG = "pyspark"
PARAMS = ['spark', 'customers', 'orders']
MINUTES = 12
ORDERED = False
TAGS = ['window', 'row_number', 'lag', 'banque DE']
SOURCE = SRC + " · Q46"
IO = [("input", "DataFrame customers, orders")]
DESC = '<p>Calculate total spend across all order statuses for each customer using <code>orders</code> and <code>customers</code>, assigning zero to customers without matching orders. Within each segment, rank by spend descending and customer ID ascending to break ties. Return up to three customers per segment with all customer columns, <code>spend</code>, and their sequential rank <code>rn</code>.</p><ul><li>Apply the three-customer limit independently within each segment, retaining smaller groups in full.</li><li>Calculate spend and segment ranking on distributed data; zero-spend customers remain eligible.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>customers</code>: <code>customer_id</code>, <code>name</code>, <code>email</code>, <code>segment</code>, <code>country</code>, <code>signup_date</code></li><li><code>orders</code>: <code>order_id</code>, <code>customer_id</code>, <code>order_date</code>, <code>status</code>, <code>amount</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all customer columns plus <code>spend</code> and sequential <code>rn</code>, containing up to three customers per segment. Rank starts at 1 within each segment, using spend descending and customer ID ascending, including at the cutoff; no global order is required.</p><h4>Example</h4>{{EXAMPLE}}'
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, customers: DataFrame, orders: DataFrame) -> DataFrame:\n    # write your code here\n    return customers\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, customers, orders):\n    spend=orders.groupBy('customer_id').agg(F.sum('amount').alias('spend'))\n    x=customers.join(spend,'customer_id','left').fillna({'spend':0})\n    w=Window.partitionBy('segment').orderBy(F.desc('spend'),F.asc('customer_id'))\n    result=x.withColumn('rn',F.row_number().over(w)).filter('rn <= 3')\n    return result\n"


def tests():
    return inputs(['customers', 'orders'], ID)
