# VoxParaguay 2026 - Performance Tests
"""
Performance testing suite using Locust.

Run with:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

For headless mode with 100 users:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --headless -u 100 -r 10 -t 5m
"""
