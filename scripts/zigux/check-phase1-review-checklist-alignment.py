#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

HOST_TOOLS_PROMPT = "if the change touches the closed Phase 1 host-tools packet"
HOST_TOOLS_MARKERS = (
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "`Documentation/zigux/phase1-closure.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`scripts/zigux/check-phase1-direct-owner-markers.py`",
    "`scripts/zigux/check-phase1-bench.py`",
    "`zigux/tests/build.zig`",
    "`zigux/tests/phase1_host_tools_smoke.zig`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/validate-phase1.py`",
    "`scripts/zigux/check-phase1-parity.py`",
    "`zigux/tests/phase1_helpers.zig`",
    "`zigux/tests/phase1_bench.zig`",
    "`zigux/tests/fixtures/phase1_bench_expectations.json`",
    "`zigux/tests/fixtures/phase1_helpers_c_harness.c`",
    "`zig build test --build-file zigux/tests/build.zig`",
    "`zig build bench --build-file zigux/tests/build.zig`",
    "`make -C zigux phase1-validate`",
    "`make -C zigux phase1-test`",
    "`make -C zigux phase1-bench`",
    "`make -C zigux phase1`",
    "`zigux/Makefile`",
    "historical packet members rather than direct current evidence unless a fresh reread materializes them again",
    "the Phase 1 reminder stays bounded to the host-side helper packet instead of reopening broader closure-stack churn",
)

REMINDER_PACKET_PROMPT = "if the change touches that same Phase 1 reminder packet"
REMINDER_PACKET_MARKERS = (
    "`python3 scripts/zigux/validate-phase1-closure.py`",
    "`python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`",
    "`python3 scripts/zigux/check-phase1-bench.py --self-test`",
    "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "`Documentation/zigux/phase1-closure.md`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`scripts/zigux/check-phase1-direct-owner-markers.py`",
    "`scripts/zigux/check-phase1-bench.py`",
    "`zigux/tests/build.zig`",
    "`zigux/tests/phase1_host_tools_smoke.zig`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "the older installer-companion self-test-versus-live route wording stays historical until `scripts/zigux/check-phase1-installer-companion-checks.py` is directly readable again",
    "the broader docs-root, checklist, and tests-root bench wording stays aligned with the shipped bench checker instead of treating it as missing current evidence",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    checklist = _read(root / REVIEW_CHECKLIST_PATH)
    failures: list[str] = []

    host_tools_line = _line_containing(checklist, HOST_TOOLS_PROMPT)
    if host_tools_line is None:
        failures.append(f"host_tools_prompt:missing:{HOST_TOOLS_PROMPT}")
    else:
        for marker in HOST_TOOLS_MARKERS:
            if marker not in host_tools_line:
                failures.append(f"host_tools_marker:missing:{marker}")

    reminder_line = _line_containing(checklist, REMINDER_PACKET_PROMPT)
    if reminder_line is None:
        failures.append(f"reminder_prompt:missing:{REMINDER_PACKET_PROMPT}")
    else:
        for marker in REMINDER_PACKET_MARKERS:
            if marker not in reminder_line:
                failures.append(f"reminder_marker:missing:{marker}")

    return failures


def _sample_review_checklist() -> str:
    host_tools = (
        "  * if the change touches the closed Phase 1 host-tools packet, do "
        "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, "
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, "
        "`Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, "
        "`zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, "
        "`scripts/zigux/validate-phase1-closure.py`, "
        "`scripts/zigux/check-phase1-string-review-packet.py`, "
        "`scripts/zigux/check-phase1-direct-owner-markers.py`, "
        "`scripts/zigux/check-phase1-bench.py` still agree on the same bounded "
        "current-`master` reminder packet, the thirteen-helper owner map, the parked "
        "shared-replay-versus-direct-anchor split, the restored closure note and closure "
        "validator, the live string-review and direct-owner guards, `zigux/tests/build.zig` "
        "and `zigux/tests/phase1_host_tools_smoke.zig` stay explicit as the shipped "
        "shared-smoke reminder anchors while `scripts/zigux/check-phase1-bench.py` stays "
        "explicit as the shipped bench-side checker anchor for the remaining shared reminder "
        "wording, and the repo-reality warning that older installer-backed, validator-first, "
        "make-route, bench-route, and replay paths such as `scripts/zigux/install-zig.py`, "
        "`scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, "
        "`zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, "
        "`zigux/tests/fixtures/phase1_bench_expectations.json`, "
        "`zigux/tests/fixtures/phase1_helpers_c_harness.c`, "
        "`zig build test --build-file zigux/tests/build.zig`, "
        "`zig build bench --build-file zigux/tests/build.zig`, "
        "`make -C zigux phase1-validate`, `make -C zigux phase1-test`, "
        "`make -C zigux phase1-bench`, and `make -C zigux phase1` stay framed as "
        "historical packet members rather than direct current evidence unless a fresh reread "
        "materializes them again, while current `master` does materialize `zigux/Makefile` "
        "and that returned file should stay framed as live repo evidence whose body still "
        "exposes only the shipped Phase 2 toolchain and kbuild wrappers together with the "
        "bounded `phase3-validate` and `phase3` routes rather than as proof that the older "
        "Phase 1 wrapper names returned, while the Phase 1 reminder stays bounded to the "
        "host-side helper packet instead of reopening broader closure-stack churn?\n"
    )
    reminder = (
        "  * if the change touches that same Phase 1 reminder packet, does the checklist "
        "still say clearly that `python3 scripts/zigux/validate-phase1-closure.py`, "
        "`python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, "
        "`python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and "
        "`python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded live "
        "reminder checks and `zig build phase1-host-tools-smoke --build-file "
        "zigux/tests/build.zig` replays the bounded live shared smoke route while "
        "`Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, "
        "`scripts/zigux/check-phase1-string-review-packet.py`, "
        "`scripts/zigux/check-phase1-direct-owner-markers.py`, "
        "`scripts/zigux/check-phase1-bench.py`, `zigux/tests/build.zig`, "
        "`zigux/tests/phase1_host_tools_smoke.zig`, and `.github/workflows/zigux-bootstrap.yml` "
        "keep the shipped current-`master` Phase 1 reminder packet explicit, that the older "
        "installer-companion self-test-versus-live route wording stays historical until "
        "`scripts/zigux/check-phase1-installer-companion-checks.py` is directly readable again, "
        "and that the broader docs-root, checklist, and tests-root bench wording stays aligned "
        "with the shipped bench checker instead of treating it as missing current evidence?\n"
    )
    return "# Zigux Review Checklist\n\n" + host_tools + reminder


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_review_checklist_") as tmpdir:
        root = Path(tmpdir)
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline review checklist fixture should pass: {failures}")
        case_count += 1

        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist().replace(HOST_TOOLS_PROMPT, "", 1))
        failures = collect_failures(root)
        expected = [f"host_tools_prompt:missing:{HOST_TOOLS_PROMPT}"]
        if failures != expected:
            raise AssertionError(f"unexpected host-tools prompt failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("`zigux/tests/fixtures/phase1_bench_expectations.json`", "", 1),
        )
        failures = collect_failures(root)
        expected = ["host_tools_marker:missing:`zigux/tests/fixtures/phase1_bench_expectations.json`"]
        if failures != expected:
            raise AssertionError(f"unexpected host-tools marker failure: {failures}")
        case_count += 1

        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist().replace(REMINDER_PACKET_PROMPT, "", 1))
        failures = collect_failures(root)
        expected = [f"reminder_prompt:missing:{REMINDER_PACKET_PROMPT}"]
        if failures != expected:
            raise AssertionError(f"unexpected reminder prompt failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("`.github/workflows/zigux-bootstrap.yml`", "", 1),
        )
        failures = collect_failures(root)
        expected = ["reminder_marker:missing:`.github/workflows/zigux-bootstrap.yml`"]
        if failures != expected:
            raise AssertionError(f"unexpected workflow marker failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "the broader docs-root, checklist, and tests-root bench wording stays aligned "
                "with the shipped bench checker instead of treating it as missing current evidence",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "reminder_marker:missing:the broader docs-root, checklist, and tests-root bench wording stays aligned with the shipped bench checker instead of treating it as missing current evidence"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected reminder detail failure: {failures}")
        case_count += 1

    print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 1 review-checklist reminder stays aligned with the current closure packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 1 review-checklist alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
