import pymysql

try:
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="seecs@123",
        database="project"
    )

    print("✅ Connected to PROJECT database!")

    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        print("Connected to:", cursor.fetchone())

    connection.close()

except Exception as e:
    print("❌ Connection failed")
    print(e)
