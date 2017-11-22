from app import db


class Temperature(db.Model):
    """
       Model for temperature storing.
    """
    timestamp = db.Column(db.Integer, primary_key=True, index=True, unique=True)
    data = db.Column(db.String(20))

    def __repr__(self):
        return 'From: %r\ntemperature\n%r\n' % (self.timestamp, self.temp)

    def str(self):
        return 'From: %r\ntemperature\n%r\n' % (self.timestamp, self.temp)
