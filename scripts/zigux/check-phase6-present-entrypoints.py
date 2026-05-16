#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 shared entrypoint inventory."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
CHECKER_PATH = Path("scripts/zigux/check-phase6-present-entrypoints.py")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
BASE64_HELPER_PATH = Path("lib/base64.zig")
BASE64_REPLAY_PATH = Path("zigux/tests/phase6_base64.zig")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
BASE64_C_PARITY_PATH = Path("zigux/tests/phase6_base64_c_parity.zig")
BASE64_C_CASEGEN_PATH = Path("zigux/tests/phase6_base64_c_casegen.zig")
BASE64_C_PARITY_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig")
BASE64_C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_harness.c")
BASE64_C_PARITY_CHECKER_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")
BSEARCH_HELPER_PATH = Path("lib/bsearch.zig")
BSEARCH_REPLAY_PATH = Path("zigux/tests/phase6_bsearch.zig")
BSEARCH_LOWER_UPPER_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
BSEARCH_EQUALITY_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
BSEARCH_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
BSEARCH_CHECKER_PATH = Path("scripts/zigux/check-phase6-bsearch-corpus-evidence.py")
CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
CHECKSUM_REPLAY_PATH = Path("zigux/tests/phase6_checksum.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
CHECKSUM_C_PARITY_PATH = Path("zigux/tests/phase6_checksum_c_parity.zig")
CHECKSUM_C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_checksum_c_harness.c")
CHECKSUM_C_PARITY_CHECKER_PATH = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
HEXDUMP_HELPER_PATH = Path("lib/hexdump.zig")
HEXDUMP_REPLAY_PATH = Path("zigux/tests/phase6_hexdump.zig")
HEXDUMP_PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
HEXDUMP_PERF_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_CHECKER_PATH = Path("scripts/zigux/check-phase6-hexdump-packet.py")
HEXDUMP_PERF_REFRESH_PATH = Path("Documentation/zigux/phase6-hexdump-perf-refresh.md")

REQUIRED_SHARED_GATES = {
    CHECKER_PATH.as_posix(),
}

REQUIRED_PRESENT_ENTRYPOINTS = {
    MANIFEST_PATH.as_posix(),
    CHECKER_PATH.as_posix(),
    CATALOG_PATH.as_posix(),
    PERF_SURVEY_PATH.as_posix(),
    PHASE6_BUILD_PATH.as_posix(),
    BASE64_HELPER_PATH.as_posix(),
    BASE64_REPLAY_PATH.as_posix(),
    BASE64_PERF_PATH.as_posix(),
    BASE64_VECTORS_PATH.as_posix(),
    BASE64_C_PARITY_PATH.as_posix(),
    BASE64_C_CASEGEN_PATH.as_posix(),
    BASE64_C_PARITY_VECTORS_PATH.as_posix(),
    BASE64_C_HARNESS_PATH.as_posix(),
    BASE64_C_PARITY_CHECKER_PATH.as_posix(),
    BSEARCH_HELPER_PATH.as_posix(),
    BSEARCH_REPLAY_PATH.as_posix(),
    BSEARCH_LOWER_UPPER_PATH.as_posix(),
    BSEARCH_EQUALITY_PATH.as_posix(),
    BSEARCH_VECTORS_PATH.as_posix(),
    BSEARCH_CHECKER_PATH.as_posix(),
    CHECKSUM_HELPER_PATH.as_posix(),
    CHECKSUM_REPLAY_PATH.as_posix(),
    CHECKSUM_PERF_PATH.as_posix(),
    CHECKSUM_VECTORS_PATH.as_posix(),
    CHECKSUM_C_PARITY_PATH.as_posix(),
    CHECKSUM_C_HARNESS_PATH.as_posix(),
    CHECKSUM_C_PARITY_CHECKER_PATH.as_posix(),
    HEXDUMP_HELPER_PATH.as_posix(),
    HEXDUMP_REPLAY_PATH.as_posix(),
    HEXDUMP_PERF_PATH.as_posix(),
    HEXDUMP_PERF_MATRIX_PATH.as_posix(),
    HEXDUMP_VECTORS_PATH.as_posix(),
    HEXDUMP_CHECKER_PATH.as_posix(),
    HEXDUMP_PERF_REFRESH_PATH.as_posix(),
}

REQUIRED_EXACT_CHECKS = {
    "python3 scripts/zigux/check-phase6-present-entrypoints.py",
    "python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test",
}

EXPECTED_BASE64_HELPER = BASE64_HELPER_PATH.as_posix()
EXPECTED_BASE64_TESTS = {
    BASE64_REPLAY_PATH.as_posix(),
    BASE64_C_PARITY_PATH.as_posix(),
    BASE64_PERF_PATH.as_posix(),
}
EXPECTED_BASE64_FIXTURES = {
    BASE64_VECTORS_PATH.as_posix(),
    BASE64_C_PARITY_VECTORS_PATH.as_posix(),
    BASE64_C_HARNESS_PATH.as_posix(),
}
EXPECTED_BASE64_EXTERNAL_PARITY = BASE64_C_PARITY_CHECKER_PATH.as_posix()
EXPECTED_BSEARCH_HELPER = BSEARCH_HELPER_PATH.as_posix()
EXPECTED_BSEARCH_TESTS = {
    BSEARCH_REPLAY_PATH.as_posix(),
    BSEARCH_LOWER_UPPER_PATH.as_posix(),
    BSEARCH_EQUALITY_PATH.as_posix(),
}
EXPECTED_BSEARCH_FIXTURES = {
    BSEARCH_VECTORS_PATH.as_posix(),
}
EXPECTED_BSEARCH_CORPUS_CHECKER = BSEARCH_CHECKER_PATH.as_posix()
EXPECTED_CHECKSUM_HELPER = CHECKSUM_HELPER_PATH.as_posix()
EXPECTED_CHECKSUM_TESTS = {
    CHECKSUM_REPLAY_PATH.as_posix(),
    CHECKSUM_PERF_PATH.as_posix(),
    CHECKSUM_C_PARITY_PATH.as_posix(),
}
EXPECTED_CHECKSUM_FIXTURES = {
    CHECKSUM_VECTORS_PATH.as_posix(),
    CHECKSUM_C_HARNESS_PATH.as_posix(),
}
EXPECTED_CHECKSUM_EXTERNAL_PARITY = CHECKSUM_C_PARITY_CHECKER_PATH.as_posix()
EXPECTED_HEXDUMP_HELPER = HEXDUMP_HELPER_PATH.as_posix()
EXPECTED_HEXDUMP_TESTS = {
    HEXDUMP_REPLAY_PATH.as_posix(),
    HEXDUMP_PERF_PATH.as_posix(),
    HEXDUMP_PERF_MATRIX_PATH.as_posix(),
}
EXPECTED_HEXDUMP_FIXTURES = {
    HEXDUMP_VECTORS_PATH.as_posix(),
}
EXPECTED_HEXDUMP_PACKET_CHECKER = HEXDUMP_CHECKER_PATH.as_posix()
EXPECTED_HEXDUMP_PERF_REFRESH = HEXDUMP_PERF_REFRESH_PATH.as_posix()

SELF_TEST_CASE_COUNT = 31


def read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc


def validate_paths(repo_root: Path) -> None:
    for rel_path in sorted(REQUIRED_PRESENT_ENTRYPOINTS):
        if not (repo_root / rel_path).is_file():
            raise ValidationError(f"missing required file: {rel_path}")


def helper_row(manifest_obj: dict[str, object], helper_id: str) -> dict[str, object]:
    helpers = manifest_obj.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers in {MANIFEST_PATH.as_posix()}")

    row = next(
        (item for item in helpers if isinstance(item, dict) and item.get("id") == helper_id),
        None,
    )
    if not isinstance(row, dict):
        raise ValidationError(f"missing {helper_id} helper row in {MANIFEST_PATH.as_posix()}")
    return row


def validate_manifest(repo_root: Path) -> None:
    manifest_obj = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest_obj, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH.as_posix()}")

    shared_gates = manifest_obj.get("shared_gates")
    if not isinstance(shared_gates, list):
        raise ValidationError(f"missing shared_gates in {MANIFEST_PATH.as_posix()}")
    for rel_path in REQUIRED_SHARED_GATES:
        if rel_path not in shared_gates:
            raise ValidationError(f"missing shared gate in {MANIFEST_PATH.as_posix()}: {rel_path}")

    present_entrypoints = manifest_obj.get("tests_root_present_entrypoints")
    if not isinstance(present_entrypoints, list):
        raise ValidationError(f"missing tests_root_present_entrypoints in {MANIFEST_PATH.as_posix()}")
    for rel_path in REQUIRED_PRESENT_ENTRYPOINTS:
        if rel_path not in present_entrypoints:
            raise ValidationError(
                f"missing tests_root_present_entrypoint in {MANIFEST_PATH.as_posix()}: {rel_path}"
            )

    exact_checks = manifest_obj.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks in {MANIFEST_PATH.as_posix()}")
    for command in REQUIRED_EXACT_CHECKS:
        if command not in exact_checks:
            raise ValidationError(f"missing exact check in {MANIFEST_PATH.as_posix()}: {command}")

    base64_helper = helper_row(manifest_obj, "base64")
    if base64_helper.get("helper") != EXPECTED_BASE64_HELPER:
        raise ValidationError(
            f"unexpected base64 helper path in {MANIFEST_PATH.as_posix()}: "
            f"{base64_helper.get('helper')!r}"
        )
    if set(base64_helper.get("tests") or []) != EXPECTED_BASE64_TESTS:
        raise ValidationError(
            f"unexpected base64 tests list in {MANIFEST_PATH.as_posix()}: "
            f"{base64_helper.get('tests')!r}"
        )
    if set(base64_helper.get("fixtures") or []) != EXPECTED_BASE64_FIXTURES:
        raise ValidationError(
            f"unexpected base64 fixtures list in {MANIFEST_PATH.as_posix()}: "
            f"{base64_helper.get('fixtures')!r}"
        )
    if base64_helper.get("external_parity") != EXPECTED_BASE64_EXTERNAL_PARITY:
        raise ValidationError(
            f"unexpected base64 external parity checker in {MANIFEST_PATH.as_posix()}: "
            f"{base64_helper.get('external_parity')!r}"
        )

    bsearch_helper = helper_row(manifest_obj, "bsearch")
    if bsearch_helper.get("helper") != EXPECTED_BSEARCH_HELPER:
        raise ValidationError(
            f"unexpected bsearch helper path in {MANIFEST_PATH.as_posix()}: "
            f"{bsearch_helper.get('helper')!r}"
        )
    if set(bsearch_helper.get("tests") or []) != EXPECTED_BSEARCH_TESTS:
        raise ValidationError(
            f"unexpected bsearch tests list in {MANIFEST_PATH.as_posix()}: "
            f"{bsearch_helper.get('tests')!r}"
        )
    if set(bsearch_helper.get("fixtures") or []) != EXPECTED_BSEARCH_FIXTURES:
        raise ValidationError(
            f"unexpected bsearch fixtures list in {MANIFEST_PATH.as_posix()}: "
            f"{bsearch_helper.get('fixtures')!r}"
        )
    if bsearch_helper.get("corpus_evidence_checker") != EXPECTED_BSEARCH_CORPUS_CHECKER:
        raise ValidationError(
            f"unexpected bsearch corpus checker in {MANIFEST_PATH.as_posix()}: "
            f"{bsearch_helper.get('corpus_evidence_checker')!r}"
        )

    checksum_helper = helper_row(manifest_obj, "checksum")
    if checksum_helper.get("helper") != EXPECTED_CHECKSUM_HELPER:
        raise ValidationError(
            f"unexpected checksum helper path in {MANIFEST_PATH.as_posix()}: "
            f"{checksum_helper.get('helper')!r}"
        )
    if set(checksum_helper.get("tests") or []) != EXPECTED_CHECKSUM_TESTS:
        raise ValidationError(
            f"unexpected checksum tests list in {MANIFEST_PATH.as_posix()}: "
            f"{checksum_helper.get('tests')!r}"
        )
    if set(checksum_helper.get("fixtures") or []) != EXPECTED_CHECKSUM_FIXTURES:
        raise ValidationError(
            f"unexpected checksum fixtures list in {MANIFEST_PATH.as_posix()}: "
            f"{checksum_helper.get('fixtures')!r}"
        )
    if checksum_helper.get("external_parity") != EXPECTED_CHECKSUM_EXTERNAL_PARITY:
        raise ValidationError(
            f"unexpected checksum external parity checker in {MANIFEST_PATH.as_posix()}: "
            f"{checksum_helper.get('external_parity')!r}"
        )

    hexdump_helper = helper_row(manifest_obj, "hexdump")
    if hexdump_helper.get("helper") != EXPECTED_HEXDUMP_HELPER:
        raise ValidationError(
            f"unexpected hexdump helper path in {MANIFEST_PATH.as_posix()}: "
            f"{hexdump_helper.get('helper')!r}"
        )
    if set(hexdump_helper.get("tests") or []) != EXPECTED_HEXDUMP_TESTS:
        raise ValidationError(
            f"unexpected hexdump tests list in {MANIFEST_PATH.as_posix()}: "
            f"{hexdump_helper.get('tests')!r}"
        )
    if set(hexdump_helper.get("fixtures") or []) != EXPECTED_HEXDUMP_FIXTURES:
        raise ValidationError(
            f"unexpected hexdump fixtures list in {MANIFEST_PATH.as_posix()}: "
            f"{hexdump_helper.get('fixtures')!r}"
        )
    if hexdump_helper.get("packet_checker") != EXPECTED_HEXDUMP_PACKET_CHECKER:
        raise ValidationError(
            f"unexpected hexdump packet checker in {MANIFEST_PATH.as_posix()}: "
            f"{hexdump_helper.get('packet_checker')!r}"
        )
    if hexdump_helper.get("perf_refresh_note") != EXPECTED_HEXDUMP_PERF_REFRESH:
        raise ValidationError(
            f"unexpected hexdump perf refresh note in {MANIFEST_PATH.as_posix()}: "
            f"{hexdump_helper.get('perf_refresh_note')!r}"
        )


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_manifest() -> dict[str, object]:
    return {
        "shared_gates": sorted(REQUIRED_SHARED_GATES),
        "tests_root_present_entrypoints": sorted(REQUIRED_PRESENT_ENTRYPOINTS),
        "exact_checks": sorted(REQUIRED_EXACT_CHECKS),
        "helpers": [
            {
                "id": "base64",
                "helper": EXPECTED_BASE64_HELPER,
                "tests": sorted(EXPECTED_BASE64_TESTS),
                "fixtures": sorted(EXPECTED_BASE64_FIXTURES),
                "external_parity": EXPECTED_BASE64_EXTERNAL_PARITY,
            },
            {
                "id": "bsearch",
                "helper": EXPECTED_BSEARCH_HELPER,
                "tests": sorted(EXPECTED_BSEARCH_TESTS),
                "fixtures": sorted(EXPECTED_BSEARCH_FIXTURES),
                "corpus_evidence_checker": EXPECTED_BSEARCH_CORPUS_CHECKER,
            },
            {
                "id": "checksum",
                "helper": EXPECTED_CHECKSUM_HELPER,
                "tests": sorted(EXPECTED_CHECKSUM_TESTS),
                "fixtures": sorted(EXPECTED_CHECKSUM_FIXTURES),
                "external_parity": EXPECTED_CHECKSUM_EXTERNAL_PARITY,
            },
            {
                "id": "hexdump",
                "helper": EXPECTED_HEXDUMP_HELPER,
                "tests": sorted(EXPECTED_HEXDUMP_TESTS),
                "fixtures": sorted(EXPECTED_HEXDUMP_FIXTURES),
                "packet_checker": EXPECTED_HEXDUMP_PACKET_CHECKER,
                "perf_refresh_note": EXPECTED_HEXDUMP_PERF_REFRESH,
            },
        ],
    }


def scaffold_repo(root: Path) -> None:
    write(root / MANIFEST_PATH, json.dumps(build_manifest(), indent=2) + "\n")
    write(root / CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / CATALOG_PATH, "# Phase 6 Helper Parity Catalog\n")
    write(root / PERF_SURVEY_PATH, "# Phase 6 Perf Gate Survey\n")
    write(root / PHASE6_BUILD_PATH, "const std = @import(\"std\");\n")
    write(root / BASE64_HELPER_PATH, "pub fn base64Stub() void {}\n")
    write(root / BASE64_REPLAY_PATH, "test \"base64\" {}\n")
    write(root / BASE64_PERF_PATH, "test \"base64 perf\" {}\n")
    write(root / BASE64_VECTORS_PATH, "pub const perf_cases = .{};\n")
    write(root / BASE64_C_PARITY_PATH, "test \"base64 c parity\" {}\n")
    write(root / BASE64_C_CASEGEN_PATH, "pub fn main() void {}\n")
    write(root / BASE64_C_PARITY_VECTORS_PATH, "pub const c_parity_cases = .{};\n")
    write(root / BASE64_C_HARNESS_PATH, "/* base64 harness */\n")
    write(root / BASE64_C_PARITY_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / BSEARCH_HELPER_PATH, "pub fn bsearchStub() void {}\n")
    write(root / BSEARCH_REPLAY_PATH, "test \"bsearch\" {}\n")
    write(root / BSEARCH_LOWER_UPPER_PATH, "test \"bsearch lower upper\" {}\n")
    write(root / BSEARCH_EQUALITY_PATH, "test \"bsearch equality\" {}\n")
    write(root / BSEARCH_VECTORS_PATH, "pub const representative_cases = .{};\n")
    write(root / BSEARCH_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / CHECKSUM_HELPER_PATH, "pub fn checksumStub() void {}\n")
    write(root / CHECKSUM_REPLAY_PATH, "test \"checksum\" {}\n")
    write(root / CHECKSUM_PERF_PATH, "test \"checksum perf\" {}\n")
    write(root / CHECKSUM_VECTORS_PATH, "pub const perf_cases = .{};\n")
    write(root / CHECKSUM_C_PARITY_PATH, "test \"checksum c parity\" {}\n")
    write(root / CHECKSUM_C_HARNESS_PATH, "/* checksum harness */\n")
    write(root / CHECKSUM_C_PARITY_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / HEXDUMP_HELPER_PATH, "pub fn hexdumpStub() void {}\n")
    write(root / HEXDUMP_REPLAY_PATH, "test \"hexdump\" {}\n")
    write(root / HEXDUMP_PERF_PATH, "test \"hexdump perf\" {}\n")
    write(root / HEXDUMP_PERF_MATRIX_PATH, "test \"hexdump perf matrix\" {}\n")
    write(root / HEXDUMP_VECTORS_PATH, "pub const grouped_cases = .{};\n")
    write(root / HEXDUMP_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / HEXDUMP_PERF_REFRESH_PATH, "# Phase 6 Hexdump Perf Refresh Evidence\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_checks(root)
    except ValidationError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase6_present_entrypoints_"))
    try:
        scaffold_repo(tmpdir)
        run_checks(tmpdir)

        manifest_path = tmpdir / MANIFEST_PATH

        manifest = build_manifest()
        manifest["shared_gates"] = []
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, CHECKER_PATH.as_posix())

        manifest = build_manifest()
        manifest["tests_root_present_entrypoints"] = sorted(
            REQUIRED_PRESENT_ENTRYPOINTS - {BASE64_C_PARITY_VECTORS_PATH.as_posix()}
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, BASE64_C_PARITY_VECTORS_PATH.as_posix())

        manifest = build_manifest()
        manifest["exact_checks"] = ["python3 scripts/zigux/check-phase6-present-entrypoints.py"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "--self-test")

        manifest = build_manifest()
        manifest["helpers"][0]["helper"] = "lib/base64_missing.zig"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected base64 helper path")

        manifest = build_manifest()
        manifest["helpers"][0]["fixtures"] = sorted(
            EXPECTED_BASE64_FIXTURES - {BASE64_C_PARITY_VECTORS_PATH.as_posix()}
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected base64 fixtures list")

        manifest = build_manifest()
        manifest["helpers"][0]["external_parity"] = "scripts/zigux/check-phase6-base64-proof.py"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected base64 external parity checker")

        manifest = build_manifest()
        manifest["helpers"] = [row for row in manifest["helpers"] if row["id"] != "base64"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "missing base64 helper row")

        manifest = build_manifest()
        manifest["helpers"][1]["helper"] = "lib/bsearch_missing.zig"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected bsearch helper path")

        manifest = build_manifest()
        manifest["helpers"][1]["tests"] = sorted(
            EXPECTED_BSEARCH_TESTS - {BSEARCH_EQUALITY_PATH.as_posix()}
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected bsearch tests list")

        manifest = build_manifest()
        manifest["helpers"][1]["fixtures"] = []
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected bsearch fixtures list")

        manifest = build_manifest()
        manifest["helpers"][1]["corpus_evidence_checker"] = "scripts/zigux/check-phase6-bsearch-proof.py"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected bsearch corpus checker")

        manifest = build_manifest()
        manifest["helpers"] = [row for row in manifest["helpers"] if row["id"] != "bsearch"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "missing bsearch helper row")

        manifest = build_manifest()
        manifest["helpers"][2]["helper"] = "lib/checksum_missing.zig"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected checksum helper path")

        manifest = build_manifest()
        manifest["helpers"][2]["tests"] = sorted(
            EXPECTED_CHECKSUM_TESTS - {CHECKSUM_PERF_PATH.as_posix()}
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected checksum tests list")

        manifest = build_manifest()
        manifest["helpers"][2]["external_parity"] = "scripts/zigux/check-phase6-checksum-proof.py"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected checksum external parity checker")

        manifest = build_manifest()
        manifest["helpers"] = [row for row in manifest["helpers"] if row["id"] != "checksum"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "missing checksum helper row")

        manifest = build_manifest()
        manifest["helpers"][3]["helper"] = "lib/hexdump_missing.zig"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected hexdump helper path")

        manifest = build_manifest()
        manifest["helpers"][3]["tests"] = sorted(
            EXPECTED_HEXDUMP_TESTS - {HEXDUMP_PERF_MATRIX_PATH.as_posix()}
        )
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected hexdump tests list")

        manifest = build_manifest()
        manifest["helpers"][3]["fixtures"] = []
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected hexdump fixtures list")

        manifest = build_manifest()
        manifest["helpers"][3]["packet_checker"] = "scripts/zigux/check-phase6-hexdump-review.py"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected hexdump packet checker")

        manifest = build_manifest()
        manifest["helpers"][3]["perf_refresh_note"] = "Documentation/zigux/phase6-hexdump-perf-old.md"
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "unexpected hexdump perf refresh note")

        manifest = build_manifest()
        manifest["helpers"] = [row for row in manifest["helpers"] if row["id"] != "hexdump"]
        write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        expect_failure(tmpdir, "missing hexdump helper row")

        scaffold_repo(tmpdir)
        (tmpdir / BASE64_C_CASEGEN_PATH).unlink()
        expect_failure(tmpdir, BASE64_C_CASEGEN_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / BASE64_C_PARITY_CHECKER_PATH).unlink()
        expect_failure(tmpdir, BASE64_C_PARITY_CHECKER_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / CATALOG_PATH).unlink()
        expect_failure(tmpdir, CATALOG_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / BSEARCH_EQUALITY_PATH).unlink()
        expect_failure(tmpdir, BSEARCH_EQUALITY_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / BSEARCH_CHECKER_PATH).unlink()
        expect_failure(tmpdir, BSEARCH_CHECKER_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / CHECKSUM_C_PARITY_CHECKER_PATH).unlink()
        expect_failure(tmpdir, CHECKSUM_C_PARITY_CHECKER_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / HEXDUMP_PERF_PATH).unlink()
        expect_failure(tmpdir, HEXDUMP_PERF_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / HEXDUMP_CHECKER_PATH).unlink()
        expect_failure(tmpdir, HEXDUMP_CHECKER_PATH.as_posix())

        scaffold_repo(tmpdir)
        (tmpdir / HEXDUMP_PERF_REFRESH_PATH).unlink()
        expect_failure(tmpdir, HEXDUMP_PERF_REFRESH_PATH.as_posix())

        print("PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass")
        print(f"PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 shared present-entrypoint inventory looks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
