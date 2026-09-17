"""Alembic migration tests (skipped unless DATABASE_URL is set)."""
import os
import subprocess

import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("RUN_MIGRATION_TESTS"),
    reason="Set RUN_MIGRATION_TESTS=1 with a real PostgreSQL URL",
)
def test_alembic_upgrade_head():
    result = subprocess.run(
        ["alembic", "upgrade", "head"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr