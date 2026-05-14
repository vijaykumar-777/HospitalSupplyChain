import pytest
from backend.services.disaster_pipeline import haversine_km, is_in_disaster_zone

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
