from search_rex import app
from search_rex import init_communities

if __name__ == '__main__':
    init_communities()
    app.run(debug=True)
