#!/usr/bin/env python3
"""
VoxParaguay 2026 - Mock Data Stream Generator
Generates simulated sentiment data for development and testing

Usage:
    python scripts/mock_data_stream.py [--rate 2.5] [--url http://localhost:8000]
"""

import argparse
import asyncio
import random
import time
from datetime import datetime
from typing import Optional

import httpx

# ============ PARAGUAY DEPARTMENTS ============
# ISO 3166-2:PY codes for all 17 departments + capital district

PARAGUAY_DEPARTMENTS = {
    # Capital District
    "PY-ASU": {"name": "Asunción", "region": "Capital"},
    # Región Oriental
    "PY-1": {"name": "Concepción", "region": "Oriental"},
    "PY-2": {"name": "San Pedro", "region": "Oriental"},
    "PY-3": {"name": "Cordillera", "region": "Oriental"},
    "PY-4": {"name": "Guairá", "region": "Oriental"},
    "PY-5": {"name": "Caaguazú", "region": "Oriental"},
    "PY-6": {"name": "Caazapá", "region": "Oriental"},
    "PY-7": {"name": "Itapúa", "region": "Oriental"},
    "PY-8": {"name": "Misiones", "region": "Oriental"},
    "PY-9": {"name": "Paraguarí", "region": "Oriental"},
    "PY-10": {"name": "Alto Paraná", "region": "Oriental"},
    "PY-11": {"name": "Central", "region": "Oriental"},
    "PY-12": {"name": "Ñeembucú", "region": "Oriental"},
    "PY-13": {"name": "Amambay", "region": "Oriental"},
    "PY-14": {"name": "Canindeyú", "region": "Oriental"},
    # Región Occidental (Chaco)
    "PY-15": {"name": "Presidente Hayes", "region": "Occidental"},
    "PY-16": {"name": "Alto Paraguay", "region": "Occidental"},
    "PY-19": {"name": "Boquerón", "region": "Occidental"},
}

DEPARTMENT_IDS = list(PARAGUAY_DEPARTMENTS.keys())

# ============ MOCK DATA GENERATION ============

# Sample survey topics
TOPICS = [
    "economia",
    "salud",
    "educacion",
    "seguridad",
    "infraestructura",
    "empleo",
    "corrupcion",
    "medio_ambiente",
]

# Sample channels
CHANNELS = ["voice", "whatsapp", "facebook", "instagram"]


def generate_mock_response() -> dict:
    """
    Generate a single mock survey response with sentiment data.

    Returns:
        dict: Mock response data ready for POST to /ingest
    """
    dept_id = random.choice(DEPARTMENT_IDS)
    dept_info = PARAGUAY_DEPARTMENTS[dept_id]

    # Generate random sentiment score (-1 to 1)
    # Slightly bias toward neutral to make distribution realistic
    sentiment = random.gauss(0, 0.4)
    sentiment = max(-1.0, min(1.0, sentiment))  # Clamp to [-1, 1]

    return {
        "department_id": dept_id,
        "department_name": dept_info["name"],
        "region": dept_info["region"],
        "sentiment_score": round(sentiment, 3),
        "topic": random.choice(TOPICS),
        "channel": random.choice(CHANNELS),
        "timestamp": datetime.now().isoformat(),
        "response_id": f"mock-{int(time.time() * 1000)}-{random.randint(1000, 9999)}",
    }


async def send_response(
    client: httpx.AsyncClient,
    url: str,
    data: dict,
    verbose: bool = True
) -> bool:
    """
    Send a single response to the ingest endpoint.

    Args:
        client: HTTP client
        url: Ingest endpoint URL
        data: Response data
        verbose: Print status messages

    Returns:
        bool: True if successful
    """
    try:
        response = await client.post(url, json=data, timeout=5.0)

        if response.status_code == 200:
            if verbose:
                dept = data["department_id"]
                name = data["department_name"]
                sentiment = data["sentiment_score"]
                sentiment_str = f"+{sentiment:.2f}" if sentiment >= 0 else f"{sentiment:.2f}"
                color = "\033[92m" if sentiment >= 0 else "\033[91m"
                reset = "\033[0m"
                print(f"  ✓ {dept} ({name}): {color}{sentiment_str}{reset} | {data['topic']}")
            return True
        else:
            if verbose:
                print(f"  ✗ Error {response.status_code}: {response.text}")
            return False

    except httpx.TimeoutException:
        if verbose:
            print("  ✗ Request timeout")
        return False
    except httpx.ConnectError:
        if verbose:
            print("  ✗ Connection error - is the backend running?")
        return False
    except Exception as e:
        if verbose:
            print(f"  ✗ Error: {e}")
        return False


async def run_data_stream(
    base_url: str = "http://localhost:8000",
    rate: float = 2.5,
    duration: Optional[int] = None,
    verbose: bool = True,
) -> None:
    """
    Run continuous mock data stream.

    Args:
        base_url: Backend API base URL
        rate: Average responses per second (will vary 2-3)
        duration: Run for N seconds (None = infinite)
        verbose: Print status messages
    """
    ingest_url = f"{base_url}/api/v1/responses/ingest"

    print("=" * 60)
    print("VoxParaguay 2026 - Mock Data Stream")
    print("=" * 60)
    print(f"Target URL:   {ingest_url}")
    print(f"Rate:         ~{rate} responses/second")
    print(f"Departments:  {len(DEPARTMENT_IDS)} total")
    print(f"Duration:     {'Infinite' if duration is None else f'{duration}s'}")
    print("=" * 60)
    print()
    print("Press Ctrl+C to stop...")
    print()

    start_time = time.time()
    total_sent = 0
    total_errors = 0

    async with httpx.AsyncClient() as client:
        try:
            while True:
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    break

                # Generate 2-3 responses per batch
                batch_size = random.randint(2, 3)
                batch_start = time.time()

                for _ in range(batch_size):
                    data = generate_mock_response()
                    success = await send_response(client, ingest_url, data, verbose)

                    if success:
                        total_sent += 1
                    else:
                        total_errors += 1

                # Sleep to maintain rate (1 second minus processing time)
                elapsed = time.time() - batch_start
                sleep_time = max(0, 1.0 - elapsed)
                await asyncio.sleep(sleep_time)

                # Periodic summary
                if total_sent > 0 and total_sent % 50 == 0:
                    elapsed_total = time.time() - start_time
                    actual_rate = total_sent / elapsed_total
                    print()
                    print(f"  [Summary] Sent: {total_sent} | Errors: {total_errors} | Rate: {actual_rate:.1f}/s")
                    print()

        except KeyboardInterrupt:
            pass

    # Final summary
    elapsed_total = time.time() - start_time
    actual_rate = total_sent / elapsed_total if elapsed_total > 0 else 0

    print()
    print("=" * 60)
    print("Stream stopped.")
    print(f"Total sent:     {total_sent}")
    print(f"Total errors:   {total_errors}")
    print(f"Duration:       {elapsed_total:.1f}s")
    print(f"Actual rate:    {actual_rate:.1f} responses/second")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="VoxParaguay 2026 - Mock Data Stream Generator"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Backend API base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--rate",
        type=float,
        default=2.5,
        help="Average responses per second (default: 2.5)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Run for N seconds (default: infinite)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-response output",
    )

    args = parser.parse_args()

    asyncio.run(
        run_data_stream(
            base_url=args.url,
            rate=args.rate,
            duration=args.duration,
            verbose=not args.quiet,
        )
    )


if __name__ == "__main__":
    main()
