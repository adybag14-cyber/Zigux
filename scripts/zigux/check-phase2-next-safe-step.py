#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
SECTION_HEADER = "## Next Step"
SENTINEL_PREFIX = "PHASE2_NEXT_SAFE_STEP="
EXPECTED_SENTINEL = (
    "keep the shared Phase 2 closure packet parked unless one shared reminder "
    "surface drifts again; if the shared backlog reopens first, start with one "
    "smallest truthfulness repair in Documentation/zigux/README.md, "
    "zigux/tests/README.md, or the directly coupled shared checker that proves "
    "the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through "
    "in their dedicated lanes"
)
REQUIRED_SECTION_MARKERS = (
    "The next bounded same-lane follow-through is to keep the shared Phase 2 closure packet parked unless one shared reminder surface drifts again.",
    "If current `master` reopens the shared backlog first, start with one smallest truthfulness repair in `Documentation/zigux/README.md`, `zigux/tests/README.md`, or the directly coupled shared checker that proves the drift, and keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes instead of sending this shared packet back through the already-covered toolchain-pinning-versus-`phase2-fixdep` comparison.",
    "`Documentation/zigux/README.md`",
    "`zigux/tests/README.md`",
    "directly coupled shared checker",
    "keep fixdep-, genksyms-, and kconfig-local follow-through in their dedicated lanes",
    "toolchain-pinning-versus-`phase2-fixdep` comparison",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def extract_next_step(text: str) -> str:
    start = SECTION_HEADER + "\n"
    if start not in text:
        raise SystemExit(f"required note section missing: {PHASE2_CLOSURE_REL}: {SECTION_HEADER}")
    after_start = text.split(start, 1)[1]
    return after_start


def extract_sentinel_payload(text: str) -> str | None:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        candidate = line
        if candidate.startswith("- "):
            candidate = candidate[2:].strip()
        if candidate.startswith("`") and candidate.endswith("`"):
            candidate = candidate[1:-1]
        if candidate.startswith(SENTINEL_PREFIX):
            return candidate[len(SENTINEL_PREFIX) :]
    return None


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    next_step_text = extract_next_step(closure_text)
    issues: list[tuple[str, str]] = []

    sentinel_payload = extract_sentinel_payload(next_step_text)
    if sentinel_payload is None:
        issues.append(("MISSING_SENTINEL", SENTINEL_PREFIX))
    elif sentinel_payload != EXPECTED_SENTINEL:
        issues.append(("MISMATCHED_SENTINEL", sentinel_payload))

    sentinel_line = f"`{SENTINEL_PREFIX}{EXPECTED_SENTINEL}`"
    sentinel_count = count_exact_lines(next_step_text, f"- {sentinel_line}")
    if sentinel_count != 1:
        issues.append(("EXACT_SENTINEL_COUNT", f"{sentinel_count}::{sentinel_line}"))

    header_count = count_exact_lines(closure_text, SECTION_HEADER)
    if header_count != 1:
        issues.append(("EXACT_HEADER_COUNT", f"{header_count}::{SECTION_HEADER}"))

    for marker in REQUIRED_SECTION_MARKERS:
        if marker not in next_step_text:
            issues.append(("MISSING_SECTION_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_NEXT_SAFE_STEP=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    text = (
        "# Phase 2 Closure\n\n"
        "## Next Step\n\n"
        f"{REQUIRED_SECTION_MARKERS[0]}\n\n"
        f"{REQUIRED_SECTION_MARKERS[1]}\n\n"
        f"- `{SENTINEL_PREFIX}{EXPECTED_SENTINEL}`\n"
    )
    write_text(root / PHASE2_CLOSURE_REL, text)


def write_sample_root(root: Path) -> int:
    build_self_test_root(root)
    print(f"PHASE2_NEXT_SAFE_STEP_SAMPLE_ROOT={root}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_next_safe_step_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(closure_path.read_text(encoding="utf-8"), SENTINEL_PREFIX + EXPECTED_SENTINEL),
            encoding="utf-8",
        )
        assert ("MISSING_SENTINEL", SENTINEL_PREFIX) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`Documentation/zigux/README.md`",
                "`Documentation/zigux/phase2-toolchain-bootstrap-notes.md`",
            ),
            encoding="utf-8",
        )
        issues = collect_issues(root)
        assert ("MISSING_SECTION_MARKER", "`Documentation/zigux/README.md`") in issues
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "toolchain-pinning-versus-`phase2-fixdep` comparison",
                "shared comparison",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_SECTION_MARKER",
            "toolchain-pinning-versus-`phase2-fixdep` comparison",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "## Next Step\n", "## Next Step\n## Next Step\n", 1
            ),
            encoding="utf-8",
        )
        assert ("EXACT_HEADER_COUNT", f"2::{SECTION_HEADER}") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        sentinel_line = f"`{SENTINEL_PREFIX}{EXPECTED_SENTINEL}`"
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                f"- {sentinel_line}\n",
                f"- {sentinel_line}\n- {sentinel_line}\n",
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "EXACT_SENTINEL_COUNT",
            f"2::{sentinel_line}",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_NEXT_SAFE_STEP_SELF_TEST=pass")
    print(f"PHASE2_NEXT_SAFE_STEP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note next-safe-step contract aligned."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_NEXT_SAFE_STEP=pass")
    print(f"PHASE2_NEXT_SAFE_STEP_MARKER_COUNT={len(REQUIRED_SECTION_MARKERS)}")
    print("PHASE2_NEXT_SAFE_STEP_SENTINEL_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
