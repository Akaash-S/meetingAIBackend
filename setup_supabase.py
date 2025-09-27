#!/usr/bin/env python3
"""
Supabase setup script for file storage
"""
import os
import sys
from dotenv import load_dotenv

def test_supabase_connection():
    """Test Supabase connection"""
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        
        if not url or not key:
            print("❌ Supabase URL or key not configured")
            return False
        
        print(f"🔗 Testing connection to: {url}")
        
        supabase: Client = create_client(url, key)
        
        # Test connection by listing buckets
        result = supabase.storage.list_buckets()
        
        if hasattr(result, 'error') and result.error:
            print(f"❌ Supabase connection failed: {result.error}")
            return False
        
        print("✅ Connected to Supabase successfully")
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def create_storage_bucket():
    """Create storage bucket for meeting files"""
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        bucket_name = os.getenv('SUPABASE_BUCKET', 'meeting-files')
        
        supabase: Client = create_client(url, key)
        
        # Check if bucket exists
        buckets = supabase.storage.list_buckets()
        existing_buckets = [bucket.name for bucket in buckets] if buckets else []
        
        if bucket_name in existing_buckets:
            print(f"✅ Bucket '{bucket_name}' already exists")
            return True
        
        # Create bucket
        print(f"📦 Creating bucket '{bucket_name}'...")
        result = supabase.storage.create_bucket(bucket_name, public=True)
        
        if hasattr(result, 'error') and result.error:
            print(f"❌ Error creating bucket: {result.error}")
            return False
        
        print(f"✅ Bucket '{bucket_name}' created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        return False

def test_file_upload():
    """Test file upload to Supabase"""
    try:
        from supabase import create_client, Client
        import io
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        bucket_name = os.getenv('SUPABASE_BUCKET', 'meeting-files')
        
        supabase: Client = create_client(url, key)
        
        # Create a test file
        test_content = b"Test file content for meeting assistant"
        test_file = io.BytesIO(test_content)
        test_file.name = "test.txt"
        test_file.content_type = "text/plain"
        
        # Upload test file
        print("📤 Testing file upload...")
        result = supabase.storage.from_(bucket_name).upload(
            "test-upload.txt",
            test_file.read(),
            file_options={"content-type": "text/plain"}
        )
        
        if hasattr(result, 'error') and result.error:
            print(f"❌ Upload test failed: {result.error}")
            return False
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url("test-upload.txt")
        print(f"✅ Test file uploaded successfully: {public_url}")
        
        # Clean up test file
        supabase.storage.from_(bucket_name).remove(["test-upload.txt"])
        print("🧹 Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Supabase for file storage...")
    
    # Load environment variables
    load_dotenv()
    
    # Test connection
    if not test_supabase_connection():
        print("\n❌ Setup failed: Could not connect to Supabase")
        print("Please check your SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file")
        return False
    
    # Create bucket
    if not create_storage_bucket():
        print("\n❌ Setup failed: Could not create storage bucket")
        return False
    
    # Test file upload
    if not test_file_upload():
        print("\n❌ Setup failed: File upload test failed")
        return False
    
    print("\n🎉 Supabase setup completed successfully!")
    print("\nYour backend is now ready to store files in Supabase!")
    print("\nNext steps:")
    print("1. Set up your AI API keys (RapidAPI, Gemini)")
    print("2. Configure email settings (SendGrid)")
    print("3. Run: python run.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
