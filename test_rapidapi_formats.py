#!/usr/bin/env python3
"""
Test Different RapidAPI Request Formats
This script tests various request formats to find the correct one.
"""

import os
import requests
from dotenv import load_dotenv

def test_different_formats():
    """Test different request formats for RapidAPI"""
    print("Testing Different RapidAPI Request Formats")
    print("=" * 45)
    
    # Load environment variables
    load_dotenv()
    
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = 'speech-to-text-ai.p.rapidapi.com'
    
    if not rapidapi_key:
        print("ERROR: RAPIDAPI_KEY not found")
        return False
    
    # Test different formats
    test_cases = [
        {
            "name": "Format 1: JSON with audio data",
            "headers": {
                'x-rapidapi-key': rapidapi_key,
                'x-rapidapi-host': rapidapi_host,
                'Content-Type': 'application/json'
            },
            "payload": {
                "audio": "base64_encoded_audio_data",
                "language": "en"
            },
            "method": "json"
        },
        {
            "name": "Format 2: Form data with file",
            "headers": {
                'x-rapidapi-key': rapidapi_key,
                'x-rapidapi-host': rapidapi_host
            },
            "files": {
                'audio': ('test.wav', b'fake_audio_data', 'audio/wav')
            },
            "method": "files"
        },
        {
            "name": "Format 3: URL encoded with different params",
            "headers": {
                'x-rapidapi-key': rapidapi_key,
                'x-rapidapi-host': rapidapi_host,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            "payload": "audio=base64_data&language=en",
            "method": "data"
        },
        {
            "name": "Format 4: URL encoded with file parameter",
            "headers": {
                'x-rapidapi-key': rapidapi_key,
                'x-rapidapi-host': rapidapi_host,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            "payload": "file=base64_data&lang=en",
            "method": "data"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 50)
        
        try:
            if test_case['method'] == 'json':
                response = requests.post(
                    f'https://{rapidapi_host}/transcribe',
                    headers=test_case['headers'],
                    json=test_case['payload'],
                    timeout=10
                )
            elif test_case['method'] == 'files':
                response = requests.post(
                    f'https://{rapidapi_host}/transcribe',
                    headers=test_case['headers'],
                    files=test_case['files'],
                    timeout=10
                )
            elif test_case['method'] == 'data':
                response = requests.post(
                    f'https://{rapidapi_host}/transcribe',
                    headers=test_case['headers'],
                    data=test_case['payload'],
                    timeout=10
                )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS: This format works!")
                print(f"Response: {response.text[:200]}...")
                return test_case
            elif response.status_code == 400:
                print("Bad Request - Wrong format")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error: {response.text[:200]}...")
            elif response.status_code == 401:
                print("Unauthorized - API key issue")
            elif response.status_code == 403:
                print("Forbidden - Access denied")
            else:
                print(f"Unexpected status: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def test_with_sample_audio():
    """Test with a real audio file URL"""
    print("\n" + "=" * 50)
    print("Testing with Sample Audio URL")
    print("=" * 50)
    
    load_dotenv()
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = 'speech-to-text-ai.p.rapidapi.com'
    
    # Test with the sample URL from your original example
    sample_url = "https://cdn.openai.com/whisper/draft-20220913a/micro-machines.wav"
    
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': rapidapi_host,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Try different parameter names
    test_params = [
        f"url={sample_url}&lang=en&task=transcribe",
        f"audio_url={sample_url}&language=en",
        f"file_url={sample_url}&lang=en",
        f"source={sample_url}&language=en&task=transcribe"
    ]
    
    for i, params in enumerate(test_params, 1):
        print(f"\n{i}. Testing: {params}")
        try:
            response = requests.post(
                f'https://{rapidapi_host}/transcribe',
                headers=headers,
                data=params,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("SUCCESS!")
                print(f"Response: {response.text}")
                return params
            else:
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def main():
    """Main test function"""
    print("RapidAPI Format Discovery Test")
    print("=" * 35)
    
    # Test different formats
    working_format = test_different_formats()
    
    if not working_format:
        # Test with sample audio
        working_params = test_with_sample_audio()
        
        if working_params:
            print(f"\nSUCCESS: Found working format!")
            print(f"Working parameters: {working_params}")
        else:
            print("\nNo working format found. Check API documentation.")
    else:
        print(f"\nSUCCESS: Found working format: {working_format['name']}")

if __name__ == '__main__':
    main()
