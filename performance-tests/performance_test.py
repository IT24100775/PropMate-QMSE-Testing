import json
import time
import statistics
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

API_SEARCH_URL = "http://localhost:5235/api/PropertyListings"
AI_URL = "http://localhost:8001/verify-listing"
DISCOVERY_URL = "http://localhost:8002/api/agent/discover"

CONCURRENT_REQUESTS = 20
WORKERS = 5


def request(url, method="GET", data=None):
    body = None
    headers = {}

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    start = time.perf_counter()

    try:
        req = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            response.read()

        elapsed_ms = (time.perf_counter() - start) * 1000
        return True, elapsed_ms

    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return False, elapsed_ms


def run_load_test(name, url, method="GET", data=None):
    print(f"\n=== {name} ===")
    print(f"Requests: {CONCURRENT_REQUESTS}")
    print(f"Concurrent workers: {WORKERS}")

    results = []

    start_total = time.perf_counter()

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [
            executor.submit(request, url, method, data)
            for _ in range(CONCURRENT_REQUESTS)
        ]

        for future in as_completed(futures):
            results.append(future.result())

    total_seconds = time.perf_counter() - start_total

    successful = [ms for ok, ms in results if ok]
    failed = [ms for ok, ms in results if not ok]

    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    print(f"Success rate: {(len(successful) / len(results)) * 100:.2f}%")
    print(f"Total duration: {total_seconds:.2f}s")

    if successful:
        print(f"Average response: {statistics.mean(successful):.2f} ms")
        print(f"Minimum response: {min(successful):.2f} ms")
        print(f"Maximum response: {max(successful):.2f} ms")
        print(f"Median response: {statistics.median(successful):.2f} ms")


ai_payload = {
    "listing_id": 99999,
    "owner_id": 1,
    "title": "Performance Test Apartment",
    "description": "Valid property listing used only for PropMate performance testing.",
    "purpose": "Rent",
    "property_type": "Apartment",
    "price": 150000,
    "address": "100 Galle Road",
    "city": "Colombo",
    "latitude": 6.9271,
    "longitude": 79.8612,
    "bedrooms": 3,
    "bathrooms": 2,
    "image_urls": [
    	"https://example.com/performance-test-property.jpg"
    ]
}


print("PropMate Performance Test")
print("=========================")

run_load_test(
    "Database-backed Property Search API",
    API_SEARCH_URL
)

run_load_test(
    "Property Verification Agent",
    AI_URL,
    method="POST",
    data=ai_payload
)

discovery_payload = {
    "query": "Find apartments for rent in Colombo with 2 bedrooms"
}

run_load_test(
    "Property Discovery & Viewing Agent",
    DISCOVERY_URL,
    method="POST",
    data=discovery_payload
)

maintenance_payload = {
    "maintenance_request_id": 10,
    "objective": "Analyze the maintenance request and recommend a suitable technician and schedule"
}

def run_maintenance_performance_test():
    global CONCURRENT_REQUESTS, WORKERS

    original_requests = CONCURRENT_REQUESTS
    original_workers = WORKERS

    try:
        CONCURRENT_REQUESTS = 5
        WORKERS = 1

        run_load_test(
            "Maintenance Coordination Agent",
            "http://127.0.0.1:8004/api/maintenance-ai/run",
            method="POST",
            data=maintenance_payload
        )
    finally:
        CONCURRENT_REQUESTS = original_requests
        WORKERS = original_workers

run_maintenance_performance_test()
