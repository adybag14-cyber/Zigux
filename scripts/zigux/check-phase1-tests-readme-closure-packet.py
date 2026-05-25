#!/usr/bin/env python3
"""Guard the Lane 15 Phase 1 tests-root closure reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

TESTS_README_REL = Path("zigux/tests/README.md")

REQUIRED_FILES = (
    Path("Documentation/zigux/phase1-closure.md"),
    Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md"),
    Path("Documentation/zigux/README.md"),
    Path("Documentation/zigux/review-checklist.md"),
    Path("scripts/zigux/README.md"),
    Path("scripts/zigux/check-phase1-string-review-packet.py"),
    Path("scripts/zigux/check-phase1-direct-owner-markers.py"),
    Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"),
    Path("scripts/zigux/check-phase1-bench.py"),
    Path("scripts/zigux/check-phase1-shared-reminder-packet.py"),
    Path("scripts/zigux/validate-phase1-closure.py"),
    Path("zigux/tests/build.zig"),
    Path("zigux/tests/phase1_host_tools_smoke.zig"),
    Path("zigux/tests/fixtures/phase1_helper_manifest.json"),
    Path(".github/workflows/zigux-bootstrap.yml"),
    Path("zigux/Makefile"),
    TESTS_README_REL,
)

REQUIRED_MARKERS = (
    "  * current direct-readback Phase 1 reminder packet:",
    "- `Documentation/zigux/phase1-closure.md`",
    "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "- `Documentation/zigux/README.md`",
    "- `Documentation/zigux/review-checklist.md`",
    "- `scripts/zigux/README.md`",
    "- `scripts/zigux/check-phase1-string-review-packet.py`",
    "- `scripts/zigux/check-phase1-direct-owner-markers.py`",
    "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`",
    "- `scripts/zigux/check-phase1-bench.py`",
    "- `scripts/zigux/check-phase1-shared-reminder-packet.py`",
    "- `scripts/zigux/validate-phase1-closure.py`",
    "- `zigux/tests/build.zig`",
    "- `zigux/tests/phase1_host_tools_smoke.zig`",
    "- `.github/workflows/zigux-bootstrap.yml`",
    "- `zigux/tests/fixtures/phase1_helper_manifest.json`",
    "- `zigux/tests/README.md`",
    "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    "Tests-root reviewer prompt:",
    "- Does the bounded Phase 1 reminder keep the restored closure note, the direct-anchor manifest gate, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
)


def repo_root(override: str | None) -> Path:
    return Path(override).resolve() if override else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    text = read_text(root, TESTS_README_REL)
    for marker in REQUIRED_MARKERS:
        count = text.count(marker)
        if count != 1:
            failures.append(
                f"{TESTS_README_REL.as_posix()}:{marker}:expected=1:actual={count}"
            )
    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def sample_tests_readme() -> str:
    return "# zigux/tests\n\n## Phase 1 host-tools review packet\n\n" + "\n".join(REQUIRED_MARKERS) + "\n"


def write_sample_root(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        content = "sample\n"
        if relative_path == TESTS_README_REL:
            content = sample_tests_readme()
        write_text(root, relative_path, content)


def mutate_remove_marker(root: Path, marker: str) -> None:
    target = root / TESTS_README_REL
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, marker: str) -> None:
    target = root / TESTS_README_REL
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases = [
        ("baseline", None, True),
        ("missing_direct_anchor_gate", lambda root: mutate_remove_marker(root, "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`"), False),
        ("duplicate_direct_anchor_gate", lambda root: mutate_duplicate_marker(root, "- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`"), False),
        ("missing_reviewer_prompt", lambda root: mutate_remove_marker(root, "- Does the bounded Phase 1 reminder keep the restored closure note, the direct-anchor manifest gate, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?"), False),
        ("missing_required_file", lambda root: (root / Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")).unlink(), False),
    ]

    for name, mutate, expect_ok in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-tests-readme-{name}-") as tmpdir:
            root = Path(tmpdir)
            write_sample_root(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            ok = not failures
            if ok != expect_ok:
                print(f"phase1-tests-readme-self-test:{name}:unexpected={failures}")
                return 1

    print("PHASE1_TESTS_README_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_TESTS_README_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_TESTS_README_CLOSURE_PACKET_SAMPLE_ROOT=written")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_TESTS_README_CLOSURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_TESTS_README_CLOSURE_PACKET=pass")
    print(f"PHASE1_TESTS_README_CLOSURE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_TESTS_README_CLOSURE_PACKET_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
