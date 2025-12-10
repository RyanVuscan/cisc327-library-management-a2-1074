import pytest
from playwright.sync_api import Page, expect
import time
import threading
import random


@pytest.fixture(scope="module")
def flask_server():

    # Setup
    from app import create_app
    app = create_app()
    def run_server():
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    
    # Separate threading
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    
    yield "http://localhost:5000"


def test_add_book_flow(page: Page, flask_server):
    # Test #1: Adding a new book to the catalog

    base_url = flask_server
    
    # Generate unique ISBN so test can run multiple times
    unique_isbn = f"9{random.randint(100000000000, 999999999999)}"
    
    # Home page
    page.goto(base_url)

    # New book
    page.click("text=Add New Book")

    # Fill form
    page.fill("#title", "Test Book from E2E")
    page.fill("#author", "Test Author")
    page.fill("#isbn", unique_isbn)
    page.fill("#total_copies", "3")
    
    # Click submit button
    page.click("button[type='submit']")
    
    # Verification
    expect(page.locator(".flash-success")).to_contain_text("successfully added")
    expect(page.locator("table")).to_contain_text("Test Book from E2E")
    expect(page.locator("table")).to_contain_text(unique_isbn)


def test_borrow_book_flow(page: Page, flask_server):
    # Test #2: Borrow a book from the catalog

    base_url = flask_server
    
    # Reset page
    page.goto(f"{base_url}/catalog")
    
    # Input patron ID
    patron_input = page.locator("input[name='patron_id']").first
    patron_input.fill("111111")
    
    # Borrow book
    borrow_button = page.locator("button.btn-success").first
    borrow_button.click()
    
    # Verification
    expect(page.locator(".flash-success")).to_be_visible()
    expect(page.locator(".flash-success")).to_contain_text("Due date")
