import argparse

from website import create_app

parser = argparse.ArgumentParser()
parser.add_argument("--remote", action="store_true")

if __name__ == "__main__":
    args = parser.parse_args()

    app = create_app(remote=args.remote)

    # app.run(host="0.0.0.0") # externally visible
    app.run(host="localhost", debug=True)
