import sqlite3
import argparse

parser = argparse.ArgumentParser(description='Recycling database.')
parser.add_argument(dest='database', help='Database name.')
parser.add_argument("--finished", "-f", action="store_true", help="Optionally purge the finished table.")
parser.add_argument("--all", "-a", action="store_true", help="Purge all databases including metrics tables.")
parser.add_argument("--only_finished", "-o", action="store_true", help="Only purge the finished database.")
args = parser.parse_args()


db = sqlite3.connect(args.database)
cursor = db.cursor()
if not args.only_finished:
    sqlstr = "DELETE FROM FinishedSamples"
    print("(deprecated) Deleting FinishedSamples...")
    cursor.execute(sqlstr)

    sqlstr = "DELETE FROM RunningSamples"
    print("(deprecated) Deleting RunningSamples...")
    cursor.execute(sqlstr)

if args.all:
    sqlstr = "DELETE FROM MpileUp"
    print("Deleting MpileUp...")
    cursor.execute(sqlstr)

    sqlstr = "DELETE FROM SamtoolsSort"
    print("Deleting SamtoolsSort...")
    cursor.execute(sqlstr)

    sqlstr = "DELETE FROM VarscanProcessIndels"
    print("Deleting VarscanProcessIndels...")
    cursor.execute(sqlstr)

    sqlstr = "DELETE FROM VarscanProcessSnps"
    print("Deleting VarscanProcessSnps...")
    cursor.execute(sqlstr)

    sqlstr = "DELETE FROM VarscanSomatic"
    print("Deleting VarscanSomatic...")
    cursor.execute(sqlstr)

if not args.only_finished:
    sqlstr = "DELETE FROM queued"
    print("Deleting queued...")
    cursor.execute(sqlstr)

    sqlstr = "DELETE FROM processing"
    print("Deleting processing...")
    cursor.execute(sqlstr)

if args.finished or args.only_finished:
    sqlstr = "DELETE FROM finished"
    print("Deleting queued...")
    cursor.execute(sqlstr)
else:
    print("Skipping finished table...")

sqlstr = "UPDATE sqlite_sequence SET seq = 0"
print("Resetting Indexes...")
cursor.execute(sqlstr)

db.commit()
db.close()

print ("FINISHED!")
