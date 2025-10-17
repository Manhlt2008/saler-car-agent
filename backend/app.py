from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
import openai
import requests
import googlemaps
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import json
from datetime import datetime, timedelta
import random

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/car_agent_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Initialize external services
openai.api_key = os.environ.get('OPENAI_API_KEY')
gmaps = None
sg = None

# Initialize Google Maps if API key is provided
if os.environ.get('GOOGLE_MAPS_API_KEY') and os.environ.get('GOOGLE_MAPS_API_KEY').strip():
    gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_API_KEY'))

# Initialize SendGrid if API key is provided
if os.environ.get('SENDGRID_API_KEY') and os.environ.get('SENDGRID_API_KEY').strip():
    sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))

# Database Models
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    price_min = db.Column(db.Integer, nullable=False)
    price_max = db.Column(db.Integer, nullable=False)
    segment = db.Column(db.String(50), nullable=False)  # sedan, suv, hatchback, etc.
    seats = db.Column(db.Integer, nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)  # petrol, diesel, hybrid, electric
    transmission = db.Column(db.String(20), nullable=False)  # manual, automatic
    engine_power = db.Column(db.String(20), nullable=False)
    features = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Showroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(100), nullable=True)
    brands = db.Column(db.Text, nullable=True)  # JSON array of brands
    offers = db.Column(db.Text, nullable=True)  # JSON array of current offers
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    preferences = db.Column(db.Text, nullable=True)  # JSON of user preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    showroom_id = db.Column(db.Integer, db.ForeignKey('showroom.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# AI Agent Logic
class CarAgent:
    def __init__(self):
        self.conversation_history = []
    
    def process_user_request(self, message, user_context=None, user_location=None):
        """Process user message and return AI response"""
        self.conversation_history.append({"role": "user", "content": message})
        
        # Analyze user requirements
        requirements = self.analyze_requirements(message)
        
        if requirements.get('stage') == 'initial':
            return self.get_car_recommendations(requirements)
        elif requirements.get('stage') == 'comparing':
            return self.compare_cars(requirements)
        elif requirements.get('stage') == 'email_request':
            return self.request_email()
        elif requirements.get('stage') == 'showroom_search':
            return self.find_nearby_showrooms(requirements, user_location)
        elif requirements.get('stage') == 'test_drive':
            return self.schedule_test_drive(requirements)
        else:
            return self.general_response(message)
    
    def analyze_requirements(self, message):
        """Analyze user message to extract car requirements"""
        # This would use OpenAI to analyze the message
        # For now, using simple keyword matching
        requirements = {
            'budget_min': None,
            'budget_max': None,
            'segment': None,
            'seats': None,
            'fuel_type': None,
            'transmission': None,
            'stage': 'initial'
        }
        
        message_lower = message.lower()
        
        # Extract budget
        if 'dưới' in message_lower or 'dưới' in message_lower:
            if 'triệu' in message_lower:
                # Extract number before "triệu"
                import re
                numbers = re.findall(r'\d+', message)
                if numbers:
                    requirements['budget_max'] = int(numbers[0]) * 1000000
        
        # Extract segment
        if 'sedan' in message_lower:
            requirements['segment'] = 'sedan'
        elif 'suv' in message_lower:
            requirements['segment'] = 'suv'
        elif 'hatchback' in message_lower:
            requirements['segment'] = 'hatchback'
        
        # Extract seats
        if 'ghế' in message_lower:
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                requirements['seats'] = int(numbers[0])
        
        return requirements
    
    def get_car_recommendations(self, requirements):
        """Get 3 car recommendations based on requirements"""
        # Query database for matching cars
        query = Car.query
        
        if requirements.get('budget_max'):
            query = query.filter(Car.price_max <= requirements['budget_max'])
        
        if requirements.get('segment'):
            query = query.filter(Car.segment == requirements['segment'])
        
        if requirements.get('seats'):
            query = query.filter(Car.seats == requirements['seats'])
        
        cars = query.limit(3).all()
        
        if not cars:
            # Fallback to any cars if no exact match
            cars = Car.query.limit(3).all()
        
        response = "Dựa trên yêu cầu của bạn, tôi xin giới thiệu 3 mẫu xe phù hợp:\n\n"
        
        for i, car in enumerate(cars, 1):
            response += f"{i}. **{car.brand} {car.name}**\n"
            response += f"   - Giá: {car.price_min:,} - {car.price_max:,} VNĐ\n"
            response += f"   - Phân khúc: {car.segment}\n"
            response += f"   - Số ghế: {car.seats}\n"
            response += f"   - Nhiên liệu: {car.fuel_type}\n"
            response += f"   - Hộp số: {car.transmission}\n"
            response += f"   - Công suất: {car.engine_power}\n\n"
        
        response += "Bạn có muốn tôi so sánh chi tiết 3 mẫu xe này không?"
        
        return response
    
    def compare_cars(self, requirements):
        """Compare the 3 recommended cars"""
        cars = Car.query.limit(3).all()
        
        response = "**BẢNG SO SÁNH CHI TIẾT 3 MẪU XE:**\n\n"
        response += "| Tiêu chí | "
        
        for car in cars:
            response += f"{car.brand} {car.name} | "
        response += "\n|----------|"
        
        for _ in cars:
            response += "----------|"
        response += "\n"
        
        # Price comparison
        response += "| Giá (VNĐ) | "
        for car in cars:
            response += f"{car.price_min:,} - {car.price_max:,} | "
        response += "\n"
        
        # Seats comparison
        response += "| Số ghế | "
        for car in cars:
            response += f"{car.seats} | "
        response += "\n"
        
        # Fuel type comparison
        response += "| Nhiên liệu | "
        for car in cars:
            response += f"{car.fuel_type} | "
        response += "\n"
        
        # Transmission comparison
        response += "| Hộp số | "
        for car in cars:
            response += f"{car.transmission} | "
        response += "\n"
        
        response += "\nBạn muốn chọn mẫu xe nào? (1, 2, hoặc 3)"
        
        return response
    
    def request_email(self):
        """Request user's email for quote"""
        return "Tuyệt vời! Để tôi gửi thông tin báo giá chi tiết, bạn vui lòng cung cấp email của mình nhé!"
    
    def find_nearby_showrooms(self, requirements, user_location=None):
        """Find nearby showrooms using Google Maps API"""
        try:
            if user_location and gmaps:
                # Use Google Maps API to find nearby showrooms
                places_result = gmaps.places_nearby(
                    location=user_location,
                    radius=50000,  # 50km radius
                    type='car_dealer'
                )
                
                showrooms = []
                for place in places_result.get('results', [])[:3]:
                    showroom_info = {
                        'name': place.get('name', 'Unknown'),
                        'address': place.get('vicinity', 'Unknown'),
                        'rating': place.get('rating', 0),
                        'place_id': place.get('place_id', ''),
                        'location': place.get('geometry', {}).get('location', {})
                    }
                    showrooms.append(showroom_info)
            else:
                # Fallback to database showrooms
                showrooms = Showroom.query.limit(3).all()
                showrooms = [{
                    'name': s.name,
                    'address': s.address,
                    'phone': s.phone,
                    'website': s.website,
                    'offers': json.loads(s.offers) if s.offers else []
                } for s in showrooms]
            
            response = "Tôi đã tìm thấy một số showroom gần bạn:\n\n"
            
            for i, showroom in enumerate(showrooms, 1):
                response += f"{i}. **{showroom['name']}**\n"
                response += f"   - Địa chỉ: {showroom['address']}\n"
                
                if 'phone' in showroom:
                    response += f"   - Điện thoại: {showroom['phone']}\n"
                if 'website' in showroom:
                    response += f"   - Website: {showroom['website']}\n"
                if 'rating' in showroom and showroom['rating']:
                    response += f"   - Đánh giá: {showroom['rating']}/5 ⭐\n"
                if 'offers' in showroom and showroom['offers']:
                    response += f"   - Ưu đãi: {', '.join(showroom['offers'][:2])}\n"
                
                response += "\n"
            
            response += "Bạn có muốn đăng ký lái thử tại showroom nào không?"
            
            return response
            
        except Exception as e:
            print(f"Error finding nearby showrooms: {e}")
            # Fallback response
            return "Tôi đã tìm thấy một số showroom gần bạn. Bạn có muốn đăng ký lái thử không?"
    
    def schedule_test_drive(self, requirements):
        """Schedule test drive"""
        return "Tôi sẽ giúp bạn đăng ký lái thử. Bạn muốn đặt lịch vào thời gian nào?"
    
    def general_response(self, message):
        """General response for unclear messages"""
        return "Xin chào! Tôi là AI agent tư vấn bán xe. Tôi có thể giúp bạn:\n- Tìm xe phù hợp với ngân sách và nhu cầu\n- So sánh các mẫu xe\n- Tìm showroom gần nhất\n- Đăng ký lái thử\n\nBạn có thể cho tôi biết ngân sách và yêu cầu của bạn không?"

# Initialize AI Agent
car_agent = CarAgent()

# API Routes
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_context = data.get('context', {})
        user_location = data.get('location')  # {lat, lng}
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process message with AI agent
        response = car_agent.process_user_request(message, user_context, user_location)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cars', methods=['GET'])
def get_cars():
    try:
        cars = Car.query.all()
        return jsonify([{
            'id': car.id,
            'name': car.name,
            'brand': car.brand,
            'price_min': car.price_min,
            'price_max': car.price_max,
            'segment': car.segment,
            'seats': car.seats,
            'fuel_type': car.fuel_type,
            'transmission': car.transmission,
            'engine_power': car.engine_power,
            'features': car.features,
            'image_url': car.image_url
        } for car in cars])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/showrooms', methods=['GET'])
def get_showrooms():
    try:
        showrooms = Showroom.query.all()
        return jsonify([{
            'id': showroom.id,
            'name': showroom.name,
            'address': showroom.address,
            'latitude': showroom.latitude,
            'longitude': showroom.longitude,
            'phone': showroom.phone,
            'email': showroom.email,
            'website': showroom.website,
            'brands': json.loads(showroom.brands) if showroom.brands else [],
            'offers': json.loads(showroom.offers) if showroom.offers else []
        } for showroom in showrooms])
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-quote', methods=['POST'])
def send_quote():
    try:
        data = request.get_json()
        email = data.get('email')
        car_id = data.get('car_id')
        user_name = data.get('name', '')
        
        if not email or not car_id:
            return jsonify({'error': 'Email and car_id are required'}), 400
        
        car = Car.query.get(car_id)
        if not car:
            return jsonify({'error': 'Car not found'}), 404
        
        # Create or get user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=user_name)
            db.session.add(user)
            db.session.commit()
        
        # Create email content with better formatting
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .car-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .price {{ color: #e74c3c; font-size: 24px; font-weight: bold; }}
                .feature {{ margin: 10px 0; }}
                .cta {{ background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚗 Báo giá xe {car.brand} {car.name}</h1>
                </div>
                <div class="content">
                    <p>Xin chào {user_name if user_name else 'Quý khách'},</p>
                    <p>Cảm ơn bạn đã quan tâm đến mẫu xe <strong>{car.brand} {car.name}</strong>. Dưới đây là thông tin chi tiết về mẫu xe này:</p>
                    
                    <div class="car-info">
                        <h3>📋 Thông tin xe</h3>
                        <div class="feature"><strong>Thương hiệu:</strong> {car.brand}</div>
                        <div class="feature"><strong>Tên xe:</strong> {car.name}</div>
                        <div class="feature"><strong>Giá:</strong> <span class="price">{car.price_min:,} - {car.price_max:,} VNĐ</span></div>
                        <div class="feature"><strong>Phân khúc:</strong> {car.segment.upper()}</div>
                        <div class="feature"><strong>Số ghế:</strong> {car.seats} chỗ</div>
                        <div class="feature"><strong>Nhiên liệu:</strong> {car.fuel_type}</div>
                        <div class="feature"><strong>Hộp số:</strong> {car.transmission}</div>
                        <div class="feature"><strong>Công suất:</strong> {car.engine_power}</div>
                        {f'<div class="feature"><strong>Tính năng:</strong> {car.features}</div>' if car.features else ''}
                    </div>
                    
                    <p>Để biết thêm thông tin chi tiết, ưu đãi đặc biệt và đăng ký lái thử, vui lòng liên hệ showroom gần nhất.</p>
                    
                    <a href="#" class="cta">📞 Liên hệ ngay</a>
                    
                    <p><strong>Lưu ý:</strong> Giá trên có thể thay đổi tùy theo thời điểm và chương trình khuyến mãi. Vui lòng liên hệ showroom để được báo giá chính xác nhất.</p>
                </div>
                <div class="footer">
                    <p>Trân trọng,<br><strong>AI Car Agent Team</strong></p>
                    <p>Email này được gửi tự động từ hệ thống tư vấn xe thông minh</p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        # Create email message
        message = Mail(
            from_email=os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@caragent.com'),
            to_emails=email,
            subject=f'🚗 Báo giá xe {car.brand} {car.name} - AI Car Agent',
            html_content=html_content
        )
        
        # Send email
        if sg:
            response = sg.send(message)
        else:
            # Mock response for development
            response = type('MockResponse', (), {'status_code': 200})()
        
        return jsonify({
            'message': 'Quote sent successfully',
            'status_code': response.status_code,
            'email_sent': True
        })
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

@app.route('/api/schedule-test-drive', methods=['POST'])
def schedule_test_drive():
    try:
        data = request.get_json()
        user_email = data.get('email')
        car_id = data.get('car_id')
        showroom_id = data.get('showroom_id')
        scheduled_date = data.get('scheduled_date')
        
        if not all([user_email, car_id, showroom_id, scheduled_date]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Create or get user
        user = User.query.filter_by(email=user_email).first()
        if not user:
            user = User(email=user_email)
            db.session.add(user)
            db.session.commit()
        
        # Create test drive record
        test_drive = TestDrive(
            user_id=user.id,
            car_id=car_id,
            showroom_id=showroom_id,
            scheduled_date=datetime.fromisoformat(scheduled_date)
        )
        
        db.session.add(test_drive)
        db.session.commit()
        
        return jsonify({
            'message': 'Test drive scheduled successfully',
            'test_drive_id': test_drive.id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/nearby-showrooms', methods=['POST'])
def get_nearby_showrooms():
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        radius = data.get('radius', 50000)  # Default 50km
        
        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Use Google Maps API to find nearby car dealers
        if not gmaps:
            return jsonify({'error': 'Google Maps API not configured'}), 500
            
        places_result = gmaps.places_nearby(
            location=(latitude, longitude),
            radius=radius,
            type='car_dealer'
        )
        
        showrooms = []
        for place in places_result.get('results', [])[:5]:
            # Get detailed information for each place
            place_details = gmaps.place(
                place_id=place['place_id'],
                fields=['name', 'formatted_address', 'formatted_phone_number', 'website', 'rating', 'opening_hours']
            )
            
            details = place_details.get('result', {})
            showroom_info = {
                'name': details.get('name', 'Unknown'),
                'address': details.get('formatted_address', 'Unknown'),
                'phone': details.get('formatted_phone_number', ''),
                'website': details.get('website', ''),
                'rating': details.get('rating', 0),
                'place_id': place['place_id'],
                'location': place['geometry']['location'],
                'is_open': details.get('opening_hours', {}).get('open_now', False)
            }
            showrooms.append(showroom_info)
        
        return jsonify({
            'showrooms': showrooms,
            'count': len(showrooms)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Initialize database with sample data
def init_db():
    with app.app_context():
        db.create_all()
        
        # Add sample cars if database is empty
        if Car.query.count() == 0:
            sample_cars = [
                Car(
                    name="Civic",
                    brand="Honda",
                    price_min=650000000,
                    price_max=850000000,
                    segment="sedan",
                    seats=5,
                    fuel_type="petrol",
                    transmission="automatic",
                    engine_power="174 HP",
                    features="LED headlights, Honda Sensing, Apple CarPlay"
                ),
                Car(
                    name="CR-V",
                    brand="Honda",
                    price_min=950000000,
                    price_max=1200000000,
                    segment="suv",
                    seats=7,
                    fuel_type="petrol",
                    transmission="automatic",
                    engine_power="190 HP",
                    features="AWD, Honda Sensing, Panoramic sunroof"
                ),
                Car(
                    name="Accord",
                    brand="Honda",
                    price_min=1200000000,
                    price_max=1500000000,
                    segment="sedan",
                    seats=5,
                    fuel_type="hybrid",
                    transmission="automatic",
                    engine_power="212 HP",
                    features="Honda Sensing, Wireless charging, Premium audio"
                )
            ]
            
            for car in sample_cars:
                db.session.add(car)
            
            db.session.commit()
        
        # Add sample showrooms if database is empty
        if Showroom.query.count() == 0:
            sample_showrooms = [
                Showroom(
                    name="Honda Center Hà Nội",
                    address="123 Đường Láng, Đống Đa, Hà Nội",
                    latitude=21.0285,
                    longitude=105.8542,
                    phone="024-1234-5678",
                    email="hanoi@honda.com.vn",
                    website="www.honda.com.vn",
                    brands='["Honda"]',
                    offers='["Giảm 50 triệu", "Tặng bảo hiểm 1 năm", "Lãi suất 0%"]'
                ),
                Showroom(
                    name="Honda Center TP.HCM",
                    address="456 Nguyễn Văn Cừ, Quận 5, TP.HCM",
                    latitude=10.7769,
                    longitude=106.7009,
                    phone="028-8765-4321",
                    email="hcm@honda.com.vn",
                    website="www.honda.com.vn",
                    brands='["Honda"]',
                    offers='["Giảm 30 triệu", "Tặng phụ kiện", "Bảo dưỡng miễn phí"]'
                )
            ]
            
            for showroom in sample_showrooms:
                db.session.add(showroom)
            
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
