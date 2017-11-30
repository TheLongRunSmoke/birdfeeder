from app import db


class Temperature(db.Model):
    """
       Model for temperature storing.
    """
    timestamp = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    internal = db.Column(db.Float)
    external = db.Column(db.Float)
    cpu = db.Column(db.Float)

    def __repr__(self):
        return '<Timestamp: %r>' % self.timestamp
