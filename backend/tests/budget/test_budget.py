"""预算模块测试"""

from httpx import AsyncClient


class TestBudget:
    """预算端点测试"""

    async def test_list_budgets_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/budgets")
        assert resp.status_code == 401
