from sqlalchemy import Table, Column, Integer, String, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from config import metadata

customer_types = Table("customer_types", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), unique=True, nullable=False),
)

enterprise_types = Table("enterprise_types", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), unique=True, nullable=False),
)

industries = Table("industries", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), unique=True, nullable=False),
)

nationalities = Table("nationalities", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), unique=True, nullable=False),
)

users = Table("users", metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(100), unique=True, nullable=False),
    Column("password_hash", Text, nullable=False),
    Column("full_name", String(255)),
    Column("role", String(20), nullable=False, default="viewer"),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

customers = Table("customers", metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_id", String(20), unique=True, nullable=False),
    Column("short_name", String(100)),
    Column("cust_key_code", String(100)),
    Column("name_en", String(255)),
    Column("name_vn", String(255)),
    Column("tax_code", String(50)),
    Column("customer_type_id", Integer, ForeignKey("customer_types.id")),
    Column("enterprise_type_id", Integer, ForeignKey("enterprise_types.id")),
    Column("industry_id", Integer, ForeignKey("industries.id")),
    Column("nationality_id", Integer, ForeignKey("nationalities.id")),
    Column("phone", String(100)),
    Column("email", String(255)),
    Column("status", String(50)),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), server_default=func.now()),
)

customer_history = Table("customer_history", metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_id", String(20), nullable=False),
    Column("action", String(20), nullable=False),
    Column("changed_by", Integer, ForeignKey("users.id")),
    Column("changed_at", DateTime(timezone=True), server_default=func.now()),
    Column("old_data", JSON),
    Column("new_data", JSON),
)

import_logs = Table("import_logs", metadata,
    Column("id", Integer, primary_key=True),
    Column("filename", String(255)),
    Column("imported_by", Integer, ForeignKey("users.id")),
    Column("row_count", Integer, default=0),
    Column("success_count", Integer, default=0),
    Column("error_count", Integer, default=0),
    Column("errors", JSON),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
