from search_rex.factory import create_app
from search_rex.recommendations import create_recommender_system

if __name__ == '__main__':
    app = create_app('recsys_config.DevelopmentConfig')
    create_recommender_system(app)
    app.run(debug=True)
