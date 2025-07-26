import requests
import json
import pytest
from datetime import datetime

# Test manifest with different file types and dependencies
test_manifest = {
    "id": "test-manifest-001",
    "creationTimeStamp": datetime.now().isoformat(),
    "manifestTemplate": "v1.0",
    "processType": "DataImport",
    "processName": "Test Multi-File Import",
    "processDate": datetime.now().strftime("%Y-%m-%d"),
    "fileTypesToProcess": [
        {
            "stepID": "step-1",
            "interfaceType": "File_Thomson",
            "sourceLocationOld": "tests/fixtures/data/old/thomson1.thomson",
            "sourceLocationNew": "tests/fixtures/data/new/thomson1.thomson",
            "prerequisites": []
        },
        {
            "stepID": "step-2",
            "interfaceType": "File_Reuters",
            "sourceLocationOld": "tests/fixtures/data/old/reuters1.reuters",
            "sourceLocationNew": "tests/fixtures/data/new/reuters1.reuters",
            "prerequisites": []
        },
        {
            "stepID": "step-3",
            "interfaceType": "File_Thomson",
            "sourceLocationOld": "tests/fixtures/data/old/thomson2.thomson",
            "sourceLocationNew": "tests/fixtures/data/new/thomson2.thomson",
            "prerequisites": [{"stepId": "step-1"}]
        },
        {
            "stepID": "step-4",
            "interfaceType": "File_Reuters",
            "sourceLocationOld": "tests/fixtures/data/old/reuters2.reuters",
            "sourceLocationNew": "tests/fixtures/data/new/reuters2.reuters",
            "prerequisites": [{"stepId": "step-2"}, {"stepId": "step-3"}]
        }
    ]
}

def test_supported_types():
    """Test getting supported file types"""
    print("\n=== Testing Supported Types Endpoint ===")
    response = requests.get("http://localhost:8000/supported-types")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_manifest_execution():
    """Test manifest execution"""
    print("\n=== Testing Manifest Execution ===")
    print(f"Sending manifest with {len(test_manifest['fileTypesToProcess'])} steps")
    
    response = requests.post(
        "http://localhost:8000/execute-manifest",
        json=test_manifest
    )
    
    print(f"Status Code: {response.status_code}")
    result = response.json()
    
    print(f"\nExecution Summary:")
    print(f"- Manifest ID: {result['manifestId']}")
    print(f"- Process Name: {result['processName']}")
    print(f"- Total Steps: {result['totalSteps']}")
    print(f"- Executed Steps: {result['executedSteps']}")
    print(f"- Success: {result['success']}")
    
    print(f"\nStep Results:")
    for step_result in result['results']:
        print(f"\n- Step ID: {step_result['stepId']}")
        print(f"  Status: {step_result['status']}")
        if 'result' in step_result:
            print(f"  Loader: {step_result['result']['loader']}")
            print(f"  File: {step_result['result']['file_path']}")

def test_invalid_file_type():
    """Test with invalid file type"""
    print("\n=== Testing Invalid File Type ===")
    invalid_manifest = {
        **test_manifest,
        "id": "test-invalid-001",
        "fileTypesToProcess": [
            {
                "stepID": "invalid-step",
                "interfaceType": "File_Unknown",
                "sourceLocationOld": "tests/fixtures/data/old/unknown.xyz",
                "sourceLocationNew": "tests/fixtures/data/new/unknown.xyz",
                "prerequisites": []
            }
        ]
    }
    
    response = requests.post(
        "http://localhost:8000/execute-manifest",
        json=invalid_manifest
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("Starting DAG Execution Tests")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("Run with: uvicorn app:app --reload")
    
    try:
        # Check if server is running
        response = requests.get("http://localhost:8000/")
        print(f"\nServer is running: {response.json()['message']}")
        
        # Run tests
        test_supported_types()
        test_manifest_execution()
        test_invalid_file_type()
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server. Make sure it's running with:")
        print("  uvicorn app:app --reload")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    main()