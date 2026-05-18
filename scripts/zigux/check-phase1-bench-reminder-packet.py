#!/usr/bin/env python3
"""Guard the shipped Phase 1 bench reminder packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    BENCH_CHECKER_REL,
)

REQUIRED_EXACT_LINES = {
    DOCS_ROOT_REL: {
        "bench_checker_listed": "- `scripts/zigux/check-phase1-bench.py`",
        "direct_checks": "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
        "self_test_split": "  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    },
    REVIEW_CHECKLIST_REL: {
        "packet_alignment": "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` still agree on the same bounded current-`master` reminder packet: the thirteen-helper owner map, the parked shared-replay-versus-direct-anchor split, the restored closure note and closure validator, the live string-review and direct-owner guards, `zigux/tests/build.zig` and `zigux/tests/phase1_host_tools_smoke.zig` stay explicit as the shipped shared-smoke reminder anchors while `scripts/zigux/check-phase1-bench.py` stays explicit as the shipped bench-side checker anchor for the remaining shared reminder wording, and the repo-reality warning that older installer-backed, validator-first, make-route, bench-route, and replay paths such as `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` stay framed as historical packet members rather than direct current evidence unless a fresh reread materializes them again, while current `master` does materialize `zigux/Makefile` and that returned file should stay framed as live repo evidence whose body still exposes only the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes rather than as proof that the older Phase 1 wrapper names returned, while the Phase 1 reminder stays bounded to the host-side helper packet instead of reopening broader closure-stack churn?",
        "self_test_alignment": "  * if the change touches that same Phase 1 reminder packet, does the checklist still say clearly that `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded live reminder checks and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the bounded live shared smoke route while `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `.github/workflows/zigux-bootstrap.yml` keep the shipped current-`master` Phase 1 reminder packet explicit, that the older installer-companion self-test-versus-live route wording stays historical until `scripts/zigux/check-phase1-installer-companion-checks.py` is directly readable again, and that the broader docs-root, checklist, and tests-root bench wording stays aligned with the shipped bench checker instead of treating it as missing current evidence?",
    },
    SCRIPTS_README_REL: {
        "self_tests": "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "packet_explicit": "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, and closure-validator packet explicit from the scripts root",
        "bench_checker_present": "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    },
    TESTS_README_REL: {
        "closure_note_present": "    `Documentation/zigux/phase1-closure.md`",
        "lane_note_present": "    `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
        "review_checklist_present": "    `Documentation/zigux/review-checklist.md`",
        "scripts_readme_present": "    `scripts/zigux/README.md`",
        "closure_validator_present": "    `scripts/zigux/validate-phase1-closure.py`",
        "string_review_present": "    `scripts/zigux/check-phase1-string-review-packet.py`",
        "direct_owner_present": "    `scripts/zigux/check-phase1-direct-owner-markers.py`",
        "bench_checker_present": "    `scripts/zigux/check-phase1-bench.py`",
        "helper_manifest_present": "    `zigux/tests/fixtures/phase1_helper_manifest.json`",
        "shared_smoke_route": "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "historical_warning": "  * repo-reality warning for the broader historical Phase 1 validator-first, bench, and replay stack: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "makefile_readback": "  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 8, Phase 10, and Phase 12 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
        "followthrough_alignment": "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    },
    WORKFLOW_REL: {
        "bench_self_test_step": "      - name: Self-test current Phase 1 bench checker",
        "bench_self_test_run": "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "shared_reminder_self_test_step": "      - name: Self-test current Phase 1 shared reminder checker",
        "shared_reminder_run_step": "      - name: Check current Phase 1 shared reminder packet",
    },
    BENCH_CHECKER_REL: {
        "self_test_function": "def run_self_test() -> None:",
        "self_test_pass": '    print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        "self_test_case_count": '    print(f"PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT={case_count}")',
    },
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == expected)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        text = load_text(root, relative_path)
        for label, line in labels.items():
            failures.extend(require_exact_line(text, f"{relative_path.as_posix()}:{label}", line))

    return failures


def expected_line_failure(relative_path: Path, label: str, actual: int) -> str:
    return f"{relative_path.as_posix()}:{label}:expected=1:actual={actual}"


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_text(relative_path: Path) -> str:
    labels = REQUIRED_EXACT_LINES.get(relative_path, {})
    if not labels:
        return "# sample\n"
    return "# sample\n\n" + "\n".join(labels.values()) + "\n"


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_file(root, relative_path, sample_text(relative_path))


def run_self_test() -> int:
    cases: list[tuple[str, Path | None, str | None, str, list[str]]] = [
        ("success", None, None, "none", []),
        ("missing_workflow", WORKFLOW_REL, None, "missing_file", [f"missing_file:{WORKFLOW_REL.as_posix()}"]),
        ("missing_bench_checker", BENCH_CHECKER_REL, None, "missing_file", [f"missing_file:{BENCH_CHECKER_REL.as_posix()}"]),
    ]
    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        for label, line in labels.items():
            cases.append(
                (
                    f"missing_{relative_path.name}_{label}",
                    relative_path,
                    line,
                    "remove",
                    [expected_line_failure(relative_path, label, 0)],
                )
            )
            cases.append(
                (
                    f"duplicate_{relative_path.name}_{label}",
                    relative_path,
                    line,
                    "duplicate",
                    [expected_line_failure(relative_path, label, 2)],
                )
            )

    for name, relative_path, needle, operation, expected_failures in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-bench-reminder-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if relative_path and needle:
                target = root / relative_path
                text = target.read_text(encoding="utf-8")
                if operation == "remove":
                    text = text.replace(needle + "\n", "", 1)
                elif operation == "duplicate":
                    text = text.replace(needle, needle + "\n" + needle, 1)
                target.write_text(text, encoding="utf-8")
            elif relative_path and operation == "missing_file":
                (root / relative_path).unlink()

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for item in failures:
                        print(item)
                    return 1
                continue

            if failures != expected_failures:
                print(f"self-test:{name}:unexpected_failures")
                print(f"expected={expected_failures!r}")
                print(f"actual={failures!r}")
                return 1

    print("phase1-bench-reminder-packet:self-test=pass")
    print(f"phase1-bench-reminder-packet:self-test-case-count={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-bench-reminder-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
