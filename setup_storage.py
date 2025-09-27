#!/usr/bin/env python3
"""
Set up file storage with sample files
"""

import os
import shutil
from pathlib import Path

def setup_file_storage():
    try:
        print("🚀 Setting up file storage...")
        
        # Create upload directories
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        meetings_dir = upload_dir / "meetings"
        meetings_dir.mkdir(exist_ok=True)
        
        audio_dir = upload_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        print("✅ Created upload directories")
        
        # Create sample audio files (dummy files for testing)
        sample_files = [
            {
                'name': 'weekly_standup_2024.wav',
                'path': meetings_dir / 'weekly_standup_2024.wav',
                'size': 2048576  # 2MB
            },
            {
                'name': 'project_planning.wav',
                'path': meetings_dir / 'project_planning.wav',
                'size': 1536000  # 1.5MB
            },
            {
                'name': 'client_review.wav',
                'path': meetings_dir / 'client_review.wav',
                'size': 3072000  # 3MB
            }
        ]
        
        for file_info in sample_files:
            # Create a dummy file with the specified size
            with open(file_info['path'], 'wb') as f:
                f.write(b'\x00' * file_info['size'])
            print(f"✅ Created sample file: {file_info['name']} ({file_info['size']} bytes)")
        
        # Create a sample transcript file
        transcript_content = """Meeting Transcript - Weekly Team Standup
Date: 2024-09-27
Duration: 30 minutes
Participants: 5

John: Good morning everyone. Let's start with our weekly standup. I've been working on the frontend components and I'm about 80% complete with the main dashboard.

Sarah: Hi team. I've finished the backend API development and it's ready for testing. All endpoints are working correctly.

Mike: I've been reviewing the database queries and I think we need to optimize some of them for better performance.

Lisa: I've completed the user authentication module and it's ready for integration.

Tom: I've been working on the documentation and it's up to date with all the recent changes.

John: Great progress everyone. For next week, I'll focus on completing the remaining frontend components.

Sarah: I'll start working on the API testing and documentation.

Mike: I'll work on optimizing the database queries we discussed.

Lisa: I'll help with the frontend integration of the authentication module.

Tom: I'll continue updating the documentation as we make progress.

Meeting concluded at 10:30 AM.
"""
        
        transcript_file = meetings_dir / 'weekly_standup_transcript.txt'
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript_content)
        print(f"✅ Created transcript file: weekly_standup_transcript.txt")
        
        # Create a sample configuration file
        config_content = """# Meeting AI Configuration
STORAGE_TYPE=local
MAX_FILE_SIZE=500MB
ALLOWED_FORMATS=wav,mp3,mp4,m4a
UPLOAD_DIR=uploads
"""
        
        config_file = Path("storage_config.txt")
        with open(config_file, 'w') as f:
            f.write(config_content)
        print(f"✅ Created storage configuration file")
        
        # Create a README for the uploads directory
        readme_content = """# Uploads Directory

This directory contains uploaded meeting files and generated content.

## Structure:
- `meetings/` - Meeting audio files and transcripts
- `audio/` - Processed audio files
- `transcripts/` - Generated transcripts
- `tasks/` - Extracted task files

## File Types:
- Audio: .wav, .mp3, .mp4, .m4a
- Text: .txt, .md
- Documents: .pdf, .docx

## Sample Files:
- weekly_standup_2024.wav (2MB)
- project_planning.wav (1.5MB)
- client_review.wav (3MB)
- weekly_standup_transcript.txt
"""
        
        readme_file = upload_dir / 'README.md'
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        print(f"✅ Created README file")
        
        # Verify directory structure
        print(f"📁 Directory structure:")
        print(f"   {upload_dir.absolute()}/")
        print(f"   ├── meetings/")
        print(f"   ├── audio/")
        print(f"   └── README.md")
        
        # List files
        print(f"📄 Files created:")
        for file_path in upload_dir.rglob("*"):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"   - {file_path.name} ({size:,} bytes)")
        
        print("🎉 File storage setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up file storage: {e}")
        return False

if __name__ == '__main__':
    setup_file_storage()
