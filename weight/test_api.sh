#!/bin/bash

# Test batch-weight endpoint
echo "Testing batch-weight endpoint..."
curl -X POST http://localhost:5000/batch-weight -H "Content-Type: application/json" -d '{"file": "containers1.csv"}'
curl -X POST http://localhost:5000/batch-weight -H "Content-Type: application/json" -d '{"file": "containers2.csv"}'

# Test weight endpoint (truck entering - weigh in)
echo -e "\nTesting weight endpoint #1 (direction: in)..."
curl -X POST http://localhost:5000/weight \
     -H "Content-Type: application/json" \
     -d '{
         "direction": "in",
         "truck": "truck1",
         "containers": "C-35434,K-4109",
         "weight": 15000,
         "unit": "kg",
         "force": false,
         "produce": "orange"
     }'

echo -e "\nTesting weight endpoint #2 (direction: in)..."
curl -X POST http://localhost:5000/weight \
     -H "Content-Type: application/json" \
     -d '{
         "direction": "in",
         "truck": "truck2",
         "containers": "C-35434,K-4109",
         "weight": 15000,
         "unit": "kg",
         "force": false,
         "produce": "orange"
     }'

# Test weight endpoint (truck leaving - weigh out)
echo -e "\nTesting weight endpoint #1 (direction: out)..."
curl -X POST http://localhost:5000/weight \
     -H "Content-Type: application/json" \
     -d '{
         "direction": "out",
         "truck": "truck1",
         "containers": "C-35434,K-4109",
         "weight": 12000,
         "unit": "kg",
         "force": false,
         "produce": "orange"
     }'

echo -e "\nTesting weight endpoint #2 (direction: out)..."
curl -X POST http://localhost:5000/weight \
     -H "Content-Type: application/json" \
     -d '{
         "direction": "out",
         "truck": "truck2",
         "containers": "C-35434,K-4109",
         "weight": 12000,
         "unit": "kg",
         "force": false,
         "produce": "orange"
     }'

curl -X POST http://localhost:5000/weight \
     -H "Content-Type: application/json" \
     -d '{
         "direction": "in",
         "truck": "truck3",
         "containers": "C-35434,K-4109",
         "weight": 15000,
         "unit": "kg",
         "force": false,
         "produce": "orange"
     }'

curl -X POST http://localhost:5000/weight \
     -H "Content-Type: application/json" \
     -d '{
         "direction": "in",
         "truck": "truck3",
         "containers": "C-35434,K-4109",
         "weight": 12345,
         "unit": "kg",
         "force": true,
         "produce": "orange"
     }'

curl -X POST http://localhost:5000/weight \
     -H "Content-Type: application/json" \
     -d '{
         "direction": "none",
         "containers": "A-123456789",
         "weight": 123,
         "unit": "kg",
         "produce": "orange"
     }'
