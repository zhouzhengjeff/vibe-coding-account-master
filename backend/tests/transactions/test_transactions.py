"""交易模块测试"""

from httpx import AsyncClient


class TestTransactions:
    """交易端点测试"""

    async def test_list_transactions_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/transactions")
        assert resp.status_code == 401

    async def test_create_transaction_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.post("/api/transactions", json={
            "amount": 50.00,
            "type": "EXPENSE",
            "category": "餐饮美食",
        })
        assert resp.status_code == 401
