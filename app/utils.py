from app.models import Country
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
from app import db

def generate_summary_image():
    os.makedirs("cache", exist_ok=True)
    total_countries = Country.query.count()
    top_countries = Country.query.order_by(Country.estimated_gdp.desc()).limit(5).all()
    last_refresh = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    img = Image.new("RGB", (600, 400), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.text((20, 20), f"Total Countries: {total_countries}", fill=(255, 255, 255), font=font)
    draw.text((20, 50), text="Top 5 Countries by Estimated GDP:", fill=(255, 255, 255), font=font)

    y=80
    for i, country in enumerate(top_countries, start=1):
        draw.text((40, y), f"{i}. {country.name} - ${country.estimated_gdp:,.0f}",
                  fill=(200, 200, 200), font=font)
        y += 25
    draw.text((40, y + 20), f"Last Refreshed: {last_refresh}", fill=(255, 255, 255), font=font)

    img.save("cache/summary.png")
