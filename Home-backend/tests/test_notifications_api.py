import sys
import os
# Ensure app can be imported
sys.path.append(os.getcwd())

import pytest
from fastapi.testclient import TestClient
from main import app
# from app.infrastructure.database import init_databases, close_databases
# from app.models.notification import Notification, NotificationCategory

client = TestClient(app)

def test_read_notifications():
    user_id = 101 # Use the ID we verified earlier
    
    print(f"Testing API for user_id={user_id}")
    
    with TestClient(app) as client:
        # 1. Get Notifications
        response = client.get(f"/api/v1/notifications/?user_id={user_id}")
        if response.status_code != 200:
             print(f"GET / failed: {response.text}")
        assert response.status_code == 200
        data = response.json()
        print(f"GET /notifications: {len(data)} items")
        
        if len(data) > 0:
            print(f"Sample: {data[0]}")
            notif_id = data[0]['id']
            
            # 2. Mark one as read
            response = client.put(f"/api/v1/notifications/{notif_id}/read?user_id={user_id}")
            if response.status_code != 200:
                 print(f"PUT /read failed: {response.text}")
            assert response.status_code == 200
            assert response.json()['is_read'] == True
            print(f"Marked {notif_id} as read.")
            
        # 3. Get Unread Count
        response = client.get(f"/api/v1/notifications/unread-count?user_id={user_id}")
        assert response.status_code == 200
        print(f"Unread Count: {response.json()}")

        # 4. Mark All Read
        response = client.put(f"/api/v1/notifications/read-all?user_id={user_id}")
        assert response.status_code == 200
        print("Marked all as read.")

if __name__ == "__main__":
    try:
        test_read_notifications()
        print("API Tests Passed!")
    except Exception as e:
        print(f"API Test Failed: {e}")
        # import traceback
        # traceback.print_exc()
