from flask import Blueprint, jsonify, request, send_file
from app.models import Country
from app import db
from datetime import datetime
import random
import requests
import os
from app.utils import generate_summary_image

main = Blueprint("main", __name__)

COUNTRIES_API = os.getenv("COUNTRIES_API", "https://restcountries.com/v2/all?fields=name,capital,region,population,"
                                           "flag,currencies")
EXCHANGE_API = os.getenv("EXCHANGE_API", "https://open.er-api.com/v6/latest/USD")

@main.route("/")
def home():
    return jsonify({
        "message": "Welcome to the HNG Stage 2 Country Currency & Exchange API!"
    }), 200

@main.route("/init-db")
def init_db():
    db.create_all()
    return {"message": "Database initialized successfully!"}

@main.route("/countries/refresh", methods=["POST"])
def refresh_countries():
    try:
        countries_res = requests.get(COUNTRIES_API, timeout=10)
        exchange_res = requests.get(EXCHANGE_API, timeout=10)
        if countries_res.status_code != 200 or exchange_res.status_code != 200:
            return jsonify({
                "error": "External data source unavailable",
                "details": "Could not fetch data from one or both APIs"
            }), 503

        countries_data = countries_res.json()
        exchange_data = exchange_res.json().get("rates", {})

        for c in countries_data:
            name = c.get("name")
            capital = c.get("capital")
            region = c.get("region")
            population = c.get("population", 0)
            flag_url = c.get("flag") or c.get("flags", {}).get("png")
            currencies = c.get("currencies", [])

            currency_code = None
            exchange_rate = None
            estimated_gdp = 0

            if currencies:
                currency_code = currencies[0].get("code")
                if currency_code in exchange_data:
                    exchange_rate = exchange_data[currency_code]
                    multiplier = random.uniform(1000, 2000)
                    estimated_gdp = (population * multiplier) / exchange_rate if exchange_data else None
                else:
                    exchange_rate = None
                    estimated_gdp = None

            country = Country.query.filter_by(name=name).first()
            if country:
                # Update existing record
                country.capital = capital
                country.region = region
                country.population = population
                country.currency_code = currency_code
                country.exchange_rate = exchange_rate
                country.estimated_gdp = estimated_gdp
                country.flag_url = flag_url
                country.last_refreshed_at = datetime.utcnow()
            else:
                # Add new record
                new_country = Country(
                    name=name,
                    capital=capital,
                    region=region,
                    population=population,
                    currency_code=currency_code,
                    exchange_rate=exchange_rate,
                    estimated_gdp=estimated_gdp,
                    flag_url=flag_url,
                    last_refreshed_at=datetime.utcnow()
                )
                db.session.add(new_country)
        db.session.commit()
        os.makedirs(os.path.join(os.getcwd(), "cache"), exist_ok=True)
        generate_summary_image()

        total = Country.query.count()
        last_refresh = datetime.utcnow().isoformat()
        return jsonify({
            "message": "Countries refreshed and summary image generated successfully",
            "total_countries": total,
            "last_refreshed_at": last_refresh
        }), 200

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "External data source unavailable",
            "details": "Could not connect to APIs"
        }), 503

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500

@main.route("/countries", methods=["GET"])
def get_countries():
    try:
        query = Country.query
        region = request.args.get("region")
        currency = request.args.get("currency")

        if region:
            query = query.filter(Country.region.ilike(f"%{region}%"))
        if currency:
            query = query.filter(Country.currency_code == currency)

        sort = request.args.get("sort")
        if sort:
            if sort == "gdp_desc":
                query = query.order_by(Country.estimated_gdp.desc())
            elif sort == "gdp_asc":
                query = query.order_by(Country.estimated_gdp.asc())
            elif sort == "population_desc":
                query = query.order_by(Country.population.desc())
            elif sort == "population_asc":
                query = query.order_by(Country.population.asc())

        countries = query.all()

        result = [country.to_dict() for country in countries]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "error": "Internal Server error",
            "details": str(e)
        }), 500

@main.route("/countries/<string:name>", methods=["GET"])
def get_country(name):
    country = Country.query.filter_by(name=name).first()

    if not country:
        return jsonify({
            "error": "Country not found",
            "message": f"No country found with the name {name}"
        }), 404

    return jsonify(country.to_dict()), 200

@main.route("/countries/<string:name>", methods=["DELETE"])
def delete_country(name):
    country = Country.query.filter_by(name=name).first()

    if not country:
        return jsonify({
            "error": "Country not found",
            "message": f"No country found with the name {name}"
        }), 404

    db.session.delete(country)
    db.session.commit()

    return jsonify({
        "message": f"Country {name} has been deleted successfully"
    }), 200

@main.route("/status", methods=["GET"])
def get_status():
    try:
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        print("Database connection error:", e)
        db_status = "disconnected"

    return jsonify({
        "status": "ok",
        "database": db_status,
        "message": "Country API is working smoothly"
    })

@main.route("/countries/image", methods=["GET"])
def get_countries_image():
    cache_dir = os.path.join(os.getcwd(), "cache")
    image_path = os.path.join(cache_dir, "summary.png")

    if not os.path.exists(image_path):
        return jsonify({
            "error": "Summary image not found. Please run /countries/refresh first."
        }), 404

    return send_file(image_path, mimetype="image/png")
