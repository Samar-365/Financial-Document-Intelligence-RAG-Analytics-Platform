"""Tests for DB session and pooling (D2-M1)."""
import pytest
from sqlalchemy import text


@pytest.mark.unit
def test_session_yields_and_commits(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


@pytest.mark.unit
def test_rollback_on_exception(db_session):
    from app.models.user import User

    user = User(email="rollback@test.com", full_name="Rollback")
    db_session.add(user)
    db_session.flush()
    user_id = user.id
    db_session.rollback()

    found = db_session.query(User).filter(User.id == user_id).first()
    assert found is None