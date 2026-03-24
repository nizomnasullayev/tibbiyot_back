import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:%236363Ali570@db.egpadgocxmcfjdpgrtce.supabase.co:5432/postgres?sslmode=require"
)

cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())

conn.close()