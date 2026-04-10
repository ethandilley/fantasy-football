import duckdb

con = duckdb.connect("/workspace/test.db")

# Run your query
result = con.execute("""
SELECT * FROM (
    VALUES 
        ('ethan', 23, 185),
        ('austin', 30, 175)
) AS t(name, age, height);
""").fetchall()

print(result)
