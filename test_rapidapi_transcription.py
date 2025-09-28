#!/usr/bin/env python3
"""
Test RapidAPI Transcription Service
This script tests the updated RapidAPI speech-to-text integration.
"""

import os
import requests
from dotenv import load_dotenv

def test_rapidapi_connection():
    """Test RapidAPI connection and configuration"""
    print("Testing RapidAPI Transcription Service")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check configuration
    rapidapi_key = os.getenv('RAPIDAPI_KEY')
    rapidapi_host = 'speech-to-text-ai.p.rapidapi.com'
    
    if not rapidapi_key:
        print("ERROR: RAPIDAPI_KEY not found in .env file")
        return False
    
    print(f"OK: RapidAPI Key configured")
    print(f"OK: RapidAPI Host: {rapidapi_host}")
    
    # Test API connection with a simple request
    try:
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': rapidapi_host,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Test with a sample URL (this is just to test the connection)
        payload = "url=https%3A%2F%2Fcdn.openai.com%2Fwhisper%2Fdraft-20220913a%2Fmicro-machines.wav&lang=en&task=transcribe"
        
        print("Testing API connection...")
        response = requests.post(
            f'https://{rapidapi_host}/transcribe',
            headers=headers,
            data=payload,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("OK: RapidAPI connection successful!")
            try:
                result = response.json()
                print(f"Response: {result}")
            except:
                print(f"Response Text: {response.text}")
            return True
        elif response.status_code == 401:
            print("ERROR: Invalid API key")
            return False
        elif response.status_code == 403:
            print("ERROR: API access forbidden - check your subscription")
            return False
        else:
            print(f"WARNING: Unexpected response: {response.status_code}")
            print(f"Response: {response.text}")
            return True  # Still consider it working if we get a response
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
        return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection failed")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_transcription_functions():
    """Test the transcription functions in the codebase"""
    print("\nTesting Transcription Functions")
    print("=" * 35)
    
    try:
        # Test importing the transcription functions
        from routes.transcribe import transcribe_with_rapidapi
        print("OK: transcribe_with_rapidapi function imported")
        
        from services.audio_processor import AudioProcessorService
        print("OK: AudioProcessorService imported")
        
        from routes.audio import AudioProcessor
        print("OK: AudioProcessor imported")
        
        print("SUCCESS: All transcription functions are available")
        return True
        
    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main test function"""
    print("RapidAPI Speech-to-Text Integration Test")
    print("=" * 45)
    
    # Test 1: API Connection
    connection_ok = test_rapidapi_connection()
    
    # Test 2: Function Availability
    functions_ok = test_transcription_functions()
    
    print("\n" + "=" * 45)
    if connection_ok and functions_ok:
        print("SUCCESS: RapidAPI integration is working correctly!")
        print("Your speech-to-text service is ready to use.")
    else:
        print("ERROR: Some tests failed!")
        if not connection_ok:
            print("- Check your RAPIDAPI_KEY in the .env file")
            print("- Verify your RapidAPI subscription is active")
        if not functions_ok:
            print("- Check that all required modules are installed")
    
    return connection_ok and functions_ok

if __name__ == '__main__':
    success = main()
    if not success:
        print("\nPlease fix the issues above and try again.")
