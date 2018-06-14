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
        sqlstr = 'select * from SamtoolsSort'
        results = self.db.get(sqlstr)
        self.write("Test:  %s" % results)

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        self.write(json["key1"]) # Specific Value - no key for all values


class SortHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        sqlstr = 'select * from SamtoolsSort'
        results = self.db.get(sqlstr)
        self.write("Hello sort world : {}".format(results))

    def post(self):
        json = tornado.escape.json_decode(self.request.body)
        columns = ''
        values = ''
        for key, value in json.iteritems():
            columns = columns + key + ', '
            values = values + value + ', '
        c = columns[:-2]
        v = values[:-2]
        sqlstr = "INSERT INTO SamtoolsSort ({}) VALUES ({})".format(c, v)
        print(sqlstr)
        self.write(sqlstr)


class MpileupHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json = tornado.escape.json_decode(self.response.body)


class VarscanSomaticHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json = tornado.escape.json_decode(self.response.body)


class VarscanProcessSomaticSnpsHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json = tornado.escape.json_decode(self.response.body)


class VarscanProcessSomaticIndelsHandler(MainHandler):
    def initialize(self):
        pass

    def get(self):
        pass

    def post(self):
        json = tornado.escape.json_decode(self.response.body)


# def make_app():
#    return tornado.web.Application([
#        url(r"/", MainHandler),
#        url(r"/samtoolssort", SortHandler, dict(db=db), name="sort"),
#        url(r"/mpileup", MpileupHandler, dict(db=db), name="mpileup"),
#        url(r"/varscansomatic", VarscanSomaticHandler, dict(db=db), name="varscansomatic"),
#        url(r"/varscanprocesssomaticsnps", VarscanProcessSomaticSnpsHandler, dict(db=db), name="varscansomaticprocesssnps"),
#        url(r"/varscanprocesssomaticindels", VarscanProcessSomaticIndelsHandler, dict(db=db), name="varscanprocesssomaticindels"),
#        url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
#    ])

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
