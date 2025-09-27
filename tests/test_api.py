import pytest
import json
from app import app, db
from models import User, Meeting, Task

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_user():
    """Create test user"""
    user = User(
        id='test-user-123',
        name='Test User',
        email='test@example.com',
        role='user'
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_meeting(test_user):
    """Create test meeting"""
    meeting = Meeting(
        id='test-meeting-123',
        title='Test Meeting',
        transcript='This is a test meeting transcript.',
        user_id=test_user.id,
        status='transcribed'
    )
    db.session.add(meeting)
    db.session.commit()
    return meeting

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_upload_meeting(client, test_user):
    """Test meeting upload endpoint"""
    # This would require actual file upload in real test
    # For now, just test the endpoint exists
    response = client.post('/api/upload')
    assert response.status_code == 400  # No file provided

def test_get_meeting(client, test_meeting):
    """Test get meeting endpoint"""
    response = client.get(f'/api/meeting/{test_meeting.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['meeting']['id'] == test_meeting.id
    assert data['meeting']['title'] == 'Test Meeting'

def test_get_user_meetings(client, test_user, test_meeting):
    """Test get user meetings endpoint"""
    response = client.get(f'/api/meetings/user/{test_user.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['meetings']) == 1
    assert data['meetings'][0]['id'] == test_meeting.id

def test_create_task(client, test_user, test_meeting):
    """Test create task endpoint"""
    task_data = {
        'name': 'Test Task',
        'description': 'Test task description',
        'meeting_id': test_meeting.id,
        'user_id': test_user.id,
        'category': 'action-item',
        'priority': 'high'
    }
    
    response = client.post('/api/tasks', 
                          data=json.dumps(task_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['task']['name'] == 'Test Task'

def test_get_user_tasks(client, test_user):
    """Test get user tasks endpoint"""
    response = client.get(f'/api/tasks/user/{test_user.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'tasks' in data
    assert 'statistics' in data

def test_notification_settings(client, test_user):
    """Test notification settings endpoint"""
    response = client.get(f'/api/notify/settings/user/{test_user.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'settings' in data
