import pymysql

db = pymysql.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="ml",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True
)
