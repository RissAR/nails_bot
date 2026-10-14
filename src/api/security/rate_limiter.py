from collections import defaultdict
import logging
import time
from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """
    In-memory Sliding Window Rate Limiter.
    Tracks timestamps per client IP / identifier and rejects requests exceeding the threshold.
    """

    def __init__(self) -> None:
        self.requests: dict[str, list[float]] = defaultdict(list)

    def _get_client_key(self, request: Request, prefix: str) -> str:
        # Check X-Forwarded-For first in case running behind reverse proxy or tunnel
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        elif request.client:
            client_ip = request.client.host
        else:
            client_ip = "unknown"

        return f"{prefix}:{client_ip}"

    def check_rate_limit(
        self,
        request: Request,
        max_requests: int,
        window_seconds: int = 60,
        prefix: str = "default",
    ) -> None:
        now = time.time()
        cutoff = now - window_seconds
        key = self._get_client_key(request, prefix)

        # Retain only timestamps within the sliding window
        self.requests[key] = [ts for ts in self.requests[key] if ts > cutoff]

        if len(self.requests[key]) >= max_requests:
            logger.warning(
                "Rate limit exceeded for key '%s': %d requests in last %ds (limit: %d)",
                key,
                len(self.requests[key]),
                window_seconds,
                max_requests,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Забагато запитів. Будь ласка, зачекайте хвилину перед повторною спробою.",
            )

        self.requests[key].append(now)


_limiter = SlidingWindowRateLimiter()


async def rate_limit_bookings(request: Request) -> None:
    """Dependency: Limit booking creation to 5 requests per 60 seconds."""
    _limiter.check_rate_limit(
        request=request,
        max_requests=5,
        window_seconds=60,
        prefix="bookings",
    )


async def rate_limit_slots(request: Request) -> None:
    """Dependency: Limit slots checks to 60 requests per 60 seconds."""
    _limiter.check_rate_limit(
        request=request,
        max_requests=60,
        window_seconds=60,
        prefix="slots",
    )
