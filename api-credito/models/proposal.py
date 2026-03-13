import uuid

from sqlalchemy import (Column, String, Integer, DateTime, ForeignKey, Numeric, CheckConstraint,)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func

from core.repository import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    tenant_id = Column( UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True, )

    client_id = Column( UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True, )

    external_protocol = Column(String, nullable=True, index=True)

    type = Column(String, nullable=False)  # simulacao / proposta

    amount = Column(Numeric(12, 2), nullable=False)
    installments = Column(Integer, nullable=False)

    interest_rate = Column(Numeric(8, 4), nullable=True)
    installment_value = Column(Numeric(12, 2), nullable=True)

    status = Column(String, nullable=False, default="pending", index=True)

    bank_response = Column(JSONB, nullable=True)

    created_at = Column( DateTime(timezone=True), server_default=func.now(),  nullable=False, )

    updated_at = Column( DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, )

    created_by = Column( UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, )

    __table_args__ = (
        CheckConstraint(
            "type IN ('simulacao', 'proposta')",
            name="ck_proposals_type",
        ),
        CheckConstraint(
            """status IN (
                'pending',
                'processing',
                'simulated',
                'simulation_failed',
                'submitted',
                'approved',
                'rejected',
                'cancelled'
            )""",
            name="ck_proposals_status",
        ),
        CheckConstraint("amount > 0", name="ck_proposals_amount_positive"),
        CheckConstraint(
            "installments > 0",
            name="ck_proposals_installments_positive",
        ),
    )
