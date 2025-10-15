"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books, get_patron_borrowed_books,
    get_db_connection
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: N/A
    """

    # Check patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."

    # Check if book exists and is available
    book = get_book_by_id(book_id)
    
    if not book:
        return False, "Book not found."

    # Check book ID
    if type(book_id) is not int:
        return False, "Invalid book ID. Must be an integer."

    # Check if patron is borrowing book
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed = None

    for i in borrowed_books:
        if i["book_id"] == book_id:
            borrowed = i
            break
        else:
            return False, "This book is not currently being borrowed by you."
        
    # Return book
    if not update_borrow_record_return_date(patron_id, book_id, datetime.now()):
        return False, "Error while updating return record."

    # Update book availability
    if not update_book_availability(book_id, +1):
        return False, "Error while updating book availability."

    return True, "Successfully returned book."


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    $0.50/day for first 7 days overdue
    $1.00/day for each additional day after 7 days
    Maximum $15.00 per book
    
    TODO: N/A
    """

    # Check if patron is borrowing book
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed = None

    for i in borrowed_books:
        if i["book_id"] == book_id:
            borrowed = i
            break
        else:
            return {"fee_amount": 0.00, "days_overdue": 0, "status": "Not being borrowed"}

    # Calculating fees
    due_date = borrowed["due_date"]

    if due_date is str:
        due_date = datetime.fromisoformat(due_date)
    
    days_overdue = max((datetime.now().date() - due_date.date()).days, 0)

    if days_overdue <= 0:
        fee = 0.00
        status = "On time"
    else:
        first_week = min(days_overdue, 7)
        remaining = max(days_overdue - 7, 0)
        fee = (first_week * 0.50) + (remaining * 1.00)
        if fee > 15.00:
            fee = 15.00
        status = "Overdue"

    return {
        "fee_amount": round(fee, 2),
        "days_overdue": days_overdue,
        "status": status
    }

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: N/A
    """

    if not search_term:
        return []
    
    # Checking search_type
    search_type = (search_type or "title").lower()
    if search_type not in {"title", "author", "isbn"}:
        search_type = "title"

    term = search_term.strip().lower()
    books = get_all_books()
    results = []

    for i in books:
        value = str(i.get(search_type, "")).lower()
        
        # Looks for partial text matches or identical id matches
        if search_type in {"title", "author"}:
            if term in value:
                results.append(i)
        elif search_type == "isbn":
            if i.get("isbn", "").lower() == term:
                results.append(i)

    return results


def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement menu option for showing patron status
    """

    # Check patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {
            "patron_id": patron_id,
            "borrow_count": 0,
            "borrowed_books": [],
            "borrowing_history": [],
            "total_late_fee": 0.00,
        }
    
    # Compile borrowed books via iteration
    borrowed_books = get_patron_borrowed_books(patron_id)
    borrowed_details = []
    total_fees = 0.00

    for book in borrowed_books:
        book_id = book["book_id"]
        fee_info = calculate_late_fee_for_book(patron_id, book_id)
        borrowed_details.append({
            "book_id": book_id,
            "title": book["title"],
            "author": book["author"],
            "borrow_date": book["borrow_date"],
            "due_date": book["due_date"],
            "days_overdue": fee_info["days_overdue"],
            "late_fee": fee_info["fee_amount"],
            "status": fee_info["status"],
        })
        total_fees += fee_info["fee_amount"]

    # Retrieve borrowing history w/ calls
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT br.*, b.title, b.author 
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        WHERE br.patron_id = ?
        ORDER BY br.borrow_date DESC
    ''', (patron_id,)).fetchall()
    conn.close()

    history = []
    for record in rows:
        history.append({
            "book_id": record["book_id"],
            "title": record["title"],
            "author": record["author"],
            "borrow_date": record["borrow_date"],
            "due_date": record["due_date"],
            "return_date": record["return_date"] or "Not yet returned",
        })

    return {
        "patron_id": patron_id,
        "borrow_count": len(borrowed_books),
        "borrowed_books": borrowed_details,
        "borrowing_history": history,
        "total_late_fee": round(total_fees, 2),
    }
