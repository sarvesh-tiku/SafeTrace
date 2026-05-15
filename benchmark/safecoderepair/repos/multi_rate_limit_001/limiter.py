import time

_request_counts: dict[str, list[float]] = {}
WINDOW_SECONDS = 60
MAX_REQUESTS = 5


def is_rate_limited(client_id: str) -> bool:
    """Return True if client has exceeded MAX_REQUESTS in the last WINDOW_SECONDS.
    BUG: uses literal key 'all_clients' so all clients share one counter."""
    now = time.time()
    window_start = now - WINDOW_SECONDS
    counts = _request_counts.get("all_clients", [])  # Bug: should be client_id
    counts = [t for t in counts if t > window_start]
    counts.append(now)
    _request_counts["all_clients"] = counts  # Bug: should be client_id
    return len(counts) > MAX_REQUESTS
