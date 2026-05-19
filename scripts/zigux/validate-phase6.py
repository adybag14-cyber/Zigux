#!/usr/bin/env python3
"""Validate the current Phase 6 shared helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

HELPER_EVIDENCE_CATALOG = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")
PHASE6_BUILD = Path("zigux/tests/phase6_build.zig")
MAKEFILE = Path("zigux/Makefile")
SHARED_SURFACE_CHECKER = Path("scripts/zigux/check-phase6-shared-surface.py")
PRESENT_ENTRYPOINTS_CHECKER = Path("scripts/zigux/check-phase6-present-entrypoints.py")
HEXDUMP_ROUTE_CHECKER = Path("scripts/zigux/check-phase6-hexdump-route.py")

REQUIRED_FILES = [
    HELPER_EVIDENCE_CATALOG,
    HELPER_EVIDENCE_MANIFEST,
    HELPER_PARITY_MANIFEST,
    PHASE6_BUILD,
    MAKEFILE,
    SHARED_SURFACE_CHECKER,
    PRESENT_ENTRYPOINTS_CHECKER,
    HEXDUMP_ROUTE_CHECKER,
]

EXPECTED_HELPER_EVIDENCE_PACKET = "phase6-helper-evidence"
EXPECTED_HELPER_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_ROADMAP_ANCHORS = [
    "lib/base64.c",
    "lib/bsearch.c",
    "lib/checksum.c",
    "lib/hexdump.c",
]
EXPECTED_SHARED_REPLAY_INVENTORY = [
    "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-test",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-validate:",
    "$(PYTHON) scripts/zigux/validate-phase6.py",
    "phase6-base64-test:",
    "phase6-base64-perf:",
    "phase6-bsearch-test:",
    "phase6-checksum-test:",
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-hexdump-perf-matrix-test:",
    "$(ZIG) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-test:",
    "phase6-hexdump-perf:",
]

REQUIRED_BUILD_SNIPPETS = [
    'const base64_test_step = b.step("phase6-base64-test", "Run Phase 6 base64 helper tests");',
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
    'const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
    '"phase6-hexdump-perf-matrix-test",',
    'const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
]

REQUIRED_CATALOG_SNIPPETS = [
    "- lane scope: shared helper-evidence rows and machine-readable manifest only",
    "- directly readable shared build foothold: `zigux/tests/phase6_build.zig`",
    "- directly readable shared Makefile wrapper surface: `zigux/Makefile`",
    "- shared machine-readable manifest: `zigux/tests/phase6_helper_evidence_manifest.json`",
    "- returned helper-parity companion: `zigux/tests/phase6_helper_parity_manifest.json`",
    "## Current direct-readback warning",
    "## Roadmap perf-gap readback",
    "## Current shared replay inventory",
    "- `zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig`",
    "- `make -C zigux phase6-hexdump-perf-matrix-test`",
]

SELF_TEST_CASE_COUNT = 4


class ValidationError(RuntimeError):
    """Raised when the Phase 6 shared packet is not aligned."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}"
            )


def require_file_set(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))


def require_manifest_shape(
    manifest: dict[str, object],
    *,
    packet: str,
    phase: str,
    lane_scope: str,
    anchors: list[str],
    label: str,
) -> None:
    if manifest.get("packet") != packet:
        raise ValidationError(f"{label} packet drift: expected {packet}")
    if manifest.get("phase") != phase:
        raise ValidationError(f"{label} phase drift: expected {phase}")
    if manifest.get("lane_scope") != lane_scope:
        raise ValidationError(f"{label} lane_scope drift: expected {lane_scope}")
    if manifest.get("roadmap_anchors") != anchors:
        raise ValidationError(f"{label} roadmap_anchors drift")


def require_helper_keys(manifest: dict[str, object], expected: list[str], label: str) -> None:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"{label} helpers list missing")
    keys = [helper.get("key") for helper in helpers if isinstance(helper, dict)]
    if keys != expected:
        raise ValidationError(f"{label} helper key drift: expected {expected}, got {keys}")


def run_checker(root: Path, checker: Path, flag: str) -> None:
    result = subprocess.run(
        [sys.executable, str(root / checker), flag, str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        detail = stderr or stdout or f"exit {result.returncode}"
        raise ValidationError(f"{checker.as_posix()} failed: {detail}")


def validate(root: Path) -> None:
    require_file_set(root)

    helper_evidence_manifest = read_json(root / HELPER_EVIDENCE_MANIFEST)
    helper_parity_manifest = read_json(root / HELPER_PARITY_MANIFEST)

    require_manifest_shape(
        helper_evidence_manifest,
        packet=EXPECTED_HELPER_EVIDENCE_PACKET,
        phase=EXPECTED_PHASE,
        lane_scope="shared helper-evidence rows and machine-readable manifest only",
        anchors=EXPECTED_ROADMAP_ANCHORS,
        label="phase6_helper_evidence_manifest",
    )
    require_manifest_shape(
        helper_parity_manifest,
        packet=EXPECTED_HELPER_PARITY_PACKET,
        phase=EXPECTED_PHASE,
        lane_scope="shared helper-parity rows and machine-readable manifest only",
        anchors=EXPECTED_ROADMAP_ANCHORS,
        label="phase6_helper_parity_manifest",
    )

    require_helper_keys(
        helper_evidence_manifest,
        ["base64", "bsearch", "checksum", "hexdump"],
        "phase6_helper_evidence_manifest",
    )
    require_helper_keys(
        helper_parity_manifest,
        ["base64", "bsearch", "checksum", "hexdump"],
        "phase6_helper_parity_manifest",
    )

    if helper_evidence_manifest.get("current_shared_replay_inventory") != EXPECTED_SHARED_REPLAY_INVENTORY:
        raise ValidationError("phase6_helper_evidence_manifest current_shared_replay_inventory drift")

    require_snippets(root / MAKEFILE, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(root / PHASE6_BUILD, REQUIRED_BUILD_SNIPPETS)
    require_snippets(root / HELPER_EVIDENCE_CATALOG, REQUIRED_CATALOG_SNIPPETS)

    run_checker(root, SHARED_SURFACE_CHECKER, "--repo-root")
    run_checker(root, PRESENT_ENTRYPOINTS_CHECKER, "--repo-root")
    run_checker(root, HEXDUMP_ROUTE_CHECKER, "--root")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_mock_checker(path: Path) -> None:
    write(
        path,
        """#!/usr/bin/env python3
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--repo-root", dest="repo_root")
parser.add_argument("--root", dest="root")
parser.parse_args()
print("MOCK_PHASE6_CHECKER=pass")
sys.exit(0)
""",
    )


def scaffold_repo(root: Path) -> None:
    write(
        root / HELPER_EVIDENCE_CATALOG,
        "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n",
    )
    write(
        root / HELPER_EVIDENCE_MANIFEST,
        json.dumps(
            {
                "packet": EXPECTED_HELPER_EVIDENCE_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": "shared helper-evidence rows and machine-readable manifest only",
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "helpers": [{"key": key} for key in ["base64", "bsearch", "checksum", "hexdump"]],
                "current_shared_replay_inventory": EXPECTED_SHARED_REPLAY_INVENTORY,
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / HELPER_PARITY_MANIFEST,
        json.dumps(
            {
                "packet": EXPECTED_HELPER_PARITY_PACKET,
                "phase": EXPECTED_PHASE,
                "lane_scope": "shared helper-parity rows and machine-readable manifest only",
                "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
                "helpers": [{"key": key} for key in ["base64", "bsearch", "checksum", "hexdump"]],
            },
            indent=2,
        )
        + "\n",
    )
    write(root / PHASE6_BUILD, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKEFILE, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    scaffold_mock_checker(root / SHARED_SURFACE_CHECKER)
    scaffold_mock_checker(root / PRESENT_ENTRYPOINTS_CHECKER)
    scaffold_mock_checker(root / HEXDUMP_ROUTE_CHECKER)


def expect_failure(fn, expected_snippet: str) -> None:
    try:
        fn()
    except ValidationError as exc:
        message = str(exc)
        if expected_snippet not in message:
            raise AssertionError(
                f"expected {expected_snippet!r} in validation error, got {message!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_validate_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        manifest_path = root / HELPER_EVIDENCE_MANIFEST
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(original_manifest)
        manifest["packet"] = "wrong-packet"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(lambda: validate(root), "phase6_helper_evidence_manifest packet drift")
        write(manifest_path, original_manifest)
        cases_run += 1

        makefile_path = root / MAKEFILE
        original_makefile = makefile_path.read_text(encoding="utf-8")
        write(makefile_path, original_makefile.replace("phase6-hexdump-perf-matrix-test:\n", "", 1))
        expect_failure(lambda: validate(root), "phase6-hexdump-perf-matrix-test:")
        write(makefile_path, original_makefile)
        cases_run += 1

        checker_path = root / SHARED_SURFACE_CHECKER
        original_checker = checker_path.read_text(encoding="utf-8")
        write(checker_path, "#!/usr/bin/env python3\nraise SystemExit(1)\n")
        expect_failure(lambda: validate(root), "check-phase6-shared-surface.py failed")
        write(checker_path, original_checker)
        cases_run += 1

        parity_manifest_path = root / HELPER_PARITY_MANIFEST
        original_parity_manifest = parity_manifest_path.read_text(encoding="utf-8")
        parity_manifest = json.loads(original_parity_manifest)
        parity_manifest["helpers"] = [{"key": "base64"}]
        write(parity_manifest_path, json.dumps(parity_manifest, indent=2) + "\n")
        expect_failure(lambda: validate(root), "helper key drift")
        write(parity_manifest_path, original_parity_manifest)
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(
                f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}"
            )

    print("PHASE6_VALIDATOR_SELF_TEST=pass")
    print(f"PHASE6_VALIDATOR_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to validate (default: current directory tree)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in validator self-test",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_VALIDATION=fail: {exc}")
        return 1

    print("PHASE6_VALIDATION=pass")
    print(f"PHASE6_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE6_REQUIRED_MARKER_COUNT="
        f"{len(REQUIRED_MAKEFILE_SNIPPETS) + len(REQUIRED_BUILD_SNIPPETS) + len(REQUIRED_CATALOG_SNIPPETS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
