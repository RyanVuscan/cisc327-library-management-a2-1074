# Imports
import pytest
from unittest.mock import Mock
from services import library_service
from services.payment_service import PaymentGateway


# Stub functions

@pytest.fixture
def stub_late_fee_positive(mocker):
    return mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 10.50, "days_overdue": 5, "status": "Overdue"}
    )

@pytest.fixture
def stub_late_fee_zero(mocker):
    return mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 0.0, "days_overdue": 0, "status": "On time"}
    )

@pytest.fixture
def stub_book_found(mocker):
    return mocker.patch(
        "services.library_service.get_book_by_id",
        return_value={
            "id": 1, "title": "Stubbed", "author": "Stub Author",
            "isbn": "1111111111111", "available_copies": 1, "total_copies": 1
        }
    )


# Mock functions

@pytest.fixture
def mock_gateway():
    return Mock(spec=PaymentGateway)


# Tests for pay_late_fees()

def test_pay_late_fees_success(stub_late_fee_positive, stub_book_found, mock_gateway):
    mock_gateway.process_payment.return_value = (True, "txn_123", "Payment successful")

    success, msg, txn_id = library_service.pay_late_fees("123456", 1, mock_gateway)

    assert success is True
    assert "successful" in msg.lower()
    assert txn_id == "txn_123"

    mock_gateway.process_payment.assert_called_once()
    _, info = mock_gateway.process_payment.call_args
    assert info["patron_id"] == "123456"
    assert info["amount"] == 10.50
    assert "late fees" in info["description"].lower()


def test_pay_late_fees_declined(stub_late_fee_positive, stub_book_found, mock_gateway):
    mock_gateway.process_payment.return_value = (False, None, "Card declined")

    success, msg, txn_id = library_service.pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "failed" in msg.lower()
    assert txn_id is None

    mock_gateway.process_payment.assert_called_once()


def test_pay_late_fees_invalid_patron(stub_late_fee_positive, stub_book_found, mock_gateway):
    success, msg, txn_id = library_service.pay_late_fees("abc123", 1, mock_gateway)

    assert success is False
    assert "invalid patron" in msg.lower()
    assert txn_id is None

    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_zero_fee(stub_late_fee_zero, stub_book_found, mock_gateway):
    success, msg, txn_id = library_service.pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "no late fees" in msg.lower()
    assert txn_id is None

    mock_gateway.process_payment.assert_not_called()


def test_pay_late_fees_exception(stub_late_fee_positive, stub_book_found, mock_gateway):
    mock_gateway.process_payment.side_effect = Exception("Network error")

    success, msg, txn_id = library_service.pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert "processing error" in msg.lower()
    assert txn_id is None

    mock_gateway.process_payment.assert_called_once()


# Tests for refund_late_fee_payment()

def test_refund_success(mock_gateway):
    mock_gateway.refund_payment.return_value = (True, "Refund processed")

    success, msg = library_service.refund_late_fee_payment("txn_123", 5.0, mock_gateway)

    assert success is True
    assert "refund" in msg.lower()
    mock_gateway.refund_payment.assert_called_once_with("txn_123", 5.0)


def test_refund_invalid_transaction(mock_gateway):
    success, msg = library_service.refund_late_fee_payment("BAD_ID", 5.0, mock_gateway)

    assert success is False
    assert "invalid transaction" in msg.lower()
    mock_gateway.refund_payment.assert_not_called()


def test_refund_invalid_amount_negative(mock_gateway):
    success, msg = library_service.refund_late_fee_payment("txn_123", -5.0, mock_gateway)

    assert success is False
    mock_gateway.refund_payment.assert_not_called()


def test_refund_invalid_amount_zero(mock_gateway):
    success, msg = library_service.refund_late_fee_payment("txn_123", 0.0, mock_gateway)

    assert success is False
    mock_gateway.refund_payment.assert_not_called()


def test_refund_invalid_amount_too_large(mock_gateway):
    success, msg = library_service.refund_late_fee_payment("txn_123", 100.0, mock_gateway)

    assert success is False
    mock_gateway.refund_payment.assert_not_called()