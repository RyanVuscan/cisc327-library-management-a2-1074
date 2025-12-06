import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Route tests

def test_catalog_route(client):
    response = client.get('/catalog')
    assert response.status_code == 200

def test_add_book_get_route(client):
    response = client.get('/add_book')
    assert response.status_code == 200

def test_add_book_post_route(client):
    response = client.post('/add_book', data={
        'title': 'New Book',
        'author': 'Author',
        'isbn': '1111111111111',
        'total_copies': '2'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_add_book_post_bad_copies(client):
    response = client.post('/add_book', data={
        'title': 'Book',
        'author': 'Author',
        'isbn': '2222222222222',
        'total_copies': 'bad'
    })
    assert response.status_code == 200

def test_borrow_route(client):
    response = client.post('/borrow', data={
        'patron_id': '333333',
        'book_id': '1'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_borrow_bad_book_id(client):
    response = client.post('/borrow', data={
        'patron_id': '333333',
        'book_id': 'notanumber'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_return_get_route(client):
    response = client.get('/return')
    assert response.status_code == 200

def test_return_post_route(client):
    response = client.post('/return', data={
        'patron_id': '444444',
        'book_id': '1'
    })
    assert response.status_code == 200

def test_return_bad_book_id(client):
    response = client.post('/return', data={
        'patron_id': '444444',
        'book_id': 'notanumber'
    })
    assert response.status_code == 200

def test_search_route(client):
    response = client.get('/search')
    assert response.status_code == 200

def test_search_with_query(client):
    response = client.get('/search?q=gatsby&type=title')
    assert response.status_code == 200

def test_late_fee_api(client):
    response = client.get('/api/late_fee/123456/3')
    assert response.status_code == 200

def test_search_api(client):
    response = client.get('/api/search?q=gatsby&type=title')
    assert response.status_code == 200
