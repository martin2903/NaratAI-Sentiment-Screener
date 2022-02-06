import db_operations.db_updates
import time

if __name__ =="__main__":
    print("STARTING UPDATE")
    t0 = time.time()
    connection, cursor = db_operations.db_updates.connect_to_db()
    db_operations.db_updates.update_db(connection, cursor)
    cursor.close()
    connection.close()
    t1 = time.time() - t0
    print("FINISHED, IT TOOK {} minutes".format(t1 / 60))


