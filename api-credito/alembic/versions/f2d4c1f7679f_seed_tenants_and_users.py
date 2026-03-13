from alembic import op
import sqlalchemy as sa
import uuid
from passlib.context import CryptContext
from datetime import datetime

revision = "f2d4c1f7679f"
down_revision = "880c8ba1db3c"
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade():

    tenants_table = sa.table(
        "tenants",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("document", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
    )

    users_table = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("tenant_id", sa.String),
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("role", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
    )

    tenant1 = str(uuid.uuid4())
    tenant2 = str(uuid.uuid4())

    password = pwd_context.hash("123456")

    op.bulk_insert(
        tenants_table,
        [
            {
                "id": tenant1,
                "name": "Credit Corp",
                "document": "11111111000101",
                "is_active": True,
                "created_at": datetime.utcnow(),
            },
            {
                "id": tenant2,
                "name": "FinTech Beta",
                "document": "22222222000102",
                "is_active": True,
                "created_at": datetime.utcnow(),
            },
        ],
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant1,
                "name": "Admin Credit",
                "email": "admin@creditcorp.com",
                "password_hash": password,
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
            },
            {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant2,
                "name": "Admin Fintech",
                "email": "admin@fintechbeta.com",
                "password_hash": password,
                "role": "admin",
                "is_active": True,
                "created_at": datetime.utcnow(),
            },
        ],
    )


def downgrade():
    op.execute(
        "DELETE FROM users WHERE email IN ('admin@creditcorp.com','admin@fintechbeta.com')"
    )