#!/usr/bin/env python3
"""
Script để seed dữ liệu mẫu vào database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db, Car, Showroom, User
import json

def seed_cars():
    """Seed sample cars data"""
    cars_data = [
        {
            "name": "Civic",
            "brand": "Honda",
            "price_min": 650000000,
            "price_max": 850000000,
            "segment": "sedan",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "174 HP",
            "features": "LED headlights, Honda Sensing, Apple CarPlay, Wireless charging",
            "image_url": "https://example.com/honda-civic.jpg"
        },
        {
            "name": "CR-V",
            "brand": "Honda",
            "price_min": 950000000,
            "price_max": 1200000000,
            "segment": "suv",
            "seats": 7,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "190 HP",
            "features": "AWD, Honda Sensing, Panoramic sunroof, 7-seat configuration",
            "image_url": "https://example.com/honda-crv.jpg"
        },
        {
            "name": "Accord",
            "brand": "Honda",
            "price_min": 1200000000,
            "price_max": 1500000000,
            "segment": "sedan",
            "seats": 5,
            "fuel_type": "hybrid",
            "transmission": "automatic",
            "engine_power": "212 HP",
            "features": "Honda Sensing, Wireless charging, Premium audio, Hybrid system",
            "image_url": "https://example.com/honda-accord.jpg"
        },
        {
            "name": "Camry",
            "brand": "Toyota",
            "price_min": 800000000,
            "price_max": 1100000000,
            "segment": "sedan",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "203 HP",
            "features": "Toyota Safety Sense, 8-inch touchscreen, Dual-zone AC",
            "image_url": "https://example.com/toyota-camry.jpg"
        },
        {
            "name": "RAV4",
            "brand": "Toyota",
            "price_min": 900000000,
            "price_max": 1300000000,
            "segment": "suv",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "203 HP",
            "features": "AWD, Toyota Safety Sense, 7-inch display, All-wheel drive",
            "image_url": "https://example.com/toyota-rav4.jpg"
        },
        {
            "name": "Corolla Cross",
            "brand": "Toyota",
            "price_min": 700000000,
            "price_max": 950000000,
            "segment": "suv",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "169 HP",
            "features": "Toyota Safety Sense, 9-inch touchscreen, LED headlights",
            "image_url": "https://example.com/toyota-corolla-cross.jpg"
        },
        {
            "name": "Mazda3",
            "brand": "Mazda",
            "price_min": 600000000,
            "price_max": 800000000,
            "segment": "sedan",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "165 HP",
            "features": "Skyactiv technology, 8.8-inch display, Bose audio",
            "image_url": "https://example.com/mazda3.jpg"
        },
        {
            "name": "CX-5",
            "brand": "Mazda",
            "price_min": 850000000,
            "price_max": 1150000000,
            "segment": "suv",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "187 HP",
            "features": "Skyactiv technology, AWD, 10.25-inch display, Premium interior",
            "image_url": "https://example.com/mazda-cx5.jpg"
        },
        {
            "name": "Elantra",
            "brand": "Hyundai",
            "price_min": 550000000,
            "price_max": 750000000,
            "segment": "sedan",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "147 HP",
            "features": "SmartSense, 8-inch touchscreen, Wireless charging",
            "image_url": "https://example.com/hyundai-elantra.jpg"
        },
        {
            "name": "Tucson",
            "brand": "Hyundai",
            "price_min": 750000000,
            "price_max": 1050000000,
            "segment": "suv",
            "seats": 5,
            "fuel_type": "petrol",
            "transmission": "automatic",
            "engine_power": "177 HP",
            "features": "SmartSense, 10.25-inch display, AWD, Panoramic sunroof",
            "image_url": "https://example.com/hyundai-tucson.jpg"
        }
    ]
    
    print("Seeding cars data...")
    for car_data in cars_data:
        car = Car(**car_data)
        db.session.add(car)
    
    db.session.commit()
    print(f"✅ Added {len(cars_data)} cars")

def seed_showrooms():
    """Seed sample showrooms data"""
    showrooms_data = [
        {
            "name": "Honda Center Hà Nội",
            "address": "123 Đường Láng, Đống Đa, Hà Nội",
            "latitude": 21.0285,
            "longitude": 105.8542,
            "phone": "024-1234-5678",
            "email": "hanoi@honda.com.vn",
            "website": "www.honda.com.vn",
            "brands": json.dumps(["Honda"]),
            "offers": json.dumps(["Giảm 50 triệu", "Tặng bảo hiểm 1 năm", "Lãi suất 0%", "Tặng phụ kiện"])
        },
        {
            "name": "Honda Center TP.HCM",
            "address": "456 Nguyễn Văn Cừ, Quận 5, TP.HCM",
            "latitude": 10.7769,
            "longitude": 106.7009,
            "phone": "028-8765-4321",
            "email": "hcm@honda.com.vn",
            "website": "www.honda.com.vn",
            "brands": json.dumps(["Honda"]),
            "offers": json.dumps(["Giảm 30 triệu", "Tặng phụ kiện", "Bảo dưỡng miễn phí", "Lãi suất ưu đãi"])
        },
        {
            "name": "Toyota Center Hà Nội",
            "address": "789 Đường Giải Phóng, Hai Bà Trưng, Hà Nội",
            "latitude": 21.0175,
            "longitude": 105.8369,
            "phone": "024-9876-5432",
            "email": "hanoi@toyota.com.vn",
            "website": "www.toyota.com.vn",
            "brands": json.dumps(["Toyota"]),
            "offers": json.dumps(["Giảm 40 triệu", "Tặng bảo hiểm", "Lãi suất 0%", "Bảo dưỡng 5 năm"])
        },
        {
            "name": "Toyota Center TP.HCM",
            "address": "321 Đường Cách Mạng Tháng 8, Quận 10, TP.HCM",
            "latitude": 10.7626,
            "longitude": 106.6602,
            "phone": "028-1234-9876",
            "email": "hcm@toyota.com.vn",
            "website": "www.toyota.com.vn",
            "brands": json.dumps(["Toyota"]),
            "offers": json.dumps(["Giảm 35 triệu", "Tặng phụ kiện cao cấp", "Lãi suất ưu đãi", "Bảo hành mở rộng"])
        },
        {
            "name": "Mazda Center Hà Nội",
            "address": "555 Đường Lê Văn Lương, Thanh Xuân, Hà Nội",
            "latitude": 21.0031,
            "longitude": 105.8201,
            "phone": "024-5555-1234",
            "email": "hanoi@mazda.com.vn",
            "website": "www.mazda.com.vn",
            "brands": json.dumps(["Mazda"]),
            "offers": json.dumps(["Giảm 25 triệu", "Tặng bảo hiểm", "Lãi suất 0%", "Tặng phụ kiện Mazda"])
        },
        {
            "name": "Hyundai Center TP.HCM",
            "address": "777 Đường Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
            "latitude": 10.7769,
            "longitude": 106.7009,
            "phone": "028-7777-8888",
            "email": "hcm@hyundai.com.vn",
            "website": "www.hyundai.com.vn",
            "brands": json.dumps(["Hyundai"]),
            "offers": json.dumps(["Giảm 20 triệu", "Tặng bảo hiểm", "Lãi suất ưu đãi", "Bảo dưỡng miễn phí"])
        }
    ]
    
    print("Seeding showrooms data...")
    for showroom_data in showrooms_data:
        showroom = Showroom(**showroom_data)
        db.session.add(showroom)
    
    db.session.commit()
    print(f"✅ Added {len(showrooms_data)} showrooms")

def seed_users():
    """Seed sample users data"""
    users_data = [
        {
            "email": "demo@example.com",
            "name": "Nguyễn Văn Demo",
            "phone": "0123456789",
            "preferences": json.dumps({
                "budget_range": "500-1000",
                "preferred_segment": "sedan",
                "fuel_type": "petrol"
            })
        },
        {
            "email": "test@example.com",
            "name": "Trần Thị Test",
            "phone": "0987654321",
            "preferences": json.dumps({
                "budget_range": "800-1200",
                "preferred_segment": "suv",
                "fuel_type": "hybrid"
            })
        }
    ]
    
    print("Seeding users data...")
    for user_data in users_data:
        user = User(**user_data)
        db.session.add(user)
    
    db.session.commit()
    print(f"✅ Added {len(users_data)} users")

def main():
    """Main function to seed all data"""
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Clear existing data
        print("🗑️ Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Seed data
        seed_cars()
        seed_showrooms()
        seed_users()
        
        print("🎉 Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Cars: {Car.query.count()}")
        print(f"   - Showrooms: {Showroom.query.count()}")
        print(f"   - Users: {User.query.count()}")

if __name__ == "__main__":
    main()


