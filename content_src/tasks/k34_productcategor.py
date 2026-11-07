from kursad import inputs, SRC

ID = 'k34'
NAME = 'Product category enrichment'
LANG = "pyspark"
PARAMS = ['spark', 'order_items', 'products']
MINUTES = 10
ORDERED = False
TAGS = ['jointure', 'join', 'banque DE']
SOURCE = SRC + " · Q34"
IO = [("input", "DataFrame order_items, products")]
DESC = "<p>Add product <code>category</code> to each record in <code>order_items</code>, matching <code>product_id</code> against <code>products</code>. Preserve all original item columns and retain items without a matching product, using null for their category.</p><ul><li>Add category without replacing the item's sale-time unit price.</li><li>Perform the lookup on distributed data and retain items with absent or null product matches.</li></ul><p><b>Input DataFrames</b> (passed to <code>solve</code> with the same names):</p><ul><li><code>order_items</code>: <code>item_id</code>, <code>order_id</code>, <code>product_id</code>, <code>quantity</code>, <code>unit_price</code></li><li><code>products</code>: <code>product_id</code>, <code>sku</code>, <code>category</code>, <code>price</code></li></ul><p><b>Expected output:</b> A PySpark DataFrame with all order-item columns plus <code>category</code>. Item records remain present, and those without a matching product have null category.</p><h4>Example</h4>{{EXAMPLE}}"
STARTER = 'from pyspark.sql import SparkSession, DataFrame, functions as F\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark: SparkSession, order_items: DataFrame, products: DataFrame) -> DataFrame:\n    # write your code here\n    return order_items\n'
SOLUTION = "from pyspark.sql import functions as F, types as T\nfrom pyspark.sql.window import Window\n\n\ndef solve(spark, order_items, products):\n    result = order_items.join(products.select('product_id','category'),'product_id','left')\n    return result\n"


def tests():
    return inputs(['order_items', 'products'], ID)
