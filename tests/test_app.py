import pytest
import json
from backend.app import app, db, Car, Showroom, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def sample_car():
    car = Car(
        name="Test Car",
        brand="Test Brand",
        price_min=500000000,
        price_max=700000000,
        segment="sedan",
        seats=5,
        fuel_type="petrol",
        transmission="automatic",
        engine_power="150 HP"
    )
    return car

@pytest.fixture
def sample_showroom():
    showroom = Showroom(
        name="Test Showroom",
        address="123 Test Street",
        latitude=21.0285,
        longitude=105.8542,
        phone="0123456789",
        email="test@showroom.com"
    )
    return showroom

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_chat_endpoint(client):
    """Test chat endpoint"""
    response = client.post('/api/chat', 
                          json={'message': 'Tôi muốn mua xe dưới 1 tỷ'},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'response' in data
    assert 'timestamp' in data

def test_get_cars(client, sample_car):
    """Test get cars endpoint"""
    db.session.add(sample_car)
    db.session.commit()
    
    response = client.get('/api/cars')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == "Test Car"

def test_get_showrooms(client, sample_showroom):
    """Test get showrooms endpoint"""
    db.session.add(sample_showroom)
    db.session.commit()
    
    response = client.get('/api/showrooms')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['name'] == "Test Showroom"

def test_send_quote_missing_data(client):
    """Test send quote endpoint with missing data"""
    response = client.post('/api/send-quote',
                          json={},
                          content_type='application/json')
    assert response.status_code == 400

def test_schedule_test_drive_missing_data(client):
    """Test schedule test drive endpoint with missing data"""
    response = client.post('/api/schedule-test-drive',
                          json={},
                          content_type='application/json')
    assert response.status_code == 400

def test_car_model_creation(sample_car):
    """Test Car model creation"""
    assert sample_car.name == "Test Car"
    assert sample_car.brand == "Test Brand"
    assert sample_car.price_min == 500000000
    assert sample_car.seats == 5

def test_showroom_model_creation(sample_showroom):
    """Test Showroom model creation"""
    assert sample_showroom.name == "Test Showroom"
    assert sample_showroom.address == "123 Test Street"
    assert sample_showroom.latitude == 21.0285
    assert sample_showroom.longitude == 105.8542


