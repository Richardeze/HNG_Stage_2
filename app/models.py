from datetime import datetime
from app import db

class Country(db.Model):
    __tablename__ = "countries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capital = db.Column(db.String(100))
    region = db.Column(db.String(100))
    population = db.Column(db.BigInteger, nullable=False)
    currency_code = db.Column(db.String(10), nullable=True)
    exchange_rate = db.Column(db.Float)
    estimated_gdp = db.Column(db.Float)
    flag_url = db.Column(db.String(255))
    last_refreshed_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Country {self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "capital": self.capital,
            "region": self.region,
            "population": self.population,
            "currency_code": self.currency_code,
            "exchange_rate": self.exchange_rate,
            "estimated_gdp": self.estimated_gdp,
            "flag_url": self.flag_url,
            "last_refreshed_at": (self.last_refreshed_at.isoformat() if self.last_refreshed_at else None)
        }