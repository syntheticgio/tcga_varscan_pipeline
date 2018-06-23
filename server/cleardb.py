import sqlite3
import argparse

parser = argparse.ArgumentParser(description='Recycling database.')
parser.add_argument(dest='database', help='Database name.')

args = parser.parse_args()


db = sqlite3.connect(args.database)
cursor = db.cursor()

sqlstr = "DELETE FROM FinishedSamples"
print("Deleting FinishedSamples...")
cursor.execute(sqlstr)

sqlstr = "DELETE FROM MpileUp"
print("Deleting MpileUp...")
cursor.execute(sqlstr)

sqlstr = "DELETE FROM RunningSamples"
print("Deleting RunningSamples...")
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

sqlstr = "UPDATE sqlite_sequence SET seq = 0"
print("Resetting Indexes...")
cursor.execute(sqlstr)

db.commit()
db.close()

print ("FINISHED!")
