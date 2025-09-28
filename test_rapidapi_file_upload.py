#!/usr/bin/env python3
"""
Test RapidAPI File Upload Format
This script tests the correct file upload format for RapidAPI.
"""

import os
import requests
from dotenv import load_dotenv

def test_file_upload_formats():
    """Test different file upload formats"""
    print("Testing RapidAPI File Upload Formats")
    print("=" * 40)
    
    load_dotenv()
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = 'speech-to-text-ai.p.rapidapi.com'
    
    if not rapidapi_key:
        print("ERROR: RAPIDAPI_KEY not found")
        return False
    
    # Create a small test audio file (fake data)
    test_audio_data = b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x08\x00\x00'
    
    # Test different file upload formats
    test_cases = [
        {
            "name": "Format 1: File with 'file' parameter",
            "files": {
                'file': ('test.wav', test_audio_data, 'audio/wav')
            },
            "data": {
                'language': 'en'
            }
        },
        {
            "name": "Format 2: File with 'audio' parameter",
            "files": {
                'audio': ('test.wav', test_audio_data, 'audio/wav')
            },
            "data": {
                'language': 'en'
            }
        },
        {
            "name": "Format 3: File with 'audioFile' parameter",
            "files": {
                'audioFile': ('test.wav', test_audio_data, 'audio/wav')
            },
            "data": {
                'language': 'en'
            }
        },
        {
            "name": "Format 4: File with 'upload' parameter",
            "files": {
                'upload': ('test.wav', test_audio_data, 'audio/wav')
            },
            "data": {
                'language': 'en'
            }
        },
        {
            "name": "Format 5: File only, no additional data",
            "files": {
                'file': ('test.wav', test_audio_data, 'audio/wav')
            },
            "data": {}
        }
    ]
    
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': rapidapi_host
    }
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f'https://{rapidapi_host}/transcribe',
                headers=headers,
                files=test_case['files'],
                data=test_case['data'],
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("SUCCESS: This format works!")
                print(f"Response: {response.text}")
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

def test_url_format():
    """Test URL format with correct parameter names"""
    print("\n" + "=" * 50)
    print("Testing URL Format with Different Parameter Names")
    print("=" * 50)
    
    load_dotenv()
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = 'speech-to-text-ai.p.rapidapi.com'
    
    sample_url = "https://cdn.openai.com/whisper/draft-20220913a/micro-machines.wav"
    
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': rapidapi_host,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Try different parameter names based on the error messages
    test_params = [
        # Based on error: "Either URL or file must be provided"
        f"url={sample_url}",
        f"file={sample_url}",
        f"url={sample_url}&language=en",
        f"file={sample_url}&language=en",
        # Try without language parameter
        f"url={sample_url}&lang=en",
        f"file={sample_url}&lang=en"
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
    print("RapidAPI Format Discovery - File Upload Test")
    print("=" * 50)
    
    # Test file upload formats
    working_format = test_file_upload_formats()
    
    if not working_format:
        # Test URL format
        working_params = test_url_format()
        
        if working_params:
            print(f"\nSUCCESS: Found working URL format!")
            print(f"Working parameters: {working_params}")
        else:
            print("\nNo working format found.")
            print("The API might require a different endpoint or format.")
    else:
        print(f"\nSUCCESS: Found working file upload format!")
        print(f"Working format: {working_format['name']}")

if __name__ == '__main__':
    main()
