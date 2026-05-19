#!/usr/bin/env python3
"""Guard the current Phase 1 reminder-companion checker packet against drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    DOCS_ROOT_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    VALIDATOR_REL,
    STRING_REVIEW_REL,
    DIRECT_OWNER_REL,
)

REQUIRED_EXACT_LINES = {
    PHASE1_CLOSURE_REL: {
        "string_review_listed": "- `scripts/zigux/check-phase1-string-review-packet.py`",
        "direct_owner_listed": "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    },
    DOCS_ROOT_REL: {
        "string_review_listed": "- `scripts/zigux/check-phase1-string-review-packet.py`",
        "direct_owner_listed": "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
        "direct_checks": "  * the current docs-root Phase 1 reminder packet should stay parked on the live owner-map, restored closure-side, string-review, direct-owner, and bench guards: `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` keep the current-master-safe closure packet explicit, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` are the shipped direct checks, while `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `scripts/zigux/README.md` keep the same historical-warning wording aligned around the broader missing installer, validator-first, bench-route, and replay surfaces.",
        "self_tests": "  * `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    },
    REVIEW_CHECKLIST_REL: {
        "packet_alignment": "  * if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    },
    SCRIPTS_README_REL: {
        "self_tests": "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "live_guards": "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, and closure-validator packet explicit from the scripts root",
    },
    VALIDATOR_REL: {
        "reminder_packet_string": '        "scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,"',
    },
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    expected = line.strip()
    count = sum(1 for current_line in text.splitlines() if current_line.strip() == expected)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        text = load_text(root, relative_path)
        for label, line in labels.items():
            failures.extend(
                require_exact_line(text, f"{relative_path.as_posix()}:{label}", line)
            )
    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        labels = REQUIRED_EXACT_LINES.get(relative_path)
        if labels:
            write_file(root, relative_path, "# sample\n\n" + "\n".join(labels.values()) + "\n")
        else:
            write_file(root, relative_path, f"# sample for {relative_path.as_posix()}\n")


def mutate_line(root: Path, relative_path: Path, line: str, operation: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    if operation == "remove":
        text = text.replace(line + "\n", "", 1)
    elif operation == "duplicate":
        text = text.replace(line + "\n", line + "\n" + line + "\n", 1)
    else:
        raise ValueError(f"unsupported operation: {operation}")
    target.write_text(text, encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, Path | None, str | None, str]] = [("baseline", None, None, "none")]
    for relative_path, labels in REQUIRED_EXACT_LINES.items():
        for label, line in labels.items():
            cases.append((f"missing_{relative_path.name}_{label}", relative_path, line, "remove"))
            cases.append((f"duplicate_{relative_path.name}_{label}", relative_path, line, "duplicate"))
    cases.extend(
        [
            ("missing_string_review_file", STRING_REVIEW_REL, None, "missing_file"),
            ("missing_direct_owner_file", DIRECT_OWNER_REL, None, "missing_file"),
        ]
    )

    for name, relative_path, line, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-reminder-companion-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if relative_path is not None:
                target = root / relative_path
                if operation == "missing_file":
                    target.unlink()
                else:
                    assert line is not None
                    mutate_line(root, relative_path, line, operation)

            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"phase1-reminder-companion-self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"phase1-reminder-companion-self-test:{name}:expected_failure")
                return 1

    print("PHASE1_REMINDER_COMPANION_PACKET_SELF_TEST=pass")
    print(f"PHASE1_REMINDER_COMPANION_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_REMINDER_COMPANION_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
