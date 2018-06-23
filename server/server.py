import tornado.ioloop
import tornado.web
import sqlite3
import os
import tornado.httpserver


class MainHandler(tornado.web.RequestHandler):
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


class ProgressHandler(MainHandler):
    def initialize(self):
        pass

    def post(self):
        sqlstr = "SELECT * FROM RunningSamples WHERE Stage < 9"
        # print(sqlstr)
        # self.cursor.execute(sqlstr)
        # self.db.commit()
        rows = "<BR><h2>Running computations</h2><table><tr><th>Normal</th><th>Tumor</th><th>Stage</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[1], row[2], row[3])
        # print(rows)
        self.set_header("Content-Type", "text/plain")
        _rws = {"results": rows}
        self.write(_rws)


class CreateRunningSampleHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("RunningSamples", json)
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
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = "UPDATE RunningSamples SET Stage = {} WHERE Normal = \"{}\" AND Tumor = \"{}\"".format(json['Stage'], json['Normal'], json['Tumor'])
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write("Updated row.")


class RemoveRunningSampleHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = "DELETE FROM RunningSamples WHERE Normal = {} AND Tumor = {}".format(json['Normal'], json['Tumor'])
        print(sqlstr)
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
        json = tornado.escape.json_decode(self.request.body)
        self.write(json["key1"])  # Specific Value - no key for all values


class RecordFinishedHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT Normal, Tumor, Stage FROM RunningSamples WHERE Stage = 9"
        rows = "<BR><h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>Normal</th><th>Tumor</th><th>Stage</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        self.set_header("Content-Type", "text/plain")
        _rws = {"results": rows}
        self.write(_rws)

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("FinishedSamples", json)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write("Inserted value.")


class SortHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT ID, ExitStatus FROM SamtoolsSort"
        rows = "<BR><h2>Samtools Sort Entries</h2>"
        rows = rows + "<table><tr><th>Sample</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1])
        # print(rows)sq
        self.set_header("Content-Type", "text/plain")
        _rws = {"results": rows}
        self.write(_rws)

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("SamtoolsSort", json)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class MpileupHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM MpileUp"
        rows = "<BR><h2>MpileUp Entries</h2>"
        rows = rows + "<table><tr><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        # print(rows)
        self.set_header("Content-Type", "text/plain")
        _rws = {"results": rows}
        self.write(_rws)

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("MpileUp", json)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class VarscanSomaticHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM VarscanSomatic"
        rows = "<BR><h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        # print(rows)
        self.set_header("Content-Type", "text/plain")
        _rws = {"results": rows}
        self.write(_rws)

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("VarscanSomatic", json)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class VarscanProcessSomaticSnpsHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM VarscanProcessSnps"
        rows = "<BR><h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2])
        # print(rows)
        self.set_header("Content-Type", "text/plain")
        _rws = {"results": rows}
        self.write(_rws)

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("VarscanProcessSnps", json)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


class VarscanProcessSomaticIndelsHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = "SELECT NormalID, TumorID, ExitStatus FROM VarscanProcessIndels"
        rows = "<BR><h2>Varscan Somatic Entries</h2>"
        rows = rows + "<table><tr><th>Index</th><th>NormalID</th><th>TumorID</th><th>ExitStatus</th></tr>"
        for row in self.cursor.execute(sqlstr):
            rows = rows + "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(row[0], row[1], row[2], row[3])
        # print(rows)
        self.set_header("Content-Type", "text/plain")
        _rws = {"results": rows}
        self.write(_rws)

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        sqlstr = self.construct_sql("VarscanProcessIndels", json)
        print(sqlstr)
        self.cursor.execute(sqlstr)
        self.db.commit()
        self.write(sqlstr)


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


if __name__ == "__main__":
    settings = {}
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()

    # app = make_app()
    # app.listen(80)
    # tornado.ioloop.IOLoop.current().start()
