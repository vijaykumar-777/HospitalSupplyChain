import pytest
from backend.services.disaster_pipeline import build_bypass_waypoints, build_hosted_ors_avoid_polygon, haversine_km, is_in_disaster_zone

def test_haversine_distance_same_point():
    # Distance from point to itself should be 0
    dist = haversine_km(12.9716, 77.5946, 12.9716, 77.5946)
    assert dist == 0.0

def test_haversine_distance_known_cities():
    # Bengaluru to Chennai is ~290km straight line
    # Bengaluru: 12.9716, 77.5946
    # Chennai: 13.0827, 80.2707
    dist = haversine_km(12.9716, 77.5946, 13.0827, 80.2707)
    assert 280 < dist < 300

def test_is_in_disaster_zone():
    bengaluru = (12.9716, 77.5946)
    chennai = (13.0827, 80.2707)
    
    # 350km radius should include Chennai from Bengaluru
    assert is_in_disaster_zone(chennai[0], chennai[1], bengaluru[0], bengaluru[1], 350) is True
    
    # 200km radius should NOT include Chennai from Bengaluru
    assert is_in_disaster_zone(chennai[0], chennai[1], bengaluru[0], bengaluru[1], 200) is False


def test_build_bypass_waypoints_returns_clearance_candidates():
    waypoints = build_bypass_waypoints(
        origin_lat=13.0827,
        origin_lng=80.2707,
        dest_lat=12.9716,
        dest_lng=77.5946,
        event_lat=12.98,
        event_lng=78.7,
        radius_km=80,
    )

    assert len(waypoints) == 2
    for waypoint_lng, waypoint_lat in waypoints:
        assert haversine_km(waypoint_lat, waypoint_lng, 12.98, 78.7) >= 79


def test_hosted_ors_avoid_polygon_skips_long_routes():
    polygon = build_hosted_ors_avoid_polygon(
        origin_lat=13.0827,
        origin_lng=80.2707,
        dest_lat=12.9716,
        dest_lng=77.5946,
        event_lat=12.98,
        event_lng=78.7,
        radius_km=80,
    )

    assert polygon is None


def test_hosted_ors_avoid_polygon_caps_radius_for_short_routes():
    polygon = build_hosted_ors_avoid_polygon(
        origin_lat=12.91,
        origin_lng=77.5,
        dest_lat=12.98,
        dest_lng=77.7,
        event_lat=12.94,
        event_lng=77.6,
        radius_km=80,
    )

    assert polygon["type"] == "Polygon"
    first_lng, first_lat = polygon["coordinates"][0][0]
    assert 7 < haversine_km(first_lat, first_lng, 12.94, 77.6) < 8
