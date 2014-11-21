from search_rex.factory import create_app
from search_rex import init_communities

if __name__ == '__main__':
    app = create_app('config.DevelopmentConfig')
    init_communities(app)
    app.run(debug=True)
