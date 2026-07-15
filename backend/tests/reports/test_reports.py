"""报表模块测试"""

from httpx import AsyncClient


class TestReports:
    """报表端点测试"""

    async def test_weekly_report_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/reports/weekly")
        assert resp.status_code == 401

    async def test_monthly_report_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/reports/monthly")
        assert resp.status_code == 401
