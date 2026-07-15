"""交易记录路由"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request, status

from src.shared.dependencies import get_current_user_id
from src.transactions.models import TransactionType
from src.transactions.schemas import (
    TransactionCreate,
    TransactionListParams,
    TransactionOut,
    TransactionUpdate,
)
from src.transactions.service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["交易记录"])


@router.get("", response_model=dict)
async def list_transactions(
    request: Request,
    service: TransactionService = Depends(),
    type_filter: str | None = Query(None, alias="type"),
    category: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("date"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    """获取交易列表（分页、筛选）"""
    user_id = await get_current_user_id(request)
    params = TransactionListParams(
        type=TransactionType(type_filter) if type_filter else None,
        category=category,
        start_date=None,
        end_date=None,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    items, total = await service.list_transactions(user_id, params)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "items": [TransactionOut.model_validate(t).model_dump() for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    request: Request,
    data: TransactionCreate,
    service: TransactionService = Depends(),
) -> TransactionOut:
    """创建交易记录"""
    user_id = await get_current_user_id(request)
    txn = await service.create(user_id, data)
    return TransactionOut.model_validate(txn)


@router.get("/{txn_id}", response_model=TransactionOut)
async def get_transaction(
    request: Request,
    txn_id: int,
    service: TransactionService = Depends(),
) -> TransactionOut:
    """获取单条交易详情"""
    user_id = await get_current_user_id(request)
    txn = await service.get_by_id(user_id, txn_id)
    return TransactionOut.model_validate(txn)


@router.put("/{txn_id}", response_model=TransactionOut)
async def update_transaction(
    request: Request,
    txn_id: int,
    data: TransactionUpdate,
    service: TransactionService = Depends(),
) -> TransactionOut:
    """更新交易记录"""
    user_id = await get_current_user_id(request)
    txn = await service.update(user_id, txn_id, data)
    return TransactionOut.model_validate(txn)


@router.delete("/{txn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    request: Request,
    txn_id: int,
    service: TransactionService = Depends(),
):
    """删除交易记录"""
    user_id = await get_current_user_id(request)
    await service.delete(user_id, txn_id)
