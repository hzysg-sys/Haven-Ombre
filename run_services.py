"""Run Ombre Brain and Gateway together in one container."""

from __future__ import annotations

import signal
import subprocess
import sys
import time


def _terminate(processes: list[subprocess.Popen[bytes]]) -> None:
    for process in processes:
        if process.poll() is None:
            process.terminate()

    deadline = time.monotonic() + 10
    for process in processes:
        if process.poll() is not None:
            continue
        try:
            process.wait(timeout=max(0.0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def main() -> int:
    processes: list[subprocess.Popen[bytes]] = []
    stopping = False

    def stop(_signum: int, _frame: object) -> None:
        nonlocal stopping
        stopping = True
        _terminate(processes)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    for entrypoint in ("server.py", "gateway.py"):
        processes.append(subprocess.Popen([sys.executable, entrypoint]))

    try:
        while not stopping:
            exited = next((p for p in processes if p.poll() is not None), None)
            if exited is not None:
                return int(exited.returncode or 1)
            time.sleep(1)
    finally:
        _terminate(processes)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
