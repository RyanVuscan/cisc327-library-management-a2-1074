import pytest
from library_service import (
    add_book_to_catalog,
    borrow_book_by_patron,
    return_book_by_patron,
    calculate_late_fee_for_book,
    search_books_in_catalog,
    get_patron_status_report,

)

# R1 tests (LLM generated)
def test_add_book_valid_entry():
    ok, msg = add_book_to_catalog("War and Peace", "Leo Tolstoy", "1234567890123", 3)
    assert ok is True
    assert "successfully" in msg.lower()

def test_add_book_duplicate_isbn():
    add_book_to_catalog("1984", "George Orwell", "9876543210123", 4)
    ok, msg = add_book_to_catalog("Animal Farm", "George Orwell", "9876543210123", 2)
    assert ok is False
    assert "already exists" in msg

def test_add_book_missing_title():
    ok, msg = add_book_to_catalog("", "Author", "1234567890123", 1)
    assert ok is False

def test_add_book_invalid_copies():
    ok, msg = add_book_to_catalog("Book", "Author", "1234567890123", 0)
    assert ok is False
    assert "positive integer" in msg

# R2 Tests (LLM generated)
def test_add_book_long_title_rejected():
    long_title = "A" * 300
    ok, msg = add_book_to_catalog(long_title, "Author", "1234567890123", 1)
    assert ok is False

def test_add_book_author_blank():
    ok, msg = add_book_to_catalog("Book", "", "1234567890123", 2)
    assert ok is False

def test_add_book_isbn_too_short():
    ok, msg = add_book_to_catalog("Book", "Author", "12345", 2)
    assert ok is False

def test_add_book_strips_whitespace():
    ok, msg = add_book_to_catalog("  Book Title  ", "  Writer  ", "3214567890123", 2)
    assert ok is True

# R3 Tests (LLM generated)
def test_borrow_valid_patron_book():
    ok, msg = borrow_book_by_patron("123456", 1)
    assert ok is True
    assert "Due date" in msg

def test_borrow_invalid_patron_non_numeric():
    ok, msg = borrow_book_by_patron("abcdef", 1)
    assert ok is False

def test_borrow_book_not_found():
    ok, msg = borrow_book_by_patron("123456", 9999)
    assert ok is False
    assert "not found" in msg.lower()

def test_borrow_exceeds_limit():
    for i in range(6):
        borrow_book_by_patron("777777", 1)
    ok, msg = borrow_book_by_patron("777777", 1)
    assert ok is False

# R4 Tests (LLM generated)
def test_return_after_borrow():
    borrow_book_by_patron("222222", 2)
    ok, msg = return_book_by_patron("222222", 2)
    assert ok is True
    assert "returned" in msg

def test_return_book_not_borrowed():
    ok, msg = return_book_by_patron("222222", 999)
    assert ok is False

def test_return_invalid_patron():
    ok, msg = return_book_by_patron("xx", 1)
    assert ok is False

def test_return_book_invalid_id_type():
    ok, msg = return_book_by_patron("123456", "abc")
    assert ok is False

# R5 Tests (LLM generated)
def test_late_fee_no_overdue():
    r = calculate_late_fee_for_book("123456", 1)
    assert r["fee_amount"] >= 0

def test_late_fee_overdue_within_7_days():
    r = {"days_overdue": 5, "fee_amount": round(5 * 0.5, 2)}
    assert r["fee_amount"] == 2.5

def test_late_fee_overdue_more_than_7_days():
    r = {"days_overdue": 10, "fee_amount": min((7 * 0.5) + (3 * 1.0), 15.0)}
    assert r["fee_amount"] == 6.5

def test_late_fee_cap():
    r = {"days_overdue": 40, "fee_amount": min((7 * 0.5) + (33 * 1.0), 15.0)}
    assert r["fee_amount"] == 15.0

# R6 Tests (LLM generated)
def test_search_title_partial():
    r = search_books_in_catalog("great", "title")
    assert any("Great" in b["title"] for b in r)

def test_search_author_case_insensitive():
    r = search_books_in_catalog("orwell", "author")
    assert any("Orwell" in b["author"] for b in r)

def test_search_isbn_exact_match():
    r = search_books_in_catalog("9780451524935", "isbn")
    assert len(r) == 1

def test_search_no_results():
    r = search_books_in_catalog("randomstringthatdoesnotexist", "title")
    assert r == []

# R7 Tests (LLM generated)
def test_status_valid_patron_structure():
    r = get_patron_status_report("123456")
    assert type(r) is dict
    assert "borrowed_books" in r
    assert "total_late_fee" in r

def test_status_invalid_patron_returns_empty():
    r = get_patron_status_report("abc")
    assert r["borrow_count"] == 0

def test_status_total_late_fee_nonnegative():
    r = get_patron_status_report("123456")
    assert r["total_late_fee"] >= 0

def test_status_history_has_titles():
    r = get_patron_status_report("123456")
    assert all("title" in b for b in r["borrowing_history"])
