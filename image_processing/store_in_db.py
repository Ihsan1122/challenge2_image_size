import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from image_processing.load_and_resize import load_and_resize

def create_table_if_not_exists(conn):
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS images (
        depth INTEGER PRIMARY KEY,
        pixels BYTEA
    )
    ''')
    conn.commit()
    cur.close()

def store_in_db(csv_path, db_uri):
    conn = psycopg2.connect(db_uri)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
 
    create_table_if_not_exists(conn)
    
   
    df_resized = load_and_resize(csv_path)
    print('row---------------------')
    
    cur = conn.cursor()
    
    print(df_resized)
    for index, row in df_resized.iterrows():
        print('row---------------------')
        cur.execute(sql.SQL('''
        INSERT INTO images (depth, pixels) VALUES (%s, %s)
        '''), (row['depth'], psycopg2.Binary(row[1:].tobytes())))
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    csv_path = 'data.csv'  
    db_uri = "postgresql://apple@localhost/2"  
    store_in_db(csv_path, db_uri)
