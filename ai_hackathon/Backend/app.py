"""Local non-API test entrypoint for the multimodal orchestration flow."""

import logging

from orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


if __name__ == "__main__":
    input_text = """
    Short Description

    High CPU utilization on application servers causing increased latency

    Detailed Description

    We are observing sustained high CPU usage on production application servers over the
    past 30 minutes, leading to degraded performance and increased API response times.

    Key observations:

    CPU utilization consistently above 90% across multiple instances
    API latency (p95) increased from ~120ms to ~900ms
    Error rate has slightly increased (~3–5%) due to request timeouts

    Log:
    2026-04-08 10:02:11 INFO  [app.server] Starting request_id=abc123 endpoint=/search user_id=981
    2026-04-08 10:02:11 DEBUG [app.service] Running aggregation for user_id=981
    2026-04-08 10:02:12 WARN  [app.performance] Function=aggregate_data execution_time=850ms threshold=200ms
    2026-04-08 10:02:13 WARN  [app.performance] High CPU usage detected: cpu=92% instance=app-1
    2026-04-08 10:02:14 INFO  [app.server] Completed request_id=abc123 status=200 latency=910ms

    2026-04-08 10:02:15 INFO  [app.server] Starting request_id=abc124 endpoint=/recommendations user_id=442
    2026-04-08 10:02:16 DEBUG [app.service] Running aggregation for user_id=442
    2026-04-08 10:02:17 WARN  [app.performance] Function=aggregate_data execution_time=910ms threshold=200ms
    2026-04-08 10:02:17 WARN  [app.performance] High CPU usage detected: cpu=95% instance=app-2
    2026-04-08 10:02:18 ERROR [app.server] Request failed request_id=abc124 error=timeout

    2026-04-08 10:02:20 INFO  [metrics] cpu_usage=93% memory_usage=65% disk_io=40% network_latency=20ms
    2026-04-08 10:02:25 INFO  [metrics] cpu_usage=91% memory_usage=67% disk_io=42% network_latency=18ms

    2026-04-08 10:02:30 WARN  [app.performance] Thread pool saturation detected active_threads=200 max_threads=200
    2026-04-08 10:02:32 DEBUG [app.service] Retrying aggregation for user_id=442
    2026-04-08 10:02:35 WARN  [app.performance] High CPU usage persists: cpu=96% instance=app-1

    2026-04-08 10:02:40 INFO  [deploy] Version=2.3.1 deployed at 09:55:00
    """

    # Leave these as None or [] for a text-only run. When supplied, speech is
    # transcribed first and screenshots are analyzed first before the text
    # pipeline continues.
    audio_path = None
    image_paths = []

    orchestrator = Orchestrator()
    result = orchestrator.run(
        input_text=input_text.strip(),
        audio_path=audio_path,
        image_paths=image_paths,
    )

    # The final report is printed once for the CLI consumer, while step-level
    # model outputs are already captured in the structured logger.
    print(result["final_output"])
