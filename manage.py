from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from search_rex import app, db

migrate = Migrate(app, db, directory='migrations')
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
