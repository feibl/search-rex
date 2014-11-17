from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)

from search_rec import GenericSearchResultRecommender
from query_sim import StringJaccardSimilarity
from query_nhood import ThresholdQueryNeighbourhood
from data_model import PersistentDataModel

rec_systems = {}


def init_communities():
    for community_id in app.config['COMMUNITIES']:
        d_model = PersistentDataModel(community_id)
        q_sim = StringJaccardSimilarity(k_shingles=3)
        q_nhood = ThresholdQueryNeighbourhood(
            data_model=d_model, query_sim=q_sim, sim_threshold=0.2)
        rec_systems[community_id] = GenericSearchResultRecommender(
            data_model=d_model,
            query_sim=q_sim,
            query_nhood=q_nhood)

from . import models, controller
