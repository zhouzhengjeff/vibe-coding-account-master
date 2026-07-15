"""启动脚本"""

import uvicorn

from src.shared.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning",
    )
