from os.path import isfile
from sqlite3 import connect
from apscheduler.triggers.cron import CronTrigger

db_path = "./data/db/data.db"

class database_manager:
    def __init__(self) -> None:
        self.cxn = connect(db_path, check_same_thread=False)
        self.cur = self.cxn.cursor()
    
    def commit(self):
        self.cxn.commit()

    def close(self):
        self.cxn.close()

    def autosave(self, sched):
        sched.add_job(self.commit, CronTrigger(second=0))

    def field(self, command, *values):
        self.cur.execute(command, tuple(values))
        if(fetch := self.cur.fetchone()) is not None:
            return fetch[0]

    def record(self, command, *values):
        self.cur.execute(command, tuple(values))

        return self.cur.fetchone()
    
    def records(self, command, *values):
        self.cur.execute(command, tuple(values))

        return [item[0] for item in self.cur.fetchall()]
    
    def column(self, command, *values):
        self.cur.execute(command, tuple(values))
        return [item[0] for item in self.cur.fetchall()]

    def execute(self, command, *values):
        self.cur.execute(command, tuple(values))

    def multiexec(self, command, valueset):
        self.cur.executemany(command, valueset)
