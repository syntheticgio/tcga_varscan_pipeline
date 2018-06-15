import tornado.ioloop
import tornado.web
import sqlite3
import database


class MainHandler(tornado.web.RequestHandler):
    # This is going to show the basic stats page
    def get(self):
        self.write("Hello, world")

    def post(self):
        self.write("Hello post world")

    @property
    def db(self):
        return self.application.db


class TestHandler(MainHandler):
    # Example implementation
    def initialize(self):
        pass

    def get(self):
        self.write("Successful GET test!")

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        self.write(json["key1"])  # Specific Value - no key for all values


class SortHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = 'select * from SamtoolsSort limit 1'
        results = self.db.get(sqlstr)
        self.write("SamtoolsSort sample : {}".format(results))

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        columns = ''
        values = ''
        for key, value in json.iteritems():
            columns = columns + '\"' + str(key) + '\", '
            values = values + '\"' + str(value) + '\", '
        c = columns[:-2]
        v = values[:-2]
        sqlstr = "INSERT INTO SamtoolsSort ({}) VALUES ({})".format(c, v)
        print(sqlstr)
        db2 = sqlite3.connect('time_keep_database.db')
        c = db2.cursor()
        c.execute(sqlstr)
        db2.commit()
        db2.close()

        #results = self.db.execute(sqlstr)
        #print(results)
        self.write(sqlstr)


class MpileupHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = 'select * from MpileUp limit 1'
        results = self.db.get(sqlstr)
        self.write("MpileUp sample : {}".format(results))

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        columns = ''
        values = ''
        for key, value in json.iteritems():
            columns = columns + str(key) + ', '
            values = values + str(value) + ', '
        c = columns[:-2]
        v = values[:-2]
        sqlstr = "INSERT INTO MpileUp ({}) VALUES ({})".format(c, v)
        print(sqlstr)
        results = self.db.execute(sqlstr)
        print(results)
        self.write(sqlstr)


class VarscanSomaticHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = 'select * from VarscanSomatic limit 1'
        results = self.db.get(sqlstr)
        self.write("VarscanSomatic sample : {}".format(results))

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        columns = ''
        values = ''
        for key, value in json.iteritems():
            columns = columns + str(key) + ', '
            values = values + str(value) + ', '
        c = columns[:-2]
        v = values[:-2]
        sqlstr = "INSERT INTO VarscanSomatic ({}) VALUES ({})".format(c, v)
        print(sqlstr)
        results = self.db.execute(sqlstr)
        print(results)
        self.write(sqlstr)


class VarscanProcessSomaticSnpsHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = 'select * from VarscanProcessSnps limit 1'
        results = self.db.get(sqlstr)
        self.write("VarscanProcessSnps sample : {}".format(results))

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        columns = ''
        values = ''
        for key, value in json.iteritems():
            columns = columns + str(key) + ', '
            values = values + str(value) + ', '
        c = columns[:-2]
        v = values[:-2]
        sqlstr = "INSERT INTO VarscanProcessSnps ({}) VALUES ({})".format(c, v)
        print(sqlstr)
        results = self.db.execute(sqlstr)
        print(results)
        self.write(sqlstr)


class VarscanProcessSomaticIndelsHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = 'select * from VarscanProcessIndels limit 1'
        results = self.db.get(sqlstr)
        self.write("VarscanProcessIndels sample : {}".format(results))

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        columns = ''
        values = ''
        for key, value in json.iteritems():
            columns = columns + str(key) + ', '
            values = values + str(value) + ', '
        c = columns[:-2]
        v = values[:-2]
        sqlstr = "INSERT INTO VarscanProcessIndels ({}) VALUES ({})".format(c, v)
        print(sqlstr)
        results = self.db.execute(sqlstr)
        print(results)
        self.write(sqlstr)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/samtoolssort/", SortHandler),
            (r"/mpileup/", MpileupHandler),
            (r"/varscansomatic/", VarscanSomaticHandler),
            (r"/varscanprocesssomaticsnps/", VarscanProcessSomaticSnpsHandler),
            (r"/varscanprocesssomaticindels/", VarscanProcessSomaticIndelsHandler),
            (r"/test/", TestHandler)
        ]
        settings = {}
        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = database.Connection()
        # self.db.execute('create table users (id integer, name char(20));')
        # self.db.execute('insert into users (id, name) values (1,"jack");')
        # self.db.execute('insert into users (id, name) values (2,"jill");')


if __name__ == "__main__":
    settings = {}
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()

    # app = make_app()
    # app.listen(80)
    # tornado.ioloop.IOLoop.current().start()
