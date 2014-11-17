from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)

from search_rec import GenericSearchResultRecommender
from data_model import PersistentDataModel

rec_systems = {}


def init_communities():
    for community_id in app.config['COMMUNITIES']:
        rec_systems[community_id] = GenericSearchResultRecommender(
            PersistentDataModel(community_id), None, None)

from . import models, controller
