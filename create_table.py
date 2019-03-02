import sqlite3

path="C://projects//video_stream//guest.sqlite"
def sqlite_entry(path,name):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    q="INSERT INTO users(id,name) VALUES (NULL,"+'"'+name+'")'
    print(q)
    c.execute(q)
    conn.commit()
    conn.close()

def sqlite_get(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    q = "SELECT * FROM users WHERE id=(SELECT MAX(id) FROM users)"
    c.execute(q)
    list=c.fetchone()
    id=list[0]
    name=list[1]
    conn.close()
    print(name)
    print(id)

sqlite_entry(path,"Anta")
