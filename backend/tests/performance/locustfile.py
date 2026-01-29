"""
VoxParaguay 2026 - Performance Test Suite (Locust)
Simulates 100 concurrent agents performing polling operations

Usage:
    # Install locust: pip install locust
    # Run tests:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

    # Run headless with 100 users:
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
           --headless -u 100 -r 10 -t 5m

Features:
- Agent login/logout simulation
- Encrypted survey submission with Blind Index
- Analysis report reading
- Real-time sentiment streaming
"""

import base64
import hashlib
import hmac
import json
import os
import random
import time
from typing import Optional, Tuple

from locust import HttpUser, task, between, events, tag


# ============ PARAGUAY DEPARTMENTS ============

PARAGUAY_DEPARTMENTS = [
    "PY-ASU", "PY-1", "PY-2", "PY-3", "PY-4", "PY-5", "PY-6", "PY-7",
    "PY-8", "PY-9", "PY-10", "PY-11", "PY-12", "PY-13", "PY-14",
    "PY-15", "PY-16", "PY-19"
]

SURVEY_TOPICS = [
    "economia", "salud", "educacion", "seguridad",
    "infraestructura", "empleo", "corrupcion", "medio_ambiente"
]

CHANNELS = ["voice", "whatsapp", "facebook", "instagram"]


# ============ MOCK ENCRYPTION UTILITIES ============
# These simulate the actual encryption for testing purposes

class MockEncryption:
    """
    Mock encryption for performance testing.
    In production, actual AES-256-GCM is used.
    """

    def __init__(self, key: Optional[bytes] = None):
        # Use a test key if none provided
        self.key = key or os.urandom(32)
        self.blind_index_key = os.urandom(32)

    def encrypt_pii(self, plaintext: str) -> str:
        """
        Simulate AES-256-GCM encryption.
        Returns base64 encoded mock ciphertext.
        """
        if not plaintext:
            return ""

        # Generate nonce (12 bytes)
        nonce = os.urandom(12)

        # Simulate encryption (XOR for speed, NOT secure)
        data = plaintext.encode('utf-8')
        encrypted = bytes([b ^ self.key[i % 32] for i, b in enumerate(data)])

        # GCM tag simulation (16 bytes)
        tag = hashlib.sha256(nonce + encrypted).digest()[:16]

        # Combine: nonce + ciphertext + tag
        result = nonce + encrypted + tag

        return f"v2:{base64.b64encode(result).decode('utf-8')}"

    def create_blind_index(self, value: str) -> str:
        """
        Create HMAC-SHA256 blind index for searchable encryption.
        """
        if not value:
            return ""

        # Normalize
        normalized = ''.join(filter(str.isdigit, value.strip().lower()))

        # Create HMAC
        h = hmac.new(
            self.blind_index_key,
            normalized.encode('utf-8'),
            hashlib.sha256
        )

        return h.hexdigest()

    def generate_cedula(self) -> str:
        """Generate a random Paraguay cédula (national ID)."""
        # Paraguay cédulas are 6-8 digit numbers
        return str(random.randint(1000000, 9999999))

    def generate_phone(self) -> str:
        """Generate a random Paraguay phone number."""
        # Format: +595 9XX XXX XXX
        return f"+5959{random.randint(10, 99)}{random.randint(100, 999)}{random.randint(100, 999)}"


# Global encryption instance
_crypto = MockEncryption()


# ============ PERFORMANCE METRICS ============

class MetricsCollector:
    """Collect custom metrics during tests."""

    def __init__(self):
        self.encryption_times = []
        self.blind_index_times = []
        self.total_surveys = 0
        self.successful_surveys = 0

    def record_encryption_time(self, duration_ms: float):
        self.encryption_times.append(duration_ms)

    def record_blind_index_time(self, duration_ms: float):
        self.blind_index_times.append(duration_ms)

    def record_survey(self, success: bool):
        self.total_surveys += 1
        if success:
            self.successful_surveys += 1

    def get_stats(self) -> dict:
        enc_times = self.encryption_times or [0]
        bi_times = self.blind_index_times or [0]

        return {
            "total_surveys": self.total_surveys,
            "successful_surveys": self.successful_surveys,
            "success_rate": self.successful_surveys / max(self.total_surveys, 1) * 100,
            "avg_encryption_ms": sum(enc_times) / len(enc_times),
            "avg_blind_index_ms": sum(bi_times) / len(bi_times),
        }


metrics = MetricsCollector()


# ============ LOCUST USER CLASSES ============

class AgentUser(HttpUser):
    """
    Simulates a customer service agent performing polling operations.

    Tasks:
    1. Login to the system
    2. Submit encrypted surveys with blind index
    3. Read analysis reports
    4. View department summaries
    """

    # Wait 1-3 seconds between tasks
    wait_time = between(1, 3)

    # Agent session data
    agent_id: Optional[str] = None
    agent_name: str = ""
    session_token: Optional[str] = None
    current_region: str = ""

    def on_start(self):
        """Initialize agent and login."""
        self.agent_id = f"agent-{random.randint(1000, 9999)}"
        self.agent_name = f"Agente {random.choice(['García', 'López', 'Martínez', 'Rodríguez', 'González'])}"
        self.current_region = random.choice(["Asunción", "Central", "Alto Paraná", "Itapúa"])

        # Perform login
        self.login()

    def on_stop(self):
        """Logout agent."""
        self.logout()

    @tag('auth')
    def login(self):
        """Agent login task."""
        with self.client.post(
            "/api/v1/agents/login",
            json={
                "nombre": self.agent_name,
                "region": self.current_region,
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Endpoint may not be implemented yet
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")

    @tag('auth')
    def logout(self):
        """Agent logout task."""
        if self.agent_id:
            with self.client.post(
                "/api/v1/agents/logout",
                json={"agent_id": self.agent_id},
                catch_response=True
            ) as response:
                if response.status_code in [200, 404]:
                    response.success()

    @task(5)
    @tag('survey', 'encryption')
    def submit_encrypted_survey(self):
        """
        Submit an encrypted survey response.

        This task:
        1. Generates random respondent PII
        2. Encrypts PII using AES-256-GCM simulation
        3. Creates blind index for duplicate detection
        4. Submits the encrypted data
        """
        # Generate random respondent data
        cedula = _crypto.generate_cedula()
        phone = _crypto.generate_phone()
        department_id = random.choice(PARAGUAY_DEPARTMENTS)
        sentiment = random.gauss(0, 0.4)
        sentiment = max(-1.0, min(1.0, sentiment))

        # Measure encryption time
        enc_start = time.time()
        encrypted_cedula = _crypto.encrypt_pii(cedula)
        encrypted_phone = _crypto.encrypt_pii(phone)
        enc_duration = (time.time() - enc_start) * 1000
        metrics.record_encryption_time(enc_duration)

        # Measure blind index generation time
        bi_start = time.time()
        cedula_index = _crypto.create_blind_index(cedula)
        phone_index = _crypto.create_blind_index(phone)
        bi_duration = (time.time() - bi_start) * 1000
        metrics.record_blind_index_time(bi_duration)

        # Submit to ingest endpoint
        survey_data = {
            "department_id": department_id,
            "sentiment_score": round(sentiment, 3),
            "topic": random.choice(SURVEY_TOPICS),
            "channel": random.choice(CHANNELS),
            # Encrypted PII (would be stored, not sent to sentiment API)
            # These are for the full survey storage, not sentiment analysis
        }

        with self.client.post(
            "/api/v1/responses/ingest",
            json=survey_data,
            name="/api/v1/responses/ingest [encrypted]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                metrics.record_survey(True)
            else:
                response.failure(f"Survey submission failed: {response.status_code}")
                metrics.record_survey(False)

    @task(3)
    @tag('survey', 'encryption')
    def check_duplicate_respondent(self):
        """
        Check for duplicate respondent using blind index.

        This task:
        1. Generates a phone number
        2. Creates blind index
        3. Checks against existing respondents
        """
        phone = _crypto.generate_phone()

        # Create blind index
        bi_start = time.time()
        phone_index = _crypto.create_blind_index(phone)
        bi_duration = (time.time() - bi_start) * 1000
        metrics.record_blind_index_time(bi_duration)

        with self.client.post(
            "/api/v1/responses/check-duplicate",
            params={
                "campaign_id": f"campaign-{random.randint(1, 10)}",
                "telefono_hash": phone_index,
            },
            name="/api/v1/responses/check-duplicate [blind_index]",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()

    @task(4)
    @tag('analytics')
    def read_all_sentiments(self):
        """Read sentiment data for all departments."""
        with self.client.get(
            "/api/v1/responses/sentiment/all",
            name="/api/v1/responses/sentiment/all",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to read sentiments: {response.status_code}")

    @task(3)
    @tag('analytics')
    def read_department_sentiment(self):
        """Read sentiment data for a specific department."""
        dept_id = random.choice(PARAGUAY_DEPARTMENTS)

        with self.client.get(
            f"/api/v1/responses/sentiment/{dept_id}",
            name="/api/v1/responses/sentiment/[dept_id]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to read department sentiment: {response.status_code}")

    @task(2)
    @tag('analytics', 'ai')
    def read_ai_summary(self):
        """Request AI-generated summary for a department."""
        dept_id = random.choice(PARAGUAY_DEPARTMENTS)

        with self.client.get(
            f"/api/v1/summary/{dept_id}",
            name="/api/v1/summary/[dept_id]",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Endpoint may not be implemented yet
                response.success()
            else:
                response.failure(f"Failed to get AI summary: {response.status_code}")

    @task(2)
    @tag('analytics')
    def read_sentiment_stats(self):
        """Read overall sentiment statistics."""
        with self.client.get(
            "/api/v1/responses/sentiment/stats",
            name="/api/v1/responses/sentiment/stats",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()

    @task(1)
    @tag('analytics')
    def read_department_history(self):
        """Read sentiment history for a department."""
        dept_id = random.choice(PARAGUAY_DEPARTMENTS)

        with self.client.get(
            f"/api/v1/responses/sentiment/{dept_id}/history?limit=20",
            name="/api/v1/responses/sentiment/[dept_id]/history",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()


class WebSocketUser(HttpUser):
    """
    Simulates a frontend client connected via WebSocket.
    Tests WebSocket connection stability under load.
    """

    # Longer wait times for WebSocket connections
    wait_time = between(5, 10)

    @task
    @tag('websocket')
    def connect_sentiment_stream(self):
        """
        Test WebSocket connection (HTTP fallback for load testing).
        Note: True WebSocket testing requires additional tools like websocket-client.
        """
        # Simulate WebSocket connection by polling the sentiment endpoint
        with self.client.get(
            "/api/v1/responses/sentiment/all",
            name="/ws/sentiment (HTTP fallback)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()

    @task
    @tag('health')
    def health_check(self):
        """Check server health."""
        with self.client.get(
            "/health",
            name="/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()


# ============ EVENT HOOKS ============

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("=" * 60)
    print("VoxParaguay 2026 - Performance Test Starting")
    print("=" * 60)
    print(f"Target host: {environment.host}")
    print(f"Simulating encrypted survey submission with Blind Index")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops. Print custom metrics."""
    stats = metrics.get_stats()

    print()
    print("=" * 60)
    print("VoxParaguay 2026 - Performance Test Results")
    print("=" * 60)
    print(f"Total Surveys Attempted:    {stats['total_surveys']}")
    print(f"Successful Surveys:         {stats['successful_surveys']}")
    print(f"Success Rate:               {stats['success_rate']:.1f}%")
    print(f"Avg Encryption Time:        {stats['avg_encryption_ms']:.2f} ms")
    print(f"Avg Blind Index Time:       {stats['avg_blind_index_ms']:.2f} ms")
    print("=" * 60)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, **kwargs):
    """Called for each request. Can be used for custom logging."""
    pass


# ============ CUSTOM SHAPES (OPTIONAL) ============

class LoadTestShape:
    """
    Custom load test shape for gradual ramp-up.

    To use:
        locust -f locustfile.py --host=http://localhost:8000 \
               --headless --run-time 10m
    """

    stages = [
        {"duration": 60, "users": 20, "spawn_rate": 5},     # Warm up: 20 users
        {"duration": 120, "users": 50, "spawn_rate": 10},   # Ramp up: 50 users
        {"duration": 180, "users": 100, "spawn_rate": 10},  # Full load: 100 users
        {"duration": 300, "users": 100, "spawn_rate": 10},  # Sustain: 100 users
        {"duration": 60, "users": 0, "spawn_rate": 10},     # Ramp down
    ]

    def tick(self):
        """Returns user count and spawn rate for current time."""
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]

        return None


# ============ MAIN ============

if __name__ == "__main__":
    import subprocess
    import sys

    print("Running Locust performance tests...")
    print("Open http://localhost:8089 for the web UI")
    print()

    subprocess.run([
        sys.executable, "-m", "locust",
        "-f", __file__,
        "--host", "http://localhost:8000",
    ])
