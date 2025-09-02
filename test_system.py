#!/usr/bin/env python3
"""
System test script to validate all services are working correctly
"""
import requests
import json
import time
import sys
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(message):
    """Print test message"""
    print(f"{Colors.BLUE}🧪 {message}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.ENDC}")

def test_service_health(service_name, url):
    """Test if service is healthy"""
    print_test(f"Testing {service_name} health...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print_success(f"{service_name} is healthy")
            return True
        else:
            print_error(f"{service_name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"{service_name} is not accessible: {e}")
        return False

def test_erp_endpoints():
    """Test ERP service endpoints"""
    base_url = "http://localhost:3001/api/v1"
    tests = [
        ("Inventory items", f"{base_url}/inventory/items"),
        ("Inventory history", f"{base_url}/inventory/SKU001/history?days=30"),
        ("Budget expenses", f"{base_url}/finance/expenses?category=Marketing&days=30")
    ]
    
    results = []
    
    for test_name, url in tests:
        print_test(f"Testing {test_name}...")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if test_name == "Inventory items":
                    if "items" in data and len(data["items"]) > 0:
                        print_success(f"{test_name}: {len(data['items'])} items found")
                        results.append(True)
                    else:
                        print_error(f"{test_name}: No items in response")
                        results.append(False)
                
                elif test_name == "Inventory history":
                    if "history" in data and "sku" in data:
                        print_success(f"{test_name}: {len(data['history'])} records for {data['sku']}")
                        results.append(True)
                    else:
                        print_error(f"{test_name}: Invalid response structure")
                        results.append(False)
                
                elif test_name == "Budget expenses":
                    if "expenses" in data and "category" in data:
                        print_success(f"{test_name}: {len(data['expenses'])} expenses for {data['category']}")
                        results.append(True)
                    else:
                        print_error(f"{test_name}: Invalid response structure")
                        results.append(False)
            else:
                print_error(f"{test_name}: HTTP {response.status_code}")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print_error(f"{test_name}: Request failed - {e}")
            results.append(False)
    
    return all(results)

def test_prediction_endpoints():
    """Test prediction service endpoints"""
    base_url = "http://localhost:3002/api/v1"
    
    # Test health first
    print_test("Testing prediction service health...")
    if not test_service_health("Prediction Service", f"{base_url.replace('/api/v1', '')}/health"):
        return False
    
    # Test prediction types endpoint
    print_test("Testing prediction types endpoint...")
    try:
        response = requests.get(f"{base_url}/predict/types", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "prediction_types" in data:
                print_success(f"Prediction types: {len(data['prediction_types'])} types available")
            else:
                print_error("Invalid prediction types response")
                return False
        else:
            print_error(f"Prediction types endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Prediction types test failed: {e}")
        return False
    
    # Test actual predictions
    test_cases = [
        {
            "name": "Inventory Prediction",
            "payload": {
                "prediction_type": "inventory",
                "entity_id": "SKU001", 
                "time_horizon": 30
            }
        },
        {
            "name": "Budget Prediction",
            "payload": {
                "prediction_type": "budget",
                "entity_id": "Marketing",
                "time_horizon": 30
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print_test(f"Testing {test_case['name']}...")
        
        try:
            response = requests.post(
                f"{base_url}/predict",
                json=test_case['payload'],
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['predictions', 'insights', 'metadata', 'prediction_type', 'entity_id']
                
                if all(field in data for field in required_fields):
                    predictions = data['predictions']
                    insights = data['insights']
                    
                    print_success(f"{test_case['name']}: {len(predictions)} predictions, {len(insights)} insights")
                    
                    # Validate prediction structure
                    if predictions and all('date' in p and 'predicted_value' in p and 'confidence' in p for p in predictions):
                        print_success(f"   Prediction data structure is valid")
                        results.append(True)
                    else:
                        print_error(f"   Invalid prediction data structure")
                        results.append(False)
                else:
                    print_error(f"{test_case['name']}: Missing required fields in response")
                    print_warning(f"   Expected: {required_fields}")
                    print_warning(f"   Got: {list(data.keys())}")
                    results.append(False)
            else:
                print_error(f"{test_case['name']}: HTTP {response.status_code}")
                if response.text:
                    print_warning(f"   Response: {response.text}")
                results.append(False)
                
        except requests.exceptions.Timeout:
            print_error(f"{test_case['name']}: Request timed out (>30s)")
            results.append(False)
        except requests.exceptions.RequestException as e:
            print_error(f"{test_case['name']}: Request failed - {e}")
            results.append(False)
        except Exception as e:
            print_error(f"{test_case['name']}: Unexpected error - {e}")
            results.append(False)
    
    return all(results)

def test_integration():
    """Test end-to-end integration"""
    print_test("Testing end-to-end integration...")
    
    # Test full workflow: ERP -> Prediction -> Response
    try:
        # 1. Get inventory items from ERP
        erp_response = requests.get("http://localhost:3001/api/v1/inventory/items", timeout=10)
        if erp_response.status_code != 200:
            print_error("Failed to get inventory items from ERP")
            return False
        
        erp_data = erp_response.json()
        if not erp_data.get('items'):
            print_error("No inventory items found")
            return False
        
        # 2. Use first SKU for prediction
        first_sku = erp_data['items'][0]['sku']
        print_test(f"Using SKU {first_sku} for integration test...")
        
        # 3. Get prediction
        pred_response = requests.post(
            "http://localhost:3002/api/v1/predict",
            json={
                "prediction_type": "inventory",
                "entity_id": first_sku,
                "time_horizon": 15
            },
            timeout=30
        )
        
        if pred_response.status_code != 200:
            print_error("Failed to get prediction")
            return False
        
        pred_data = pred_response.json()
        
        # 4. Validate complete workflow
        if (pred_data.get('predictions') and 
            pred_data.get('insights') and 
            pred_data['entity_id'] == first_sku):
            print_success("End-to-end integration test passed")
            print_success(f"   Generated {len(pred_data['predictions'])} predictions")
            print_success(f"   Generated {len(pred_data['insights'])} insights") 
            return True
        else:
            print_error("Integration test failed - invalid prediction response")
            return False
            
    except Exception as e:
        print_error(f"Integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print(f"{Colors.BOLD}🧪 ERP Prediction System - Test Suite{Colors.ENDC}")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Test 1: Service Health Checks
    print(f"{Colors.BOLD}1. Service Health Checks{Colors.ENDC}")
    print("-" * 30)
    
    health_tests = [
        ("ERP Service", "http://localhost:3001/health"),
        ("Prediction Service", "http://localhost:3002/health")
    ]
    
    for service_name, url in health_tests:
        result = test_service_health(service_name, url)
        test_results.append(result)
    
    print()
    
    # Test 2: ERP Service Endpoints
    print(f"{Colors.BOLD}2. ERP Service Endpoints{Colors.ENDC}")
    print("-" * 30)
    
    erp_result = test_erp_endpoints()
    test_results.append(erp_result)
    print()
    
    # Test 3: Prediction Service Endpoints  
    print(f"{Colors.BOLD}3. Prediction Service Endpoints{Colors.ENDC}")
    print("-" * 30)
    
    pred_result = test_prediction_endpoints()
    test_results.append(pred_result)
    print()
    
    # Test 4: Integration Test
    print(f"{Colors.BOLD}4. End-to-End Integration{Colors.ENDC}")
    print("-" * 30)
    
    integration_result = test_integration()
    test_results.append(integration_result)
    print()
    
    # Summary
    print("=" * 60)
    print(f"{Colors.BOLD}📊 Test Summary{Colors.ENDC}")
    print("-" * 20)
    
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print_success(f"All tests passed! ({passed}/{total})")
        print_success("🎉 System is working correctly!")
        return 0
    else:
        print_error(f"Some tests failed ({passed}/{total})")
        print_warning("🔧 Please check the services and try again")
        return 1

if __name__ == "__main__":
    sys.exit(main())