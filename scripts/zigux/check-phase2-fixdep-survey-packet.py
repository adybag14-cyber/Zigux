#!/usr/bin/env python3
"""Guard the live Phase 2 fixdep survey packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

SURVEY = Path("Documentation/zigux/phase2-fixdep-dual-implementation-survey.md")
HELPER = Path("scripts/zigux/fixdep.zig")
GATE = Path("scripts/zigux/check-phase2-fixdep-gate.py")
DIFF = Path("scripts/zigux/check-fixdep-diff.py")
VALIDATOR = Path("scripts/zigux/validate-phase2.py")
ARTIFACT_DIFF_NOTE = Path("Documentation/zigux/artifact-diff.md")
CLOSURE = Path("Documentation/zigux/phase2-closure.md")
TESTS_README = Path("zigux/tests/README.md")
CASES = Path("zigux/tests/fixtures/fixdep/cases.json")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_PATHS = (
    str(SURVEY),
    str(HELPER),
    str(GATE),
    str(DIFF),
    str(VALIDATOR),
    str(ARTIFACT_DIFF_NOTE),
    str(CLOSURE),
    str(TESTS_README),
    str(CASES),
    str(MAKEFILE),
    str(WORKFLOW),
)

SURVEY_MARKERS = (
    "Current `master` still directly serves `scripts/zigux/fixdep.zig`",
    "Current `master` also directly serves `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/validate-phase2.py`",
    "Current `master` directly serves `zigux/tests/fixtures/fixdep/cases.json`",
    "The live `zigux/Makefile` still exposes `phase2-fixdep`",
    "The live `.github/workflows/zigux-bootstrap.yml` still replays the same fixdep packet",
    "The shared reminder packet in `Documentation/zigux/phase2-closure.md` and `zigux/tests/README.md` now also treats the fixdep helper, parity checker, fixture roster, and wrapper route as current repo evidence.",
    "Current `master` now directly serves `Documentation/zigux/artifact-diff.md`",
    "Repeated exact-path contents reads still return missing for `scripts/basic/fixdep.c`",
    "The bounded fixdep packet is now thirteen cases wide",
    "The live repo also no longer supports the older survey claim that `Documentation/zigux/artifact-diff.md` is missing",
    "Keep `P2-L01` parked unless a fresh current-`master` reread finds new repo-versus-roadmap drift inside the fixdep helper, checker, fixture, or route packet.",
)

TESTS_README_MARKERS = (
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/fixdep.zig`",
    "`make -C zigux phase2-fixdep`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
)

MAKEFILE_LINES = (
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
)

WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: make -C zigux phase2-fixdep",
)

EXPECTED_CASE_NAMES = (
    "sample",
    "sample_multi_target",
    "sample_escaped_space",
    "sample_escaped_colon",
    "sample_concatenated",
    "sample_dependency_continuation",
    "sample_comment_continuation",
    "sample_double_backslash_comment",
    "sample_comment_only",
    "sample_comment_only_stdout_full",
    "sample_missing_dep",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
)

EXPECTED_STDOUT_FULL_CASES = (
    "sample_comment_only_stdout_full",
    "sample_missing_dep_stdout_full",
    "sample_output_write",
)

EXPECTED_MISSING_DEPFILE = "scripts/basic/fixdep.c"

SAMPLE_SURVEY = """# Phase 2 fixdep dual-implementation survey

Lane: `P2-L01`

## Roadmap and ledger anchor

- The Phase 2 roadmap still keeps `scripts/basic/fixdep.c` and `scripts/zigux/fixdep.zig` inside the selected dual-implementation tranche for toolchain and kbuild enablement.
- The bootstrap ledger still records a bounded fixdep lane around `scripts/zigux/fixdep.zig` together with the dedicated parity checker, fixture packet, and wrapper-backed follow-through, so this family remains real product infrastructure rather than churn.

## Current repo evidence

- Current `master` still directly serves `scripts/zigux/fixdep.zig`, so the core dual-implementation helper remains present on head.
- Current `master` also directly serves `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `scripts/zigux/validate-phase2.py`, so the helper, dedicated gate, parity checker, and shared Phase 2 validator packet are all materialized together.
- Current `master` directly serves `zigux/tests/fixtures/fixdep/cases.json`, which now carries the bounded thirteen-case external fixdep packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_double_backslash_comment`, and the current `/dev/full` stdout-failure replays.
- The live `zigux/Makefile` still exposes `phase2-fixdep` with the dedicated fixdep gate self-test, fixdep gate run, fixdep diff self-test, fixdep diff run, and `zig test scripts/zigux/fixdep.zig` replay.
- The live `.github/workflows/zigux-bootstrap.yml` still replays the same fixdep packet on current `master` through the dedicated gate self-test and run, the fixdep diff self-test and run, `make -C zigux phase2-fixdep`, and the direct `zig test scripts/zigux/fixdep.zig` step.
- The shared reminder packet in `Documentation/zigux/phase2-closure.md` and `zigux/tests/README.md` now also treats the fixdep helper, parity checker, fixture roster, and wrapper route as current repo evidence.
- Current `master` now directly serves `Documentation/zigux/artifact-diff.md`, so the older reminder-side companion gap recorded in this survey is no longer live.
- Repeated exact-path contents reads still return missing for `scripts/basic/fixdep.c`, so the remaining narrow same-family limitation is the readable C-anchor question rather than any missing Zigux-side fixdep packet.

## Survey result

- The roadmap-backed dual-implementation gap for `scripts/zigux/fixdep.zig` is currently closed on `master`.
- The live repo no longer supports the older survey claim that the fixdep fixture packet stops at twelve external cases. The bounded fixdep packet is now thirteen cases wide and already includes the later dependency-continuation, comment-continuation, and double-backslash-comment parity paths.
- The live repo also no longer supports the older survey claim that `Documentation/zigux/artifact-diff.md` is missing: current authenticated contents readback now returns that reminder-side companion directly on `master`.
- The honest remaining same-family follow-through is smaller than the roadmap survey question: exact-path contents reads still miss `scripts/basic/fixdep.c`, but that miss does not reopen the Phase 2 dual-implementation scaffold gap.
- The honest lane result is therefore a survey-note truthfulness refresh and parking pass, not a new fixdep behavior, fixture, or route implementation.

## Next bounded same-family step

1. Keep `P2-L01` parked unless a fresh current-`master` reread finds new repo-versus-roadmap drift inside the fixdep helper, checker, fixture, or route packet.
2. If the fixdep family reopens from reminder drift only, keep the follow-through on the directly coupled non-survey lane that owns it, such as a future checker-anchor truthfulness repair rather than new survey-only churn.
3. Do not widen from this survey into genksyms, kconfig, parser behavior, or shared Phase 2 reminder maintenance.
"""

SAMPLE_TESTS_README = """# zigux/tests

current `master` also directly materializes `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `make -C zigux phase2-fixdep`, and `zigux/tests/fixtures/fixdep/cases.json`, so keep that returned fixdep governance, parity, helper, wrapper, and fixture packet explicit here instead of leaving it outside the tests-root reminder
"""

SAMPLE_CASES = json.dumps(
    [
        {
            "name": name,
            "depfile": f"{name}.d",
            "target": f"{name}.o",
            "cmdline": "clang -c sample.c -o sample.o",
            "expected": f"{name}_expected.txt",
            "expected_exit_code": 0 if name not in EXPECTED_STDOUT_FULL_CASES else 1,
            **({"stdout_mode": "dev_full"} if name in EXPECTED_STDOUT_FULL_CASES else {}),
        }
        for name in EXPECTED_CASE_NAMES
    ],
    indent=2,
) + "\n"

SAMPLE_MAKEFILE = "\n".join(MAKEFILE_LINES) + "\n"
SAMPLE_WORKFLOW = "\n".join(WORKFLOW_LINES) + "\n"


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 fixdep survey packet missing file: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"phase2 fixdep survey packet unreadable file {path}: {exc}") from exc


def require_paths(root: Path) -> None:
    for rel in REQUIRED_PATHS:
        path = root / rel
        if not path.is_file():
            raise SystemExit(f"phase2 fixdep survey packet missing required path: {path}")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"phase2 fixdep survey packet missing {label} marker: {marker}")


def require_exact_lines(text: str, lines: tuple[str, ...], label: str) -> None:
    stripped = [line.strip() for line in text.splitlines()]
    for line in lines:
        count = sum(1 for candidate in stripped if candidate == line)
        if count == 0:
            raise SystemExit(f"phase2 fixdep survey packet missing {label} line: {line}")
        if count != 1:
            raise SystemExit(f"phase2 fixdep survey packet duplicate {label} line count={count}: {line}")


def check_cases_json(root: Path) -> None:
    path = root / CASES
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"phase2 fixdep survey packet invalid cases JSON {path}: {exc}") from exc

    if not isinstance(payload, list):
        raise SystemExit("phase2 fixdep survey packet expected fixdep cases JSON array")
    if len(payload) != len(EXPECTED_CASE_NAMES):
        raise SystemExit(
            "phase2 fixdep survey packet wrong fixdep case count: "
            f"expected {len(EXPECTED_CASE_NAMES)} got {len(payload)}"
        )

    names = [entry.get("name") for entry in payload if isinstance(entry, dict)]
    if tuple(names) != EXPECTED_CASE_NAMES:
        raise SystemExit(
            "phase2 fixdep survey packet wrong fixdep case order: "
            f"expected {EXPECTED_CASE_NAMES} got {tuple(names)}"
        )

    stdout_full = tuple(
        entry["name"]
        for entry in payload
        if isinstance(entry, dict) and entry.get("stdout_mode") == "dev_full"
    )
    if stdout_full != EXPECTED_STDOUT_FULL_CASES:
        raise SystemExit(
            "phase2 fixdep survey packet wrong stdout-full case set: "
            f"expected {EXPECTED_STDOUT_FULL_CASES} got {stdout_full}"
        )


def check_root(root: Path) -> None:
    require_paths(root)
    require_markers(read_text(root, SURVEY), SURVEY_MARKERS, "survey")
    require_markers(read_text(root, TESTS_README), TESTS_README_MARKERS, "tests-readme")
    require_markers(read_text(root, CLOSURE), ("`scripts/zigux/check-phase2-fixdep-gate.py --self-test`", "`make -C zigux phase2-fixdep`"), "closure")
    require_exact_lines(read_text(root, MAKEFILE), MAKEFILE_LINES, "Makefile")
    require_exact_lines(read_text(root, WORKFLOW), WORKFLOW_LINES, "workflow")
    check_cases_json(root)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_sample_root(root: Path) -> None:
    write_text(root / SURVEY, SAMPLE_SURVEY)
    write_text(root / TESTS_README, SAMPLE_TESTS_README)
    write_text(root / CLOSURE, "`scripts/zigux/check-phase2-fixdep-gate.py --self-test`\n`make -C zigux phase2-fixdep`\n")
    write_text(root / HELPER, "// helper placeholder\n")
    write_text(root / GATE, "# gate placeholder\n")
    write_text(root / DIFF, "# diff placeholder\n")
    write_text(root / VALIDATOR, "# validator placeholder\n")
    write_text(root / ARTIFACT_DIFF_NOTE, "# artifact diff note\n")
    write_text(root / CASES, SAMPLE_CASES)
    write_text(root / MAKEFILE, SAMPLE_MAKEFILE)
    write_text(root / WORKFLOW, SAMPLE_WORKFLOW)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_phase2_fixdep_survey_packet_") as tmp:
        sample_root = Path(tmp)
        write_sample_root(sample_root)
        check_root(sample_root)
        case_count += 1

        broken = sample_root / SURVEY
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "survey marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing survey marker failure")
        write_sample_root(sample_root)

        broken = sample_root / TESTS_README
        broken.write_text("# broken\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "tests-readme marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing tests-readme marker failure")
        write_sample_root(sample_root)

        broken = sample_root / MAKEFILE
        broken.write_text("phase2-fixdep:\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "Makefile line" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing Makefile line failure")
        write_sample_root(sample_root)

        broken = sample_root / WORKFLOW
        broken.write_text("run: zig test scripts/zigux/fixdep.zig\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "workflow line" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing workflow line failure")
        write_sample_root(sample_root)

        broken = sample_root / CASES
        payload = json.loads(broken.read_text(encoding="utf-8"))
        payload.pop()
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "wrong fixdep case count" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected wrong case count failure")
        write_sample_root(sample_root)

        broken = sample_root / CASES
        payload = json.loads(broken.read_text(encoding="utf-8"))
        payload[0]["name"] = "wrong"
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "wrong fixdep case order" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected wrong case order failure")
        write_sample_root(sample_root)

        broken = sample_root / CASES
        payload = json.loads(broken.read_text(encoding="utf-8"))
        for entry in payload:
            if entry["name"] == "sample_output_write":
                entry.pop("stdout_mode", None)
        broken.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "wrong stdout-full case set" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected wrong stdout-full set failure")
        write_sample_root(sample_root)

        missing_required = sample_root / HELPER
        missing_required.unlink()
        try:
            check_root(sample_root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")

    print("PHASE2_FIXDEP_SURVEY_PACKET_SELF_TEST=pass")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the live Phase 2 fixdep survey packet.")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        write_sample_root(args.write_sample_root)
        return 0

    check_root(args.root.resolve())
    print("PHASE2_FIXDEP_SURVEY_PACKET=pass")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_ROOT={args.root.resolve()}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_CASE_COUNT={len(EXPECTED_CASE_NAMES)}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_STDOUT_FULL_CASE_COUNT={len(EXPECTED_STDOUT_FULL_CASES)}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_WORKFLOW_LINE_COUNT={len(WORKFLOW_LINES)}")
    print(f"PHASE2_FIXDEP_SURVEY_PACKET_MISSING_C_ANCHOR={EXPECTED_MISSING_DEPFILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
