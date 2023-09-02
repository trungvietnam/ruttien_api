import mysql.connector

cnx = mysql.connector.connect(user='trungdc', password='IXFagng!ig]rvEYa',
                              host='103.186.101.41',
                              database='momo_tool')
query = ("SELECT * from giaodich")

cursor = cnx.cursor()

cursor.execute(query)
# print(cursor)
myresult = cursor.fetchall()

for x in myresult:
  print(x)

cnx.close()

def 