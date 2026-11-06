from kit import table, tables, rng, ts

ID = "h13t3"
NAME = "Golden Customer Record"
LANG = "sql"
MINUTES = 25
TAGS = ["dernière valeur non nulle", "array_agg FILTER", "NULL vs chaîne vide", "nettoyage", "regexp_replace"]
DESC = """
<p>The table <b>customer_updates</b> has the columns <code>update_id</code>, <code>customer_id</code>, <code>updated_at</code> (timestamp), <code>email</code>, <code>phone</code> and <code>city</code>. Each row is a <b>partial</b> update sent by one of our apps:</p>
<ul><li>a field that is <code>NULL</code> means <i>not changed</i> by this update;</li>
<li>a field that is not <code>NULL</code> replaces the previous value, even when it is an empty or blank string: that means the value was <b>cleared</b>.</li></ul>
<p>Updates are applied in order of <code>updated_at</code>, then <code>update_id</code>. The current value of a field is therefore the latest non-<code>NULL</code> value sent for it, then cleaned:</p>
<ul><li><code>email</code>: trimmed and lower case;</li>
<li><code>phone</code>: digits only (every other character removed);</li>
<li><code>city</code>: trimmed, with the first letter of each word in upper case and the others in lower case (<code>INITCAP</code>).</li></ul>
<p>A value that is empty after cleaning is <code>NULL</code> in the result (cleared). A field never sent is <code>NULL</code> too.</p>
<p>Your task is to return one row per customer with the columns <code>customer_id</code>, <code>email</code>, <code>phone</code>, <code>city</code>, <code>last_update</code> (the latest <code>updated_at</code>) and <code>updates</code> (number of rows), sorted by <code>customer_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT customer_id,
  NULLIF(LOWER(TRIM((array_agg(email ORDER BY updated_at DESC, update_id DESC) FILTER (WHERE email IS NOT NULL))[1])), '') AS email,
  NULLIF(regexp_replace((array_agg(phone ORDER BY updated_at DESC, update_id DESC) FILTER (WHERE phone IS NOT NULL))[1], '[^0-9]', '', 'g'), '') AS phone,
  NULLIF(INITCAP(TRIM((array_agg(city ORDER BY updated_at DESC, update_id DESC) FILTER (WHERE city IS NOT NULL))[1])), '') AS city,
  MAX(updated_at) AS last_update,
  COUNT(*) AS updates
FROM customer_updates
GROUP BY customer_id
ORDER BY customer_id;
"""
MUTANTS = [
    SOLUTION.replace("FILTER (WHERE email IS NOT NULL)", "FILTER (WHERE TRIM(email) <> '')"),
    SOLUTION.replace("(array_agg(city ORDER BY updated_at DESC, update_id DESC) FILTER (WHERE city IS NOT NULL))[1]", "(array_agg(city ORDER BY updated_at DESC, update_id DESC))[1]"),
    SOLUTION.replace("ORDER BY updated_at DESC, update_id DESC) FILTER (WHERE phone", "ORDER BY updated_at, update_id) FILTER (WHERE phone"),
    SOLUTION.replace("NULLIF(LOWER(TRIM(", "LOWER(TRIM(").replace("[1])), '') AS email", "[1])) AS email"),
]
T = "update_id INT, customer_id INT, updated_at TIMESTAMP, email TEXT, phone TEXT, city TEXT"


def tests():
    t = [tables(customer_updates=table(T, [
        [1, 10, ts(0), " Amina@Mail.COM ", "+212 6-12-34", "casablanca"], [2, 10, ts(60), None, None, "  rabat "],
        [3, 10, ts(120), "", None, None], [4, 11, ts(0), "k@x.io", None, None], [6, 11, ts(30), None, "06 00", None],
        [5, 11, ts(30), None, "07 11", "EL JADIDA"], [7, 12, ts(10), None, None, None]])),
         tables(customer_updates=table(T, [[1, 1, ts(0), "a@b.c", "1", "fès"], [2, 1, ts(5), "   ", "n/a", None], [3, 1, ts(9), None, None, "  "]]))]
    r = rng(4133)
    emails = ["Ali@Mail.com", " sara@x.ma", "", "  ", "omar@y.org "]
    phones = ["+212 600-000", "06 11 22", "", "n/a", "0700"]
    cities = ["casablanca", " RABAT", "el jadida ", "", "   "]
    for _ in range(8):
        rows = []
        for i in range(r.randint(4, 20)):
            rows.append([i + 1, r.randint(1, 4), ts(r.choice([0, 10, 10, 20, 50, 90])),
                         r.choice(emails + [None] * 4), r.choice(phones + [None] * 4), r.choice(cities + [None] * 4)])
        r.shuffle(rows)
        t.append(tables(customer_updates=table(T, rows)))
    return t
