from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from search_rex.core import db
from search_rex.factory import create_app

app = create_app()
migrate = Migrate(app, db, directory='migrations')
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
