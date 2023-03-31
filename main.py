import traceback

from website import create_app, db

if __name__ == "__main__":
    try:
        app = create_app()
        app.run(host="0.0.0.0", debug=True)
    except:
        traceback.print_exc()
    finally:
        db.rollback()
        db.close()
