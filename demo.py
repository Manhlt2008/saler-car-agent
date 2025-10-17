#!/usr/bin/env python3
"""
Demo script để test AI Car Agent
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_chat():
    """Test chat functionality"""
    print("\n💬 Testing chat functionality...")
    
    test_messages = [
        "Xin chào! Tôi muốn mua xe dưới 1 tỷ",
        "Tôi cần xe 7 chỗ",
        "Tôi muốn xe SUV",
        "So sánh các xe này cho tôi",
        "Tôi chọn xe số 1",
        "Email của tôi là demo@example.com"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test message {i}: {message}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:100]}...")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Wait between requests

def test_cars():
    """Test cars endpoint"""
    print("\n🚗 Testing cars endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/cars")
        if response.status_code == 200:
            cars = response.json()
            print(f"✅ Found {len(cars)} cars")
            for car in cars[:3]:  # Show first 3 cars
                print(f"   - {car['brand']} {car['name']}: {car['price_min']:,} - {car['price_max']:,} VNĐ")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_showrooms():
    """Test showrooms endpoint"""
    print("\n🏢 Testing showrooms endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/showrooms")
        if response.status_code == 200:
            showrooms = response.json()
            print(f"✅ Found {len(showrooms)} showrooms")
            for showroom in showrooms[:3]:  # Show first 3 showrooms
                print(f"   - {showroom['name']}: {showroom['address']}")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_nearby_showrooms():
    """Test nearby showrooms endpoint"""
    print("\n📍 Testing nearby showrooms endpoint...")
    try:
        # Test with Hanoi coordinates
        data = {
            "latitude": 21.0285,
            "longitude": 105.8542,
            "radius": 10000  # 10km
        }
        
        response = requests.post(
            f"{BASE_URL}/api/nearby-showrooms",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['count']} nearby showrooms")
            for showroom in result['showrooms'][:3]:
                print(f"   - {showroom['name']}: {showroom['address']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_send_quote():
    """Test send quote endpoint"""
    print("\n📧 Testing send quote endpoint...")
    try:
        data = {
            "email": "demo@example.com",
            "car_id": 1,
            "name": "Demo User"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/send-quote",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Quote sent successfully: {result['message']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main demo function"""
    print("🚀 AI Car Agent Demo")
    print("=" * 50)
    
    # Test all endpoints
    test_health()
    test_cars()
    test_showrooms()
    test_nearby_showrooms()
    test_chat()
    test_send_quote()
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n📋 To run the full application:")
    print("1. Start backend: cd backend && python app.py")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000")

if __name__ == "__main__":
    main()


