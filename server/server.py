from typing import Optional, Awaitable

import tornado.ioloop
import tornado.web
import sqlite3
import os
import tornado.httpserver
import json
from src.support.tcga import TCGAVariantCaller


class MainHandler(tornado.web.RequestHandler):
    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    # This is going to show the basic stats page
    def get(self):
        self.render("../index.html")

    def post(self):
        self.write("Hello post world")

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers",
                        "Access-Control-Allow-Headers, Origin, Accept, X-Requested-With, \
                        Content-Type, Access-Control-Request-Method, \
                        Access-Control-Request-Headers")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, POST, \
                        DELETE, OPTIONS')
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    @staticmethod
    def construct_sql(table_name, json_object):
        print("In the construct sql method...")
        print("Table name: {}".format(table_name))
        columns = ''
        values = ''
        for key, value in json_object.iteritems():
            columns = columns + '\"' + str(key) + '\", '
            values = values + '\"' + str(value) + '\", '
        c = columns[:-2]
        v = values[:-2]
        sqlstr = "INSERT INTO {} ({}) VALUES ({})".format(table_name, c, v)
        return sqlstr

    @property
    def db(self):
        return self.application.db

    @property
    def cursor(self):
        return self.application.cursor

    @property
    def batch_scriptor(self):
        return self.application.batch_scriptor

    @property
    def callers(self):
        return self.application.callers

    @property
    def table_style(self):
        return "<html><head><style>table {font-family: \"Trebuchet MS\", Arial, Helvetica, sans-serif;border-collapse: collapse;width: 100%;}table td, #customers th {border: 1px solid #ddd;padding: 8px;}table tr:nth-child(even){background-color: #f2f2f2;}table tr:hover {background-color: #ddd;}table th {padding-top: 12px;padding-bottom: 12px;text-align: left;background-color: #4CAF50;color: white;}</style></head>"


class ProgressHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT * FROM RunningSamples WHERE Stage < 9"
        rows = self.table_style
        rows = rows + "<body>"
        rows = rows + "<h2>Running computations</h2>"
        rows = rows + "<table><tr><th>Normal</th><th>Tumor</th><th>Stage</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[1], row[2], row[3])
        rows = rows + "</body></html>"
        self.set_header("Content-Type", "text/html")
        self.write(rows)

    def post(self):
        # Fetch the processing ones
        sqlstr = "SELECT tumor_barcode, tumor_file_size, normal_barcode, normal_file_size, cancer_type, tcga_id, stage  FROM processing"
        # TODO: move finished processing entries to finished here
        #       Should be some type of call when they get finished; maybe at the end of the computation
        #       the shell script should make a requests call.

        rows = "<h2>Running computations</h2><table><tr>" \
                      "<th>TCGA ID</th>" \
                      "<th>Cancer Type</th>" \
                      "<th>Tumor Barcode</th>" \
                      "<th>Tumor File Size</th>" \
                      "<th>Normal Barcode</th>" \
                      "<th>Normal File Size</th>" \
                      "<th>Stage</th>" \
                      "</tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{" \
                                        "}</td><td>{}</td></tr>".format(
                                        row[5], row[4], row[0], row[1],
                                        row[2], row[3], row[6])

        # Fetched the queued ones.
        queued_rows = "<h2>Queued computations</h2><table><tr>" \
                      "<th>TCGA ID</th>" \
                      "<th>Cancer Type</th>" \
                      "<th>Tumor Barcode</th>" \
                      "<th>Tumor File Size</th>" \
                      "<th>Normal Barcode</th>" \
                      "<th>Normal File Size</th>" \
                      "<th>Run</th>" \
                      "</tr>"
        sqlstr2 = "SELECT tumor_barcode, tumor_file_size, normal_barcode, normal_file_size, cancer_type, tcga_id FROM " \
                  "queued "
        for row in self.cursor.execute(sqlstr2):
            queued_rows = queued_rows + "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{" \
                                        "}</td><td><button type=\"button\" onclick=\"SubmitJob(\'{}\')\">+</button></td></tr>".format(
                                        row[5], row[4], row[0], row[1],
                                        row[2], row[3], row[5])

        sqlstr3 = "SELECT tumor_barcode, tumor_file_size, normal_barcode, normal_file_size, cancer_type, tcga_id, stage FROM finished"
        finished_rows = "<h2>Finished computations</h2><table><tr>" \
                      "<th>TCGA ID</th>" \
                      "<th>Cancer Type</th>" \
                      "<th>Tumor Barcode</th>" \
                      "<th>Tumor File Size</th>" \
                      "<th>Normal Barcode</th>" \
                      "<th>Normal File Size</th>" \
                      "<th>Stage</th>" \
                      "</tr>"
        for row in self.cursor.execute(sqlstr3):
            finished_rows = finished_rows + "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{" \
                                        "}</td><td>{}</td></tr>".format(
                                        row[5], row[4], row[0], row[1],
                                        row[2], row[3], row[6])
        self.set_header("Content-Type", "text/plain")
        _rws = {
            "processing": rows,
            "queued": queued_rows,
            "finished": finished_rows
        }
        self.write(_rws)


class RawDataHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        table = json_body["table"]
        print("TABLE: {}".format(table))
        self.cursor.execute("SELECT * FROM {}".format(table))
        r = [dict((self.cursor.description[i][0], value) \
                  for i, value in enumerate(row)) for row in self.cursor.fetchall()]
        self.set_header("Content-Type", "text/plain")
        print(r)
        json_mylist = json.dumps(r, separators=(',', ':'))
        self.write(json_mylist)


class CreateRunningSampleHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("RunningSamples", json_body)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write("Inserted row.")


class UpdateRunningSampleHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = "UPDATE RunningSamples SET Stage = {} WHERE Normal = \"{}\" AND Tumor = \"{}\"".format(
            json_body['Stage'], json_body['Normal'], json_body['Tumor'])
        # parrot the processing table too
        sqlstr2 = "UPDATE processing SET stage = {} WHERE normal_file = \"{}\" AND tumor_file = \"{}\"".format(
            json_body['Stage'], json_body['Normal'], json_body['Tumor'])
        self.cursor.execute(sqlstr2)
        # print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write("Updated row.")


class RemoveRunningSampleHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = "DELETE FROM RunningSamples WHERE Normal = {} AND Tumor = {}".format(json_body['Normal'],
                                                                                      json_body['Tumor'])
        sql_statement = """
                        INSERT INTO
                        finished
                        SELECT * FROM
                        processing
                        WHERE
                        normal_file = \'{}\' and tumor_file = \"{}\" 
                        """.format(json_body['Normal'], json_body['Tumor'])
        self.cursor.execute(sql_statement)

        sqlstr2 = "DELETE FROM processing WHERE normal_file = {} AND tumor_file = {}".format(json_body['Normal'],
                                                                                      json_body['Tumor'])
        self.cursor.execute(sqlstr2)
        # print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write("Deleted row.")


class TestHandler(MainHandler):
    # Example implementation
    def initialize(self):
        pass

    def get(self):
        self.write("Successful GET test!")

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        self.write(json_body["key1"])  # Specific Value - no key for all values


class RecordFinishedHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT Normal, Tumor, Stage FROM RunningSamples WHERE Stage = 9"
        rows = self.table_style
        rows = rows + "<body>"
        rows = rows + "<h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>Normal</th><th>Tumor</th><th>Stage</th></tr>"
        i = 0
        for row in self.cursor.execute(sqlstr):
            i = i + 1
            rows = rows + "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        rows = rows + "<br><br>Total Records: {}".format(i)
        rows = rows + "</body></html>"
        self.set_header("Content-Type", "text/html")
        self.write(rows)

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("FinishedSamples", json_body)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write("Inserted value.")


class SortHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT ID, ExitStatus FROM SamtoolsSort"
        rows = self.table_style
        rows = rows + "<body>"
        rows = rows + "<h2>Samtools Sort Entries</h2>"
        rows = rows + "<table><tr><th>Sample</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1])
        # print(rows)sq
        rows = rows + "</body></html>"
        self.set_header("Content-Type", "text/html")
        self.write(rows)

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("SamtoolsSort", json_body)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class MpileupHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM MpileUp"
        rows = self.table_style
        rows = rows + "<body>"
        rows = rows + "<h2>MpileUp Entries</h2>"
        rows = rows + "<table><tr><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        # print(rows)
        rows = rows + "</body></html>"
        self.set_header("Content-Type", "text/html")
        self.write(rows)

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("MpileUp", json_body)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class VarscanSomaticHandler(MainHandler):

    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM VarscanSomatic"
        rows = self.table_style
        rows = rows + "<body>"
        rows = rows + "<h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        # print(rows)
        rows = rows + "</body></html>"
        self.set_header("Content-Type", "text/html")
        self.write(rows)

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("VarscanSomatic", json_body)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class VarscanProcessSomaticSnpsHandler(MainHandler):

    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM VarscanProcessSnps"
        rows = self.table_style
        rows = rows + "<body>"
        rows = rows + "<h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        # print(rows)
        rows = rows + "</body></html>"
        self.set_header("Content-Type", "text/html")
        self.write(rows)

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("VarscanProcessSnps", json_body)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class VarscanProcessSomaticIndelsHandler(MainHandler):

    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM VarscanProcessIndels"
        rows = self.table_style
        rows = rows + "<body>"
        rows = rows + "<BR><h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>Index</th><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2], row[3])
        # print(rows)
        rows = rows + "</body></html>"
        self.set_header("Content-Type", "text/html")
        # _rws = {"results": rows}
        self.write(rows)

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("VarscanProcessIndels", json_body)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class SubmitJobHandler(MainHandler):
    def get(self):
        pass

    def post(self):
        json_body = tornado.escape.json_decode(self.request.body)
        print("Body: {}".format(json_body))
        print("Checking to see if {} is available to push to computations.".format(json_body['tcga_id']))
        try:
            if self.batch_scriptor.generate_sbatch_by_tcga_id(json_body['tcga_id']):
                # Remove this tcga ID entry from the query table, and put it into the processing one
                sql_statement = """
                                INSERT INTO
                                processing
                                SELECT * FROM
                                queued
                                WHERE
                                tcga_id = \'{}\'
                                """.format(json_body['tcga_id'])
                self.cursor.execute(sql_statement)
                sql_statement = """
                                DELETE FROM queued WHERE tcga_id = \'{}\'
                                """.format(json_body['tcga_id'])
                self.cursor.execute(sql_statement)
            else:
                print("Failed to submit the tcga ID job: {}".format(json_body['tcga_id']))
                self.write({"result": "failed"})

        except KeyError:
            print("There was no TCGA ID sent!")
            self.write({"result": "failed"})

        self.db.commit()
        self.write({"result": "ok"})


class Application(tornado.web.Application):
    def __init__(self):
        tornado_settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            'debug': True
        }

        handlers = [
            (r"/", MainHandler),
            (r"/progress/", ProgressHandler),
            (r"/samtoolssort/", SortHandler),
            (r"/mpileup/", MpileupHandler),
            (r"/varscansomatic/", VarscanSomaticHandler),
            (r"/varscanprocesssomaticsnps/", VarscanProcessSomaticSnpsHandler),
            (r"/varscanprocesssomaticindels/", VarscanProcessSomaticIndelsHandler),
            (r"/recordfinished/", RecordFinishedHandler),
            (r"/createrunningsample/", CreateRunningSampleHandler),
            (r"/updaterunningsample/", UpdateRunningSampleHandler),
            (r"/removerunningsample/", RemoveRunningSampleHandler),
            (r"/rawdata/", RawDataHandler),
            (r"/test/", TestHandler),
            (r"/js/(.*)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path'])),
            (r"/(styles\.css)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path'])),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path'])),
            (r"/img/(.*)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path']))
        ]

        tornado.web.Application.__init__(self, handlers, **tornado_settings)

        # self.db = database.Connection()
        self.db = sqlite3.connect('time_keep_database.db')
        self.cursor = self.db.cursor()


class ManagerApplication(tornado.web.Application):
    def __init__(self, callers, batch_scriptor):
        tornado_settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            'debug': True
        }

        handlers = [
            (r"/", MainHandler),
            (r"/progress/", ProgressHandler),
            (r"/submit_job/", SubmitJobHandler),
            (r"/samtoolssort/", SortHandler),
            (r"/mpileup/", MpileupHandler),
            (r"/varscansomatic/", VarscanSomaticHandler),
            (r"/varscanprocesssomaticsnps/", VarscanProcessSomaticSnpsHandler),
            (r"/varscanprocesssomaticindels/", VarscanProcessSomaticIndelsHandler),
            (r"/recordfinished/", RecordFinishedHandler),
            (r"/createrunningsample/", CreateRunningSampleHandler),
            (r"/updaterunningsample/", UpdateRunningSampleHandler),
            (r"/removerunningsample/", RemoveRunningSampleHandler),
            (r"/rawdata/", RawDataHandler),
            (r"/test/", TestHandler),
            (r"/js/(.*)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path'])),
            (r"/(styles\.css)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path'])),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path'])),
            (r"/img/(.*)", tornado.web.StaticFileHandler,
             dict(path=tornado_settings['static_path']))
        ]

        tornado.web.Application.__init__(self, handlers, **tornado_settings)

        # self.db = database.Connection()
        self.db = sqlite3.connect('time_keep_database.db')
        self.cursor = self.db.cursor()
        self.callers = callers
        self.batch_scriptor = batch_scriptor
        print(os.getcwd())
        print("Adding callers to database.")
        # Add callers to database
        for x, caller in enumerate(self.callers):
            print('Processing caller {}\r'.format(x), end="")
            statement = caller.add_to_db()
            # print(statement)
            self.cursor.execute(statement)

        self.db.commit()
        print("\n")
        print("Finished setting up database.")


if __name__ == "__main__":
    settings = {}
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()

    # app = make_app()
    # app.listen(80)
    # tornado.ioloop.IOLoop.current().start()
