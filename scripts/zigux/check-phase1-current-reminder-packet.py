#!/usr/bin/env python3
"""Guard the ordered Phase 1 current reminder packet roster."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
CLOSURE_NOTE = "Documentation/zigux/phase1-closure.md"

REQUIRED_PACKET = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_helpers_build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
)

PACKET_PREFIX = "- `PHASE1_CURRENT_REMINDER_PACKET="


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def packet_line(closure_note: str) -> str | None:
    matches = [line for line in closure_note.splitlines() if line.startswith(PACKET_PREFIX)]
    if len(matches) != 1:
        return None
    return matches[0]


def parse_packet(line: str) -> list[str]:
    packet = line.removeprefix(PACKET_PREFIX)
    if not packet.endswith("`"):
        return []
    return [entry.strip() for entry in packet[:-1].split(",")]


def collect_missing_materialized_paths(root: Path, packet: tuple[str, ...]) -> list[str]:
    return [relative_path for relative_path in packet if not (root / relative_path).is_file()]


def collect_packet_issues(root: Path) -> list[str]:
    issues: list[str] = []
    try:
        closure_note = read_text(root, CLOSURE_NOTE)
    except FileNotFoundError:
        return [f"missing_file:{CLOSURE_NOTE}"]

    line = packet_line(closure_note)
    if line is None:
        issues.append("phase1_current_reminder_packet_line:expected=1")
        packet: list[str] = []
    else:
        packet = parse_packet(line)
        if tuple(packet) != REQUIRED_PACKET:
            issues.append(
                "phase1_current_reminder_packet:"
                f"expected={','.join(REQUIRED_PACKET)}:actual={','.join(packet)}"
            )

    materialized = collect_missing_materialized_paths(root, REQUIRED_PACKET)
    issues.extend(f"missing_materialized_path:{relative_path}" for relative_path in materialized)
    return issues


def write_file(root: Path, relative_path: str, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def closure_text(packet: tuple[str, ...] = REQUIRED_PACKET, duplicate: bool = False) -> str:
    line = f"{PACKET_PREFIX}{','.join(packet)}`"
    lines = ["# Phase 1 Closure", "", line]
    if duplicate:
        lines.append(line)
    lines.append("")
    return "\n".join(lines)


def materialize_packet(root: Path, packet: tuple[str, ...] = REQUIRED_PACKET) -> None:
    for relative_path in packet:
        write_file(root, relative_path, f"fixture for {relative_path}\n")
    write_file(root, CLOSURE_NOTE, closure_text(packet))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        materialize_packet(root)
        assert collect_packet_issues(root) == []

        write_file(root, CLOSURE_NOTE, closure_text(REQUIRED_PACKET[1:] + REQUIRED_PACKET[:1]))
        assert any(issue.startswith("phase1_current_reminder_packet:") for issue in collect_packet_issues(root))

        write_file(root, CLOSURE_NOTE, closure_text(duplicate=True))
        assert "phase1_current_reminder_packet_line:expected=1" in collect_packet_issues(root)

        write_file(root, CLOSURE_NOTE, closure_text())
        (root / REQUIRED_PACKET[-1]).unlink()
        assert f"missing_materialized_path:{REQUIRED_PACKET[-1]}" in collect_packet_issues(root)

    print("PHASE1_CURRENT_REMINDER_PACKET_SELF_TEST=pass")
    print("PHASE1_CURRENT_REMINDER_PACKET_REQUIRED_PATH_COUNT=18")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="Repository root to check")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    issues = collect_packet_issues(root)
    if issues:
        print("PHASE1_CURRENT_REMINDER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE1_CURRENT_REMINDER_PACKET=pass")
    print("PHASE1_CURRENT_REMINDER_PACKET_REQUIRED_PATH_COUNT=18")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
