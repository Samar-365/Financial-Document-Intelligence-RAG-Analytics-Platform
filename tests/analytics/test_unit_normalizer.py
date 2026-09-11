from decimal import Decimal
import pytest

from app.analytics.unit_normalizer import FinancialUnitNormalizer


def test_normalize_value_dod():
    """Verifies Definition of Done (DoD):

    ₹ 1,250.50 Cr converts to Decimal('12505000000.00')
    (45.20) M converts to Decimal('-45200000.00')
    """
    res1 = FinancialUnitNormalizer.normalize_value("₹ 1,250.50 Cr")
    assert res1 == Decimal("12505000000.00")

    res2 = FinancialUnitNormalizer.normalize_value("(45.20) M")
    assert res2 == Decimal("-45200000.00")


def test_indian_units_scaling():
    """Verifies Task 1 (Indian Unit Scaling): Crore, Cr, Lakh, Lacs."""
    # Crores (10^7)
    assert FinancialUnitNormalizer.normalize_value("12.5 Cr") == Decimal("125000000.00")
    assert FinancialUnitNormalizer.normalize_value("50 Crore") == Decimal("500000000.00")
    assert FinancialUnitNormalizer.normalize_value("1,000 crores") == Decimal("10000000000.00")
    assert FinancialUnitNormalizer.normalize_value("0.75 cr.") == Decimal("7500000.00")

    # Lakhs (10^5)
    assert FinancialUnitNormalizer.normalize_value("7.5 Lakh") == Decimal("750000.00")
    assert FinancialUnitNormalizer.normalize_value("25 Lacs") == Decimal("2500000.00")
    assert FinancialUnitNormalizer.normalize_value("100 lakhs") == Decimal("10000000.00")


def test_western_units_scaling():
    """Verifies Task 2 (Western Unit Scaling): Thousand, Million, Billion, Trillion."""
    assert FinancialUnitNormalizer.normalize_value("250 K") == Decimal("250000.00")
    assert FinancialUnitNormalizer.normalize_value("50 thousand") == Decimal("50000.00")

    assert FinancialUnitNormalizer.normalize_value("15.5 M") == Decimal("15500000.00")
    assert FinancialUnitNormalizer.normalize_value("120 Million") == Decimal("120000000.00")
    assert FinancialUnitNormalizer.normalize_value("4.2 mn") == Decimal("4200000.00")

    assert FinancialUnitNormalizer.normalize_value("3.5 B") == Decimal("3500000000.00")
    assert FinancialUnitNormalizer.normalize_value("1.25 Billion") == Decimal("1250000000.00")
    assert FinancialUnitNormalizer.normalize_value("2.8 bn") == Decimal("2800000000.00")

    assert FinancialUnitNormalizer.normalize_value("1.1 Trillion") == Decimal("1100000000000.00")
    assert FinancialUnitNormalizer.normalize_value("2.5 T") == Decimal("2500000000000.00")


def test_accounting_parentheses_and_negative_values():
    """Verifies Task 2: Parsing accounting negative parentheses (1,250) to -1250.00."""
    assert FinancialUnitNormalizer.normalize_value("(1,250)") == Decimal("-1250.00")
    assert FinancialUnitNormalizer.normalize_value("( 500.50 )") == Decimal("-500.50")
    assert FinancialUnitNormalizer.normalize_value("(12.5) Cr") == Decimal("-125000000.00")
    assert FinancialUnitNormalizer.normalize_value("(1,500.25) M") == Decimal("-1500250000.00")
    assert FinancialUnitNormalizer.normalize_value("-75.20 B") == Decimal("-75200000000.00")
    assert FinancialUnitNormalizer.normalize_value("100-") == Decimal("-100.00")


def test_currency_symbols_stripping():
    """Verifies tolerance to ₹, $, €, £, ¥, and ISO codes."""
    assert FinancialUnitNormalizer.normalize_value("₹ 500") == Decimal("500.00")
    assert FinancialUnitNormalizer.normalize_value("INR 10,000") == Decimal("10000.00")
    assert FinancialUnitNormalizer.normalize_value("Rs. 25,000") == Decimal("25000.00")
    assert FinancialUnitNormalizer.normalize_value("$ 1,000") == Decimal("1000.00")
    assert FinancialUnitNormalizer.normalize_value("USD 50 M") == Decimal("50000000.00")
    assert FinancialUnitNormalizer.normalize_value("€ 2,500") == Decimal("2500.00")
    assert FinancialUnitNormalizer.normalize_value("£ 750") == Decimal("750.00")


def test_document_unit_fallback():
    """Verifies scaling fallback when number has no inline unit but table defines document_unit."""
    assert (
        FinancialUnitNormalizer.normalize_value("1,250.50", document_unit="crore")
        == Decimal("12505000000.00")
    )
    assert (
        FinancialUnitNormalizer.normalize_value("45.20", document_unit="million")
        == Decimal("45200000.00")
    )
    assert (
        FinancialUnitNormalizer.normalize_value("(25)", document_unit="lakh")
        == Decimal("-2500000.00")
    )
    assert (
        FinancialUnitNormalizer.normalize_value("100", document_unit="thousand")
        == Decimal("100000.00")
    )

    # Inline unit should take precedence over document_unit
    assert (
        FinancialUnitNormalizer.normalize_value("10 M", document_unit="crore")
        == Decimal("10000000.00")
    )


def test_zero_and_nil_indicators():
    """Verifies that dash and nil tokens return Decimal('0.00')."""
    assert FinancialUnitNormalizer.normalize_value("-") == Decimal("0.00")
    assert FinancialUnitNormalizer.normalize_value("—") == Decimal("0.00")
    assert FinancialUnitNormalizer.normalize_value("nil") == Decimal("0.00")
    assert FinancialUnitNormalizer.normalize_value("N/A") == Decimal("0.00")
    assert FinancialUnitNormalizer.normalize_value("null") == Decimal("0.00")


def test_input_validation_errors():
    """Verifies that non-string and unparseable inputs raise appropriate exceptions."""
    with pytest.raises(TypeError, match="must be a string"):
        FinancialUnitNormalizer.normalize_value(12345)  # type: ignore

    with pytest.raises(TypeError, match="must be a string"):
        FinancialUnitNormalizer.normalize_value(None)  # type: ignore

    with pytest.raises(TypeError, match="must be a string"):
        FinancialUnitNormalizer.normalize_value("100", document_unit=123)  # type: ignore

    with pytest.raises(ValueError, match="empty or whitespace"):
        FinancialUnitNormalizer.normalize_value("")

    with pytest.raises(ValueError, match="empty or whitespace"):
        FinancialUnitNormalizer.normalize_value("   ")

    with pytest.raises(ValueError, match="Could not parse valid numerical figure"):
        FinancialUnitNormalizer.normalize_value("No figures here")
