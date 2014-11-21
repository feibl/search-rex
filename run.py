from search_rex.factory import create_app

if __name__ == '__main__':
    app = create_app('config.DevelopmentConfig')
    app.run(debug=True)
