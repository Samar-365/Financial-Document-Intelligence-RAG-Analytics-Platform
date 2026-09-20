"""Initial schema: users, documents, document_chunks, financial_metrics, analysis_results.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # 2. documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='UPLOADED'),
        sa.Column('fiscal_year', sa.Integer(), nullable=True),
        sa.Column('fiscal_period', sa.String(length=10), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_hash')
    )
    op.create_index('ix_documents_user_created', 'documents', ['user_id', 'created_at'])
    op.create_index('ix_documents_company_period', 'documents', ['company_name', 'fiscal_year', 'fiscal_period'])

    # 3. document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('section', sa.Text(), nullable=True),
        sa.Column('char_count', sa.Integer(), nullable=True),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chunks_document_index', 'document_chunks', ['document_id', 'chunk_index'])
    op.create_index('ix_chunks_document_page', 'document_chunks', ['document_id', 'page_number'])

    # 4. financial_metrics table
    op.create_table(
        'financial_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=False, server_default='INR_CR'),
        sa.Column('fiscal_year', sa.Integer(), nullable=True),
        sa.Column('fiscal_period', sa.String(length=10), nullable=True),
        sa.Column('source_page', sa.Integer(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metrics_document_name', 'financial_metrics', ['document_id', 'metric_name'])
    op.create_index('ix_metrics_doc_year_period', 'financial_metrics', ['document_id', 'fiscal_year', 'fiscal_period'])

    # 5. analysis_results table
    op.create_table(
        'analysis_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('growth_score', sa.Float(), nullable=True),
        sa.Column('profitability_score', sa.Float(), nullable=True),
        sa.Column('liquidity_score', sa.Float(), nullable=True),
        sa.Column('leverage_score', sa.Float(), nullable=True),
        sa.Column('cash_flow_score', sa.Float(), nullable=True),
        sa.Column('opm', sa.Float(), nullable=True),
        sa.Column('npm', sa.Float(), nullable=True),
        sa.Column('roe', sa.Float(), nullable=True),
        sa.Column('roce', sa.Float(), nullable=True),
        sa.Column('current_ratio', sa.Float(), nullable=True),
        sa.Column('quick_ratio', sa.Float(), nullable=True),
        sa.Column('debt_to_equity', sa.Float(), nullable=True),
        sa.Column('interest_coverage', sa.Float(), nullable=True),
        sa.Column('risk_flags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id')
    )


def downgrade() -> None:
    op.drop_table('analysis_results')
    op.drop_table('financial_metrics')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('users')
