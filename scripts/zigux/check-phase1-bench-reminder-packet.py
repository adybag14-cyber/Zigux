#!/usr/bin/env python3
"""Guard the shipped Phase 1 bench reminder packet against reminder-surface drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    LANE_NOTE_REL,
    BENCH_CHECKER_REL,
)

REQUIRED_EXACT_LINES = {
    DOCS_ROOT_REL: {
        "phase1_bench_checker_listed": "- `scripts/zigux/check-phase1-bench.py`",
        "phase1_historical_warning": "  * repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1`, so treat those installer-backed, closure-side, validator-first, bench-route, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-master evidence.",
        "phase1_direct_checks": "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, string-review, direct-owner, and bench guards: `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, closure-side, bench-route, and replay surfaces.",
        "phase1_self_test_split": "  * `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    },
    REVIEW_CHECKLIST_REL: {
        "phase1_packet_alignment": "  * if the change touches the closed Phase 1 host-tools packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, `scripts/zigux/check-phase1-string-review-packet.py`, and `scripts/zigux/check-phase1-direct-owner-markers.py` still agree on the same bounded current-`master` reminder packet: the thirteen-helper owner map, the parked shared-replay-versus-direct-anchor split, the live string-review and direct-owner guards, and the repo-reality warning that older installer-backed, closure-side, validator-first, make-route, bench, and replay paths such as `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, `zigux/tests/fixtures/phase1_helpers_c_harness.c`, `zigux/Makefile`, `zig build test --build-file zigux/tests/build.zig`, `zig build bench --build-file zigux/tests/build.zig`, `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, and `make -C zigux phase1` stay framed as historical packet members rather than direct current evidence unless a fresh reread materializes them again, while `scripts/zigux/check-phase1-bench.py` stays explicit as the shipped bench-side checker anchor for the remaining shared reminder wording, without widening Phase 1 beyond the bounded host-side helper packet?",
        "phase1_self_test_alignment": "  * if the change touches that same Phase 1 reminder packet, does the checklist still say clearly that `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded live reminder checks while `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` guard the shipped current-`master` Phase 1 reminder packet, that the older installer-companion self-test-versus-live route wording stays historical until `scripts/zigux/check-phase1-installer-companion-checks.py` is directly readable again, and that the broader docs-root, checklist, and tests-root bench wording stays aligned with the shipped bench checker instead of treating it as missing current evidence?",
    },
    TESTS_README_REL: {
        "phase1_direct_packet": "  * current direct-readback Phase 1 reminder packet: `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py`",
        "phase1_historical_warning": "  * repo-reality warning for the broader Phase 1 installer-backed closure-and-replay packet: repeated authenticated contents reads on current `master` now return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`",
        "phase1_bench_checker_present": "  * current `master` does ship `scripts/zigux/check-phase1-bench.py`, so keep the remaining shared reminder follow-through on the broader docs-root, checklist, and tests-root bench wording instead of treating the checker itself as a missing tests-root route",
        "phase1_followthrough_alignment": "  * keep current Phase 1 follow-through tied to the live owner-map plus string-review and bench reminder packet instead of reconstructing the broader installer-backed closure-and-replay packet from those older missing installer, closure-side, and replay files and routes alone",
    },
    SCRIPTS_README_REL: {
        "phase1_bench_checker_present": "- current `master` does ship `scripts/zigux/check-phase1-bench.py`, and `.github/workflows/zigux-bootstrap.yml` self-tests it, so keep the remaining shared reminder follow-through focused on the broader docs-root, checklist, and tests-root bench wording instead of treating the bench checker itself as a repo-reality gap here",
    },
    LANE_NOTE_REL: {
        "shared_reminder_split_note": "- broader shared reminder surfaces now split cleanly: `scripts/zigux/README.md` already records that `scripts/zigux/check-phase1-bench.py` ships on current `master` and that `.github/workflows/zigux-bootstrap.yml` now self-tests it, while `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` still keep the checker inside their historical-gap wording, so the remaining bench-wording follow-through is limited to those three surfaces",
        "shared_reminder_gap_note": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_GAPS=the shared reminder packet now splits cleanly: scripts/zigux/README.md already records that scripts/zigux/check-phase1-bench.py ships on current master and that bootstrap self-tests it, while Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md still keep the checker inside their historical-gap wording, so the remaining bench-wording follow-through is limited to those three surfaces`",
        "shared_reminder_next_step": "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_NEXT_STEP=finish the remaining three-surface bench-wording sync across Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, and zigux/tests/README.md while keeping scripts/zigux/README.md on the already-shipped bench-checker wording before reopening helper-local follow-through, unless one of the helper-specific next-safe-step markers below exposes a smaller same-family drift first`",
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
        if relative_path == BENCH_CHECKER_REL:
            write_file(root, relative_path, "#!/usr/bin/env python3\nprint('bench checker placeholder')\n")
        else:
            write_file(root, relative_path, sample_text(relative_path))


def run_self_test() -> int:
    cases: list[tuple[str, Path | None, str | None, str]] = [("success", None, None, "none")]
    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        for _, line in labels.items():
            cases.append((f"missing_{relative_path.name}", relative_path, line, "remove"))
            cases.append((f"duplicate_{relative_path.name}", relative_path, line, "duplicate"))

    for name, relative_path, needle, operation in cases:
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

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for item in failures:
                        print(item)
                    return 1
                continue

            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
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
