#!/bin/bash

ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTczOTA5NjYyMCwianRpIjoiNzhjODU0YmItZGI5Mi00YjUwLWI2Y2UtYTc5NTYwNjllMDM1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6InRlc3RAZXhhbXBsZS5jb20iLCJuYmYiOjE3MzkwOTY2MjAsImNzcmYiOiJjZGEzODUwNy0xYzQwLTQ1ZTQtOWYzYS0yODhkOWMxNjA5N2EiLCJleHAiOjE3MzkxMDAyMjB9.wyAiVakMlRHWKCzHhVy0a-47x2jAjNpXoxJp8snFYng"

echo "🔍 Using Token: $ACCESS_TOKEN"

echo "🔄 Running API Tests..."

echo "📌 Testing Portfolio Tracking..."
curl -X GET http://127.0.0.1:5000/portfolio/track \
-H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

echo "📌 Checking Historical Portfolio Data..."
curl -X GET http://127.0.0.1:5000/portfolio/history \
-H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

echo "✅ All Tests Complete!"



