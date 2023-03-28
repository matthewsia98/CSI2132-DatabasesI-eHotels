from . import db


class Chain(db.Model):
    __tablename__ = "chains"
    chain_id = db.Column(db.Integer, primary_key=True)
    chain_name = db.Column(db.Text)
    num_hotels = db.Column(db.Integer)
