#!/usr/bin/env python3
"""Guard the historical Phase 1 parity-gap packet and Phase 4 artifact-diff boundary."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_GAP_PACKET = (
    "scripts/zigux/validate-phase1.py,"
    "scripts/zigux/check-phase1-parity.py,"
    "zigux/tests/phase1_helpers.zig,"
    "zigux/tests/phase1_bench.zig,"
    "zigux/tests/fixtures/phase1_bench_expectations.json,"
    "zigux/tests/fixtures/phase1_helpers_c_harness.c"
)

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/validate-phase1-closure.py",
    "scripts/zigux/artifact_diff.py",
    "zigux/tests/README.md",
    ".github/workflows/zigux-bootstrap.yml",
)

EXACT_MARKERS = {
    "Documentation/zigux/README.md": (
        "keep the live owner map, the restored closure note and closure validator, the parked shared-replay-versus-direct-anchor split, the shipped bench checker, and the current Phase 1 reminder packet explicit from the docs root without rebuilding the broader host-tools closure stack from older missing validator and replay surfaces.",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.",
        f"`PHASE1_CURRENT_GAP_PACKET={PHASE1_GAP_PACKET}`",
        "This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them.",
    ),
    "Documentation/zigux/review-checklist.md": (
        "keep `zigux/Makefile` explicit as current repo evidence for the returned Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    "scripts/zigux/README.md": (
        "repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, older validator-first, parity, and replay routes as historical packet members that need fresh re-materialization before they are reused here as direct current-`master` reminder evidence",
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        f"\"gap_packet\": \"`PHASE1_CURRENT_GAP_PACKET={PHASE1_GAP_PACKET}`\",",
    ),
    "scripts/zigux/artifact_diff.py": (
        'MODE_CHOICES = ("text", "json", "bytes")',
        'print("ARTIFACT_DIFF_SELF_TEST=pass")',
    ),
    "zigux/tests/README.md": (
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    ),
}

WORKFLOW_STRIPPED_LINES = (
    "run: python3 scripts/zigux/artifact_diff.py --self-test",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
)

FORBIDDEN_FRAGMENTS = (
    "python3 scripts/zigux/check-phase1-parity.py --self-test",
    "python3 scripts/zigux/check-phase1-parity.py",
    "python3 scripts/zigux/validate-phase1.py --self-test",
    "python3 scripts/zigux/validate-phase1.py",
    "run: python3 scripts/zigux/check-phase1-parity.py",
    "run: python3 scripts/zigux/validate-phase1.py",
    "`scripts/zigux/artifact_diff.py` is the Phase 1 parity gate",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_fragment(text: str, label: str, fragment: str) -> list[str]:
    count = text.count(fragment)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_stripped_line(text: str, label: str, line: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == line.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_fragment(text: str, label: str, fragment: str) -> list[str]:
    count = text.count(fragment)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, relative_path)
        for index, marker in enumerate(markers):
            failures.extend(
                require_exact_fragment(text, f"{relative_path}:marker_{index}", marker)
            )

    workflow_text = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    for index, line in enumerate(WORKFLOW_STRIPPED_LINES):
        failures.extend(
            require_stripped_line(
                workflow_text, f".github/workflows/zigux-bootstrap.yml:line_{index}", line
            )
        )

    for relative_path in REQUIRED_FILES:
        text = read_text(root, relative_path)
        for index, fragment in enumerate(FORBIDDEN_FRAGMENTS):
            failures.extend(
                require_absent_fragment(
                    text,
                    f"{relative_path}:forbidden_{index}",
                    fragment,
                )
            )

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = list(EXACT_MARKERS.get(relative_path, ()))
        if relative_path == ".github/workflows/zigux-bootstrap.yml":
            markers.extend(WORKFLOW_STRIPPED_LINES)
        write_text(root, relative_path, "\n".join(markers) + "\n")


def remove_fragment(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(fragment + "\n", "", 1).replace(fragment, "", 1), encoding="utf-8")


def duplicate_fragment(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(fragment, fragment + "\n" + fragment, 1), encoding="utf-8")


def append_fragment(root: Path, relative_path: str, fragment: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + fragment + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, str | None, str | None, str]] = [("success", None, None, "none")]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", relative_path, None, "missing_file"))
    for relative_path, markers in EXACT_MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}:{abs(hash(marker))}", relative_path, marker, "remove"))
            cases.append((f"duplicate:{relative_path}:{abs(hash(marker))}", relative_path, marker, "duplicate"))
    for line in WORKFLOW_STRIPPED_LINES:
        cases.append(("remove_workflow_line:" + str(abs(hash(line))), ".github/workflows/zigux-bootstrap.yml", line, "remove"))
        cases.append(("duplicate_workflow_line:" + str(abs(hash(line))), ".github/workflows/zigux-bootstrap.yml", line, "duplicate"))
    for fragment in FORBIDDEN_FRAGMENTS:
        cases.append(("forbidden:" + str(abs(hash(fragment))), "Documentation/zigux/README.md", fragment, "forbidden"))

    for name, relative_path, payload, operation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-parity-gap-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if relative_path is not None:
                if operation == "missing_file":
                    (root / relative_path).unlink()
                elif operation == "remove":
                    assert payload is not None
                    remove_fragment(root, relative_path, payload)
                elif operation == "duplicate":
                    assert payload is not None
                    duplicate_fragment(root, relative_path, payload)
                elif operation == "forbidden":
                    assert payload is not None
                    append_fragment(root, relative_path, payload)

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_PARITY_GAP_PACKET_SELF_TEST=pass")
    print(f"PHASE1_PARITY_GAP_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_PARITY_GAP_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_PARITY_GAP_PACKET=pass")
    print(f"PHASE1_PARITY_GAP_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_PARITY_GAP_PACKET_GAP_ENTRY_COUNT={PHASE1_GAP_PACKET.count(',') + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
