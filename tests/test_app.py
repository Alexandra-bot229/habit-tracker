import pytest
import tempfile
import os
from app import app
from database import init_db, add_user, get_user

@pytest.fixture
def client():
    app.config['TESTING'] = True
    import database
    database.DATABASE = tempfile.mktemp(suffix='.db')
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    
    if os.path.exists(database.DATABASE):
        os.unlink(database.DATABASE)

def test_index_page_redirects_to_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_login_page_returns_200(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_register_page_returns_200(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_register_new_user(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    user = get_user('testuser', 'testpass')
    assert user is not None

def test_login_success(client):
    client.post('/register', data={'username': 'logintest', 'password': '123'})
    response = client.post('/login', data={
        'username': 'logintest',
        'password': '123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'logintest' in response.data

def test_login_fail(client):
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpass'
    })
    assert response.status_code == 200

def test_add_habit_after_login(client):
    client.post('/register', data={'username': 'habituser', 'password': '123'})
    client.post('/login', data={'username': 'habituser', 'password': '123'})
    
    response = client.post('/add', data={
        'name': 'Test Habit',
        'description': 'Test Description',
        'target_count': 1
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Habit' in response.data

def test_404_error(client):
    response = client.get('/nonexistent_page_12345')
    assert response.status_code == 404

def test_empty_habit_field(client):
    client.post('/register', data={'username': 'emptyuser', 'password': '123'})
    client.post('/login', data={'username': 'emptyuser', 'password': '123'})
    
    response = client.post('/add', data={
        'name': '',
        'description': 'Something',
        'target_count': 1
    }, follow_redirects=True)
    
    assert response.status_code == 200

def test_logout(client):
    client.post('/register', data={'username': 'logoutuser', 'password': '123'})
    client.post('/login', data={'username': 'logoutuser', 'password': '123'})
    
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200