#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

TESTS_README_PATH = Path("zigux/tests/README.md")
MAKEFILE_PATH = Path("zigux/Makefile")

DIRECT_PACKET_PATHS = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-string-review-packet.py",
    "scripts/zigux/check-phase1-direct-owner-markers.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/README.md",
)

BROADER_COMPANION_PATHS = (
    "scripts/zigux/validate-phase1.py",
    "scripts/zigux/check-phase1-parity.py",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/phase1_bench.zig",
    "zigux/tests/fixtures/phase1_bench_expectations.json",
    "zigux/tests/fixtures/phase1_helpers_c_harness.c",
)

REQUIRED_MARKERS = (
    "## Phase 1 host-tools review packet",
    "* current direct-readback Phase 1 reminder packet:",
    "* current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "* current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof",
    "* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
    "* keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
    "Tests-root reviewer prompt:",
    "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    readme = _read(root / TESTS_README_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in readme:
            failures.append(f"tests_readme:missing:{marker}")

    for rel in DIRECT_PACKET_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"tests_readme:missing_direct_path:`{rel}`")
        if not (root / rel).exists():
            failures.append(f"repo:missing_direct_path:{rel}")

    if not (root / MAKEFILE_PATH).exists():
        failures.append(f"repo:missing_present_path:{MAKEFILE_PATH}")

    for rel in BROADER_COMPANION_PATHS:
        if f"`{rel}`" not in readme:
            failures.append(f"tests_readme:missing_broader_companion:`{rel}`")

    return failures


def _sample_readme() -> str:
    direct = "\n".join(f"- `{rel}`" for rel in DIRECT_PACKET_PATHS[:-1])
    return f"""# zigux/tests

## Phase 1 host-tools review packet

  * current direct-readback Phase 1 reminder packet:
{direct}
- `zigux/tests/README.md`

  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
  * current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with the bounded `phase3-validate` and `phase3` routes plus the later Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14 route families, so treat the returned file as current repo evidence while the older Phase 1 wrapper names remain historical packet members rather than active tests-root proof
  * broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet
  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`

Tests-root reviewer prompt:
- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?
"""


def _seed(root: Path) -> None:
    _write(root / TESTS_README_PATH, _sample_readme())
    for rel in DIRECT_PACKET_PATHS:
        if rel == TESTS_README_PATH.as_posix():
            continue
        _write(root / rel, "present\n")
    _write(root / MAKEFILE_PATH, "present\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1_tests_readme_alignment_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_direct_root = root / "missing_direct"
        _seed(missing_direct_root)
        (missing_direct_root / "scripts/zigux/check-phase1-bench.py").unlink()
        failures = collect_failures(missing_direct_root)
        expected = ["repo:missing_direct_path:scripts/zigux/check-phase1-bench.py"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-direct failure: {failures}")

        missing_companion_root = root / "missing_companion_marker"
        _seed(missing_companion_root)
        _write(
            missing_companion_root / TESTS_README_PATH,
            _sample_readme().replace("`zigux/tests/phase1_bench.zig`, ", "", 1),
        )
        failures = collect_failures(missing_companion_root)
        expected = [
            "tests_readme:missing:* broader Phase 1 closure companions stay outside the narrow direct-readback packet: authenticated contents reads on current `master` still return missing for `scripts/zigux/validate-phase1.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, but current public-tree readback does rematerialize that validator-first, bench, and replay family on `master`, so keep those paths framed as broader closure companions rather than as active tests-root proof inside this direct-readback reminder packet",
            "tests_readme:missing_broader_companion:`zigux/tests/phase1_bench.zig`",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing-companion failure: {failures}")

        missing_makefile_root = root / "missing_makefile"
        _seed(missing_makefile_root)
        (missing_makefile_root / MAKEFILE_PATH).unlink()
        failures = collect_failures(missing_makefile_root)
        expected = ["repo:missing_present_path:zigux/Makefile"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-makefile failure: {failures}")

    print("PHASE1_TESTS_README_ALIGNMENT_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 1 tests-root reminder stays aligned with the current closure packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE1_TESTS_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
