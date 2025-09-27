# Routes package
from .upload import upload_bp
from .transcribe import transcribe_bp
from .extract import extract_bp
from .meeting import meeting_bp
from .task import task_bp
from .notify import notify_bp

__all__ = ['upload_bp', 'transcribe_bp', 'extract_bp', 'meeting_bp', 'task_bp', 'notify_bp']
