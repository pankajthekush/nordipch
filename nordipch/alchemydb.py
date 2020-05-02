
class Employee():
    def __init__(self,first,last,pay):
        self.first = first
        self.last = last
        self.pay = pay




import sqlite3
conn = sqlite3.connect('employee.db')
cur = conn.cursor()
# cur.execute("""CREATE TABLE employees(
#             first text,
#             last text,
#             sal integer
#             )""")


# cur.execute("""CREATE TABLE employees (
#             first text,
#             last text,
#             pay integer
#             )""")


def insert(emp):
    with conn:
        cur.execute("INSERT INTO employees VALUES(?,?,?)",(emp.first,emp.last,emp.pay))


e1 = Employee('joh','doe',100)
e2 = Employee('jak','june',100)



cur.execute("INSERT INTO employees VALUES(:first,:last,:pay)",{'first':e2.first,'last':e2.last,'pay':e2 .pay})
conn.commit()

cur.execute("SELECT * from employees")

print(cur.fetchall())

conn.commit()
conn.close()


