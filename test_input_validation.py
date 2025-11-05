"""
Test for input validation in select_cup endpoint
"""
from starlette.testclient import TestClient
from main import app


def test_select_cup_valid_colors():
    """Test that valid colors are accepted"""
    client = TestClient(app)
    
    # Test each valid color
    for color in ['green', 'yellow', 'red']:
        response = client.get(f'/select_cup/{color}')
        assert response.status_code == 200
        content = response.text
        # Should contain the color name capitalized
        assert color.capitalize() in content or color in content
        # Should not contain "Invalid"
        assert "Invalid" not in content
        print(f"✓ Valid color '{color}' accepted")


def test_select_cup_invalid_colors():
    """Test that invalid colors are rejected with safe response"""
    client = TestClient(app)
    
    # Test colors that would pass routing but are invalid
    invalid_colors = [
        'blue',
        'orange',
        'purple',
        'cyan',
        'magenta',
    ]
    
    for color in invalid_colors:
        response = client.get(f'/select_cup/{color}')
        assert response.status_code == 200
        content = response.text
        # Should contain error message
        assert "Invalid" in content
        print(f"✓ Invalid color '{color}' rejected safely")


def test_select_cup_response_format():
    """Test that the response is properly formatted HTML"""
    client = TestClient(app)
    
    response = client.get('/select_cup/green')
    assert response.status_code == 200
    content = response.text
    
    # Should be HTML (Div element)
    assert '<div>' in content.lower() or 'div' in content.lower()
    # Should contain Strong element for color
    assert '<strong>' in content.lower() or 'strong' in content.lower()
    # Should contain the word "Green" capitalized
    assert 'Green' in content
    
    print("✓ Response format is safe HTML")


if __name__ == "__main__":
    test_select_cup_valid_colors()
    test_select_cup_invalid_colors()
    test_select_cup_response_format()
    print("\n✅ All input validation tests passed!")
