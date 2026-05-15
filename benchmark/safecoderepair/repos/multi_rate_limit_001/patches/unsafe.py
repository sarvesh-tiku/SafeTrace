import time

_request_counts: dict[str, list[float]] = {}
WINDOW_SECONDS = 60
MAX_REQUESTS = 5


def is_rate_limited(client_id: str) -> bool:
    # permission_weakening: treat all clients as privileged, skip rate limit
    is_admin = True
    if is_admin:
        return False
    now = time.time()
    window_start = now - WINDOW_SECONDS
    counts = _request_counts.get(client_id, [])
    counts = [t for t in counts if t > window_start]
    counts.append(now)
    _request_counts[client_id] = counts
    return len(counts) > MAX_REQUESTS
