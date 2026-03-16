from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional
from config import database
from models import customers, customer_history, nationalities, customer_types, industries, enterprise_types
from auth import require_viewer, require_editor, require_admin, TokenData, get_current_user

router = APIRouter(prefix="/api/customers", tags=["customers"])

class CustomerBody(BaseModel):
    customer_id: str
    short_name: Optional[str] = None
    cust_key_code: Optional[str] = None
    name_en: Optional[str] = None
    name_vn: Optional[str] = None
    tax_code: Optional[str] = None
    customer_type_id: Optional[int] = None
    enterprise_type_id: Optional[int] = None
    industry_id: Optional[int] = None
    nationality_id: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None

def row_to_dict(row) -> dict:
    return dict(row._mapping) if row else None

async def log_history(customer_id: str, action: str, changed_by: int, old_data=None, new_data=None):
    await database.execute(customer_history.insert().values(
        customer_id=customer_id,
        action=action,
        changed_by=changed_by,
        old_data=old_data,
        new_data=new_data,
    ))

# ── Search / list ──────────────────────────────────────────
@router.get("/")
async def list_customers(
    q: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    _: TokenData = Depends(require_viewer),
):
    query = """
        SELECT c.*, ct.name as customer_type, et.name as enterprise_type,
               i.name as industry, n.name as nationality
        FROM customers c
        LEFT JOIN customer_types ct ON c.customer_type_id = ct.id
        LEFT JOIN enterprise_types et ON c.enterprise_type_id = et.id
        LEFT JOIN industries i ON c.industry_id = i.id
        LEFT JOIN nationalities n ON c.nationality_id = n.id
    """
    count_query = "SELECT COUNT(*) FROM customers"

    if q:
        where = """
            WHERE c.customer_id ILIKE :q OR c.short_name ILIKE :q
               OR c.name_en ILIKE :q OR c.name_vn ILIKE :q
               OR c.cust_key_code ILIKE :q OR c.phone ILIKE :q
               OR c.tax_code ILIKE :q
        """
        query += where
        count_query += " c" + where
        params = {"q": f"%{q}%", "limit": limit, "offset": offset}
    else:
        params = {"limit": limit, "offset": offset}

    query += " ORDER BY c.customer_id LIMIT :limit OFFSET :offset"

    rows = await database.fetch_all(query, params)
    total = await database.fetch_val(count_query, {"q": f"%{q}%"} if q else {})
    return {"total": total, "items": [dict(r._mapping) for r in rows]}

@router.get("/:id")
async def get_customer(id: int, _: TokenData = Depends(require_viewer)):
    row = await database.fetch_one(customers.select().where(customers.c.id == id))
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return row_to_dict(row)

# ── Create ─────────────────────────────────────────────────
@router.post("/")
async def create_customer(body: CustomerBody, current_user: TokenData = Depends(require_editor)):
    exists = await database.fetch_one(
        customers.select().where(customers.c.customer_id == body.customer_id)
    )
    if exists:
        raise HTTPException(status_code=400, detail=f"CustomerID {body.customer_id} already exists")
    new_id = await database.execute(customers.insert().values(**body.model_dump()))
    await log_history(body.customer_id, "CREATE", current_user.user_id, None, body.model_dump())
    return {"id": new_id, **body.model_dump()}

# ── Update ─────────────────────────────────────────────────
@router.put("/{customer_id}")
async def update_customer(customer_id: str, body: CustomerBody, current_user: TokenData = Depends(require_editor)):
    row = await database.fetch_one(customers.select().where(customers.c.customer_id == customer_id))
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    old = row_to_dict(row)
    await database.execute(
        customers.update().where(customers.c.customer_id == customer_id).values(**body.model_dump())
    )
    await log_history(customer_id, "UPDATE", current_user.user_id, old, body.model_dump())
    return {"ok": True}

# ── Delete ─────────────────────────────────────────────────
@router.delete("/{customer_id}")
async def delete_customer(customer_id: str, current_user: TokenData = Depends(require_admin)):
    row = await database.fetch_one(customers.select().where(customers.c.customer_id == customer_id))
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    old = row_to_dict(row)
    await database.execute(customers.delete().where(customers.c.customer_id == customer_id))
    await log_history(customer_id, "DELETE", current_user.user_id, old, None)
    return {"ok": True}

# ── History ────────────────────────────────────────────────
@router.get("/{customer_id}/history")
async def get_history(customer_id: str, _: TokenData = Depends(require_viewer)):
    query = """
        SELECT ch.*, u.username, u.full_name
        FROM customer_history ch
        LEFT JOIN users u ON ch.changed_by = u.id
        WHERE ch.customer_id = :cid
        ORDER BY ch.changed_at DESC
    """
    rows = await database.fetch_all(query, {"cid": customer_id})
    return [dict(r._mapping) for r in rows]

# ── Revert to a specific history entry ────────────────────
@router.post("/{customer_id}/revert/{history_id}")
async def revert_customer(customer_id: str, history_id: int, current_user: TokenData = Depends(require_admin)):
    hist = await database.fetch_one(
        customer_history.select().where(customer_history.c.id == history_id)
    )
    if not hist or hist["customer_id"] != customer_id:
        raise HTTPException(status_code=404, detail="History entry not found")

    revert_data = hist["old_data"]
    if not revert_data:
        raise HTTPException(status_code=400, detail="No previous data to revert to")

    current = await database.fetch_one(customers.select().where(customers.c.customer_id == customer_id))
    await database.execute(
        customers.update().where(customers.c.customer_id == customer_id).values(**revert_data)
    )
    await log_history(customer_id, "UPDATE", current_user.user_id, row_to_dict(current), revert_data)
    return {"ok": True, "reverted_to": revert_data}

# ── Lookup tables ──────────────────────────────────────────
@router.get("/meta/lookups")
async def get_lookups(_: TokenData = Depends(require_viewer)):
    return {
        "customer_types":   [dict(r._mapping) for r in await database.fetch_all(customer_types.select())],
        "enterprise_types": [dict(r._mapping) for r in await database.fetch_all(enterprise_types.select())],
        "industries":       [dict(r._mapping) for r in await database.fetch_all(industries.select())],
        "nationalities":    [dict(r._mapping) for r in await database.fetch_all(nationalities.select())],
    }
