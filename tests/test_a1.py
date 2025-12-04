import pytest
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,

)

def test_add_book_valid_input():
    """Test adding a book with valid input."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 5)
    
    assert success == True
    assert "successfully added" in message.lower()

def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message


# R1 Tests (non-AI)

def test_add_book_isbn_too_long():
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567823123123123123", 5)
    assert success is False

def test_add_book_num_int_check():
    success = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -4)
    assert success is False

def test_add_book_missing_entry():
    success = add_book_to_catalog("Test Book", "1234567890123", 2)
    assert success is False

def test_add_book_special_symbols():
    success = add_book_to_catalog("!@#$%^&*(-=)", "Test Author", "1234567890123", 1)
    assert success is True


# R3 Tests (non-AI)

def test_patron_id_too_long():
    success, message = borrow_book_by_patron("123123123", 1)
    assert success == False

def test_patron_id_non_digit():
    success = borrow_book_by_patron("abcdef", 2)
    assert success is False

def test_correct_borrow():
    success = borrow_book_by_patron("123456", 3)
    assert success is True

def test_book_id_non_digit():
    success = borrow_book_by_patron("123456", "xyz")
    assert success is False


# R4 Tests (non-AI)

def test_book_return_valid():
    borrow_book_by_patron("222222", 2)
    success, message = return_book_by_patron("222222", 2)
    assert success is True

def test_book_not_borrowed():
    success, message = return_book_by_patron("111111", 999)
    assert success is False

def test_invalid_patron_id():
    success, message = return_book_by_patron("abc123", 1)
    assert success is False
    
def test_book_not_in_database():
    success, message = return_book_by_patron("123456", 9999)
    assert success is False
    assert "Book not found" in message


# R5 Tests (non-AI)
def test_valid_input():
    result = calculate_late_fee_for_book("123456", 3)
    assert result["fee_amount"] >= 0

def test_invalid_patron():
    result = calculate_late_fee_for_book("abc", 2)
    assert result["fee_amount"] == 0

def test_invalid_book_id():
    result = calculate_late_fee_for_book("123456", 9999)
    assert result["fee_amount"] == 0.0

def test_zero_days_overdue():
    result = calculate_late_fee_for_book("123456", 3)
    assert result["days_overdue"] >= 0
    assert result["fee_amount"] >= 0.0

# R6 Tests (non-AI)
def test_title_search():
    result = search_books_in_catalog("gatsby", "title")
    assert type(result) == list

def test_no_match():
    result = search_books_in_catalog("RANDOM-STR", "title")
    assert result == []

def test_patrial_author_search():
    result = search_books_in_catalog("orw", "author")
    assert result != []


def test_isbn_match():
    result = search_books_in_catalog("9780451524935", "isbn")
    assert len(result) == 1

# R7 Tests (non-AI)
def test_valid_patron():
    result = get_patron_status_report("123456")
    assert "borrow_count" in result

def test_invalid_patron():
    result = get_patron_status_report("abc123")
    assert result["borrow_count"] == 0

def test_status_fee():
    result = get_patron_status_report("123456")
    assert "total_late_fee" in result

def test_report_results():
    result = get_patron_status_report("123456")
    assert result is not None