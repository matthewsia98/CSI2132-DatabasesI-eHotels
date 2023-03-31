import traceback

from website import create_app, db

if __name__ == "__main__":
    app = create_app()
    app.run(host="localhost", debug=True)
