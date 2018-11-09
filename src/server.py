import tornado.ioloop
import tornado.web
import sqlite3

CONNECTION = sqlite3.connect('wgstimes.db')
TIME_DB = CONNECTION.cursor()

try:

CREATE TABLE contacts (
 contact_id integer PRIMARY KEY,
 first_name text NOT NULL,
 last_name text NOT NULL,
 email text NOT NULL UNIQUE,
 phone text NOT NULL UNIQUE
);
except sqlite3.OperationalError:
    pass

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class RecordDataTumorSort(tornado.web.RequestHandler):
    def initialize(self):
        self.connection = sqlite3.connect(SQLITE_FILE)
        pass
    
    def post(self):
        username = self.get_argument('username')
        designation = self.get_argument('designation')
        self.write("Wow " + username + " you're a " + designation)

class RecordDataNormalSort(tornado.web.RequestHandler):
    def initialize(self):
        self.connection = sqlite3.connect(SQLITE_FILE)
        pass
    
    def post(self):
        username = self.get_argument('username')
        designation = self.get_argument('designation')
        self.write("Wow " + username + " you're a " + designation)

class RecordDataMpileUp(tornado.web.RequestHandler):
    def initialize(self):
        self.connection = sqlite3.connect(SQLITE_FILE)
        pass
    
    def post(self):
        username = self.get_argument('username')
        designation = self.get_argument('designation')
        self.write("Wow " + username + " you're a " + designation)

class RecordDataBaseMutations(tornado.web.RequestHandler):
    def initialize(self):
        self.connection = sqlite3.connect(SQLITE_FILE)
        pass
    
    def post(self):
        username = self.get_argument('username')
        designation = self.get_argument('designation')
        self.write("Wow " + username + " you're a " + designation)

class RecordDataSomaticSNPs(tornado.web.RequestHandler):
    def initialize(self):
        self.connection = sqlite3.connect(SQLITE_FILE)
        pass
    
    def post(self):
        username = self.get_argument('username')
        designation = self.get_argument('designation')
        self.write("Wow " + username + " you're a " + designation)

class RecordDataSomaticIndels(tornado.web.RequestHandler):
    def initialize(self):
        self.connection = sqlite3.connect(SQLITE_FILE)
        pass
    
    def post(self):
        username = self.get_argument('username')
        designation = self.get_argument('designation')
        self.write("Wow " + username + " you're a " + designation)

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/recorddatatumorsort/", RecordDataTumorSort),
        (r"/recorddatanormalsort/", RecordDataNormalSort),
        (r"/recorddatampileup/", RecordDataMpileUp),
        (r"/recorddatabasemutations/", RecordDataBaseMutations),
        (r"/recorddatasomaticsnps/", RecordDataSomaticSNPs),
        (r"/recorddatasomaticindels/", RecordDataSomaticIndels),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
