"""Educational CPU scheduling simulator: FCFS, non-preemptive SJF and RR."""

from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class Process:
    pid: str
    arrival: int
    burst: int

    def __post_init__(self) -> None:
        if not self.pid or self.arrival < 0 or self.burst <= 0:
            raise ValueError("进程需要非空 id、非负到达时间和正执行时间")


@dataclass(frozen=True)
class Slice:
    pid: str
    start: int
    end: int


def _append_slice(timeline: List[Slice], pid: str, start: int, end: int) -> None:
    if start == end:
        return
    if timeline and timeline[-1].pid == pid and timeline[-1].end == start:
        previous = timeline[-1]
        timeline[-1] = Slice(pid, previous.start, end)
    else:
        timeline.append(Slice(pid, start, end))


def fcfs(processes: Iterable[Process]) -> List[Slice]:
    """First-come-first-served, breaking equal arrivals by process id."""
    time, timeline = 0, []
    for process in sorted(processes, key=lambda item: (item.arrival, item.pid)):
        if time < process.arrival:
            _append_slice(timeline, "IDLE", time, process.arrival)
            time = process.arrival
        _append_slice(timeline, process.pid, time, time + process.burst)
        time += process.burst
    return timeline


def sjf(processes: Iterable[Process]) -> List[Slice]:
    """Non-preemptive shortest-job-first scheduling."""
    pending = sorted(processes, key=lambda item: (item.arrival, item.pid))
    time, timeline, ready = 0, [], []
    while pending or ready:
        while pending and pending[0].arrival <= time:
            ready.append(pending.pop(0))
        if not ready:
            next_arrival = pending[0].arrival
            _append_slice(timeline, "IDLE", time, next_arrival)
            time = next_arrival
            continue
        ready.sort(key=lambda item: (item.burst, item.arrival, item.pid))
        process = ready.pop(0)
        _append_slice(timeline, process.pid, time, time + process.burst)
        time += process.burst
    return timeline


def round_robin(processes: Iterable[Process], quantum: int) -> List[Slice]:
    """Round-robin scheduling with a positive integer time quantum."""
    if quantum <= 0:
        raise ValueError("时间片必须为正整数")
    pending = sorted(processes, key=lambda item: (item.arrival, item.pid))
    remaining = {process.pid: process.burst for process in pending}
    ready: deque[Process] = deque()
    time, timeline = 0, []
    while pending or ready:
        while pending and pending[0].arrival <= time:
            ready.append(pending.pop(0))
        if not ready:
            next_arrival = pending[0].arrival
            _append_slice(timeline, "IDLE", time, next_arrival)
            time = next_arrival
            continue
        process = ready.popleft()
        duration = min(quantum, remaining[process.pid])
        _append_slice(timeline, process.pid, time, time + duration)
        time += duration
        remaining[process.pid] -= duration
        while pending and pending[0].arrival <= time:
            ready.append(pending.pop(0))
        if remaining[process.pid] > 0:
            ready.append(process)
    return timeline


def metrics(processes: Iterable[Process], timeline: Iterable[Slice]) -> List[dict]:
    """Calculate completion, turnaround, waiting and response time for each process."""
    process_map = {process.pid: process for process in processes}
    executions = {pid: [] for pid in process_map}
    for item in timeline:
        if item.pid in executions:
            executions[item.pid].append(item)
    result = []
    for pid in sorted(process_map):
        process, slices = process_map[pid], executions[pid]
        completion = slices[-1].end
        turnaround = completion - process.arrival
        result.append({
            "pid": pid, "completion": completion, "turnaround": turnaround,
            "waiting": turnaround - process.burst, "response": slices[0].start - process.arrival,
        })
    return result


def load_processes(source: Path) -> List[Process]:
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("输入 JSON 必须是进程数组")
    return [Process(str(item["id"]), int(item["arrival"]), int(item["burst"])) for item in data]


def render(timeline: Iterable[Slice], results: Iterable[dict]) -> str:
    chart = " | ".join(f"{item.start}-{item.end}:{item.pid}" for item in timeline)
    rows = ["进程  完成  周转  等待  响应"]
    rows.extend(f"{row['pid']:<5} {row['completion']:<5} {row['turnaround']:<5} {row['waiting']:<5} {row['response']:<5}" for row in results)
    return "甘特图\n" + chart + "\n\n" + "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="CPU 调度算法模拟器")
    parser.add_argument("input", type=Path, help="进程 JSON 文件")
    parser.add_argument("--algorithm", choices=("fcfs", "sjf", "rr"), default="fcfs")
    parser.add_argument("--quantum", type=int, default=2, help="RR 时间片，默认 2")
    args = parser.parse_args()
    try:
        processes = load_processes(args.input)
        timeline = {"fcfs": fcfs, "sjf": sjf}.get(args.algorithm, lambda items: round_robin(items, args.quantum))(processes)
        print(render(timeline, metrics(processes, timeline)))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

