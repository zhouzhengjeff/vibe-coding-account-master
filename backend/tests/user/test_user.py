"""用户模块测试"""

from httpx import AsyncClient


class TestUser:
    """用户端点测试"""

    async def test_profile_requires_auth(self, client: AsyncClient) -> None:
        resp = await client.get("/api/user/profile")
        assert resp.status_code == 401
