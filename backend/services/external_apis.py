import os
import httpx
import logging
from xml.etree import ElementTree as ET
from backend.settings import NEWS_API_KEY, ORS_API_KEY

logger = logging.getLogger(__name__)

async def fetch_gdacs_alerts() -> list[dict]:
    """Fetch active disaster alerts from GDACS."""
    url = "https://www.gdacs.org/xml.aspx"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
        root = ET.fromstring(resp.text)
        events = []
        for item in root.findall('.//item'):
            events.append({
                "source": "gdacs",
                "title": item.findtext('title'),
                "description": item.findtext('description'),
                "pubDate": item.findtext('pubDate'),
                "link": item.findtext('link')
            })
        return events
    except Exception as e:
        logger.error(f"GDACS fetch error: {e}")
        return []

async def fetch_reliefweb_alerts() -> list[dict]:
    """Fetch active disaster alerts from ReliefWeb for India."""
    url = "https://api.reliefweb.int/v1/disasters"
    params = {
        "appname": "hospital-supply-chain",
        "filter[field]": "country.name",
        "filter[value]": "India",
        "limit": 10,
        "sort[]": "date:desc"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        data = resp.json().get("data", [])
        return [{"source": "reliefweb", **item} for item in data]
    except Exception as e:
        logger.error(f"ReliefWeb fetch error: {e}")
        return []

async def fetch_news_disaster_alerts() -> list[dict]:
    """Fetch disaster-related news for India from NewsAPI."""
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set. Skipping NewsAPI.")
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "disaster OR flood OR earthquake OR cyclone OR fire India hospital",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [{"source": "newsapi", **item} for item in articles]
    except Exception as e:
        logger.error(f"NewsAPI fetch error: {e}")
        return []

async def get_alternate_route(
    origin_lat: float, origin_lng: float,
    dest_lat: float, dest_lng: float,
    avoid_polygon_geojson: dict
) -> dict:
    """Fetch alternate route avoiding a specific disaster polygon using OpenRouteService."""
    if not ORS_API_KEY:
        logger.warning("ORS_API_KEY not set. Skipping OpenRouteService.")
        return {}
    url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {
        "coordinates": [[origin_lng, origin_lat], [dest_lng, dest_lat]],
        "options": {"avoid_polygons": avoid_polygon_geojson}
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=body, headers=headers)
            resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"OpenRouteService fetch error: {e}")
        return {}

async def geocode_city(city_name: str) -> tuple[float, float]:
    """Geocode an Indian city using Nominatim (OpenStreetMap)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name + ", India", "format": "json", "limit": 1}
    headers = {"User-Agent": "hospital-supply-chain/1.0"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        raise ValueError(f"Could not geocode: {city_name}")
    except Exception as e:
        logger.error(f"Geocoding error for {city_name}: {e}")
        raise
