#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=zar_runtime_research_absorption

Fail-closed checker for the Phase 14 ZAR runtime research absorption note.

The checker keeps the note bounded to architecture research absorption:
ZAR runtime layering may inform boundary maps and audit language, but it must
not become a Phase 14 bridge, parity, ownership, or freeze-map status claim.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=zar_runtime_research_absorption"
NOTE_PATH = Path("Documentation/zigux/phase14-zar-runtime-research-absorption.md")

NOTE_MARKERS = [
    "`PHASE14_LANE_KEY=P14-L06`",
    "`PHASE14_SOURCE=ZAR-Zig-Agent-Runtime-main/docs/architecture.md`",
    "gateway and dispatcher layering maps only to review-boundary vocabulary",
    "bounded in-memory histories and compact retention map only to audit prompts for workqueue and ring-buffer study notes",
    "secret-store fallback reporting maps only to explicit stay-in-C and unsupported-backend wording",
    "bare-metal ABI lifecycle hooks map only to ABI-boundary review prompts",
    "does not add `kernel/workqueue_bridge.zig`, `kernel/trace/ring_buffer.zig`, `net/core/skbuff_bridge.zig`, or `kernel/rcu/tree_bridge.zig`",
    "does not change the freeze map, Architecture Council posture, or Phase 15 governance packet",
]

ABSENT_CLAIMS = [
    "PHASE14_STATUS=parity",
    "PHASE14_STATUS=implementation_ready",
    "workqueue parity is ready",
    "ring buffer parity is ready",
    "skbuff ownership transferred",
    "rcu tree ownership transferred",
]


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def checker_text() -> str:
    path = Path(__file__)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return __doc__ or ""


def require_note(errors: list[str], text: str) -> None:
    for marker in NOTE_MARKERS:
        if marker not in text:
            errors.append(f"missing_marker:{NOTE_PATH.as_posix()}:{marker}")
    for claim in ABSENT_CLAIMS:
        if claim in text:
            errors.append(f"forbidden_claim:{NOTE_PATH.as_posix()}:{claim}")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    if MARKER not in checker_text():
        errors.append("missing_checker_marker:self")
    try:
        note = read_text(root, NOTE_PATH)
    except FileNotFoundError:
        return [f"missing_file:{NOTE_PATH.as_posix()}"]
    require_note(errors, note)
    return errors


def fixture_note() -> str:
    return "\n".join(
        [
            "# Phase 14 ZAR Runtime Research Absorption",
            "",
            "## Status",
            "- `PHASE14_LANE_KEY=P14-L06`",
            "- `PHASE14_SOURCE=ZAR-Zig-Agent-Runtime-main/docs/architecture.md`",
            "",
            "## Absorbed boundaries",
            "- gateway and dispatcher layering maps only to review-boundary vocabulary",
            "- bounded in-memory histories and compact retention map only to audit prompts for workqueue and ring-buffer study notes",
            "- secret-store fallback reporting maps only to explicit stay-in-C and unsupported-backend wording",
            "- bare-metal ABI lifecycle hooks map only to ABI-boundary review prompts",
            "",
            "## Non-goals",
            "This note does not add `kernel/workqueue_bridge.zig`, `kernel/trace/ring_buffer.zig`, `net/core/skbuff_bridge.zig`, or `kernel/rcu/tree_bridge.zig`.",
            "It does not change the freeze map, Architecture Council posture, or Phase 15 governance packet.",
            "",
        ]
    )


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-zar-runtime-research-"))
    try:
        write_text(base, NOTE_PATH, fixture_note())
        errors = check(base)
        if errors:
            print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        write_text(base, NOTE_PATH, fixture_note().replace(NOTE_MARKERS[1], "", 1))
        if not any(NOTE_MARKERS[1] in error for error in check(base)):
            print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_SELF_TEST=fail")
            print("expected source marker drift to fail")
            return 1

        write_text(base, NOTE_PATH, fixture_note() + "\nPHASE14_STATUS=parity\n")
        if not any(error.endswith("PHASE14_STATUS=parity") for error in check(base)):
            print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_SELF_TEST=fail")
            print("expected forbidden parity claim to fail")
            return 1

        write_text(base, NOTE_PATH, fixture_note().replace(NOTE_MARKERS[6], "", 1))
        if not any(NOTE_MARKERS[6] in error for error in check(base)):
            print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_SELF_TEST=fail")
            print("expected non-goal marker drift to fail")
            return 1

        print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_SELF_TEST=pass")
        print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_SELF_TEST_CASE_COUNT=3")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION=fail")
        print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_ISSUES_END")
        return 1

    print("PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION=pass")
    print(f"PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE14_ZAR_RUNTIME_RESEARCH_ABSORPTION_FORBIDDEN_CLAIM_COUNT={len(ABSENT_CLAIMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
