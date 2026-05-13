#!/usr/bin/env python3

"""Fail-closed Phase 6 checksum packet truthfulness checks."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_PRESENT_FILE_PATHS = [
    "Documentation/zigux/phase6-checksum-slice.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
]

REQUIRED_ABSENT_FILE_PATHS = [
    "lib/checksum.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
]

REQUIRED_SNIPPETS = {
    "Documentation/zigux/phase6-checksum-slice.md": [
        "`PHASE6_STATUS=blocked`",
        "still-present direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "current missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "blocked route note: the checked-in direct C parity scaffolding is not currently runnable as a complete packet because `zigux/tests/phase6_checksum_c_parity.zig` still imports the absent `lib/checksum.zig` helper and the absent `zigux/tests/fixtures/phase6_checksum_vectors.zig` fixture module",
        "stale shared route surfaces that still point at the absent broader checksum helper packet: `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
    ],
    "Documentation/zigux/phase6-helper-parity-catalog.md": [
        "`lib/checksum.c`",
        "helper expected by the shared packet: `lib/checksum.zig`",
        "still-present direct C parity scaffolding: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "current missing helper-local helper and perf packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `27` direct C parity cases",
    ],
    "Documentation/zigux/phase6-perf-gate-survey.md": [
        "checksum shared posture: `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still advertise a dedicated checksum slowdown gate, but current `master` lacks `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`, so that replay is currently not runnable from the committed tree",
        "checksum exact thresholds: the last checksum packet documented `64B` at `iterations = 200_000` and `1501B` at `iterations = 12_000` with `max_slowdown_pct = 150`",
    ],
    "scripts/zigux/check-phase6-checksum-c-parity.py": [
        "PHASE6_CHECKSUM_C_PARITY=blocked",
        'FIXTURE_IPV6_PSEUDO_HEADER_CASE_MARKER = "pub const ipv6_pseudo_header_cases = [_]Ipv6PseudoHeaderCase"',
        'FIXTURE_CARRY_DISCIPLINE_CASE_MARKER = "pub const carry_discipline_cases = [_]CarryDisciplineCase"',
        "FIXED_DIRECT_16BIT_CARRY_CASE_COUNT = 5",
        '"carry-discipline\\tall-ones even payload with zero seed\\t0x0000"',
        '"tcpudpv6-nofold\\tudp doc payload odd\\t0x0000f876"',
    ],
}

MANIFEST_CHECKSUM_TESTS = [
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/phase6_checksum_c_parity.zig",
]

MANIFEST_CHECKSUM_FIXTURES = [
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
]

MANIFEST_PRESENT_ENTRYPOINTS = [
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]

MANIFEST_PUBLIC_TREE_GAPS = [
    "lib/checksum.zig",
    "zigux/tests/phase6_checksum.zig",
    "zigux/tests/phase6_checksum_perf.zig",
    "zigux/tests/fixtures/phase6_checksum_vectors.zig",
]

MANIFEST_BLOCKED_ROUTES = [
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "make -C zigux phase6-checksum-c-parity",
    "make -C zigux phase6-checksum-perf",
]

SELF_TEST_MANIFEST = {
    "packet_state_summary": {
        "checksum": "blocked_helper_packet_missing",
    },
    "helpers": [
        {
            "id": "checksum",
            "helper": "lib/checksum.zig",
            "tests": MANIFEST_CHECKSUM_TESTS,
            "fixtures": MANIFEST_CHECKSUM_FIXTURES,
            "external_parity": "scripts/zigux/check-phase6-checksum-c-parity.py",
        }
    ],
    "tests_root_present_entrypoints": MANIFEST_PRESENT_ENTRYPOINTS,
    "tests_root_public_tree_gaps": MANIFEST_PUBLIC_TREE_GAPS,
    "inventory_only_blocked_routes": MANIFEST_BLOCKED_ROUTES,
    "exact_checks": [
        "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test",
    ],
    "determinism_evidence": {
        "checksum": {
            "c_parity_cases": 27,
        }
    },
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path):
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json file: {path.as_posix()}: {exc}") from exc


def validate_manifest(repo_root: Path) -> list[str]:
    missing: list[str] = []
    manifest_path = repo_root / "zigux/tests/phase6_helper_parity_manifest.json"
    try:
        manifest = read_json(manifest_path)
    except ValidationError as exc:
        return [str(exc)]

    packet_state_summary = manifest.get("packet_state_summary", {})
    if packet_state_summary.get("checksum") != "blocked_helper_packet_missing":
        missing.append(
            "zigux/tests/phase6_helper_parity_manifest.json: packet_state_summary.checksum=blocked_helper_packet_missing"
        )

    helpers = manifest.get("helpers")
    checksum_helper = None
    if isinstance(helpers, list):
        checksum_helper = next((helper for helper in helpers if helper.get("id") == "checksum"), None)
    if checksum_helper is None:
        missing.append("zigux/tests/phase6_helper_parity_manifest.json: helpers.checksum present")
    else:
        if checksum_helper.get("helper") != "lib/checksum.zig":
            missing.append("zigux/tests/phase6_helper_parity_manifest.json: helpers.checksum.helper=lib/checksum.zig")
        for path in MANIFEST_CHECKSUM_TESTS:
            if path not in checksum_helper.get("tests", []):
                missing.append(f"zigux/tests/phase6_helper_parity_manifest.json: helpers.checksum.tests contains {path}")
        for path in MANIFEST_CHECKSUM_FIXTURES:
            if path not in checksum_helper.get("fixtures", []):
                missing.append(f"zigux/tests/phase6_helper_parity_manifest.json: helpers.checksum.fixtures contains {path}")
        if checksum_helper.get("external_parity") != "scripts/zigux/check-phase6-checksum-c-parity.py":
            missing.append(
                "zigux/tests/phase6_helper_parity_manifest.json: helpers.checksum.external_parity=scripts/zigux/check-phase6-checksum-c-parity.py"
            )

    present_entrypoints = manifest.get("tests_root_present_entrypoints", [])
    for path in MANIFEST_PRESENT_ENTRYPOINTS:
        if path not in present_entrypoints:
            missing.append(f"zigux/tests/phase6_helper_parity_manifest.json: tests_root_present_entrypoints contains {path}")

    public_tree_gaps = manifest.get("tests_root_public_tree_gaps", [])
    for path in MANIFEST_PUBLIC_TREE_GAPS:
        if path not in public_tree_gaps:
            missing.append(f"zigux/tests/phase6_helper_parity_manifest.json: tests_root_public_tree_gaps contains {path}")

    blocked_routes = manifest.get("inventory_only_blocked_routes", [])
    for route in MANIFEST_BLOCKED_ROUTES:
        if route not in blocked_routes:
            missing.append(f"zigux/tests/phase6_helper_parity_manifest.json: inventory_only_blocked_routes contains {route}")

    exact_checks = manifest.get("exact_checks", [])
    if "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test" not in exact_checks:
        missing.append(
            "zigux/tests/phase6_helper_parity_manifest.json: exact_checks contains python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test"
        )
    if "python3 scripts/zigux/check-phase6-checksum-c-parity.py" in exact_checks:
        missing.append(
            "zigux/tests/phase6_helper_parity_manifest.json: exact_checks omits blocked direct checksum parity replay"
        )

    checksum_evidence = manifest.get("determinism_evidence", {}).get("checksum", {})
    if checksum_evidence.get("c_parity_cases") != 27:
        missing.append(
            "zigux/tests/phase6_helper_parity_manifest.json: determinism_evidence.checksum.c_parity_cases=27"
        )

    return missing


def validate(repo_root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in REQUIRED_PRESENT_FILE_PATHS:
        if not (repo_root / relative_path).is_file():
            missing.append(f"missing required file: {relative_path}")
    for relative_path in REQUIRED_ABSENT_FILE_PATHS:
        if (repo_root / relative_path).exists():
            missing.append(f"unexpected present file: {relative_path}")
    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        try:
            text = read_text(repo_root / relative_path)
        except ValidationError as exc:
            missing.append(str(exc))
            continue
        for snippet in snippets:
            if snippet not in text:
                missing.append(f"{relative_path}: {snippet}")
    missing.extend(validate_manifest(repo_root))
    return missing


def write_fixture(root: Path) -> None:
    for relative_path in REQUIRED_PRESENT_FILE_PATHS:
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("// fixture marker\n", encoding="utf-8")
    for relative_path, snippets in REQUIRED_SNIPPETS.items():
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(snippets) + "\n", encoding="utf-8")
    manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(SELF_TEST_MANIFEST, indent=2) + "\n", encoding="utf-8")


def expect_failure(repo_root: Path, needle: str) -> None:
    missing = validate(repo_root)
    if needle not in missing:
        raise ValidationError(f"expected self-test failure for {needle!r}, got {missing!r}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_fixture(root)

        missing = validate(root)
        if missing:
            raise ValidationError(f"self-test positive case failed: {missing!r}")

        slice_path = root / "Documentation/zigux/phase6-checksum-slice.md"
        slice_text = slice_path.read_text(encoding="utf-8")
        removed = "`PHASE6_STATUS=blocked`"
        slice_path.write_text(slice_text.replace(removed, "", 1), encoding="utf-8")
        expect_failure(root, f"Documentation/zigux/phase6-checksum-slice.md: {removed}")

        write_fixture(root)
        manifest_path = root / "zigux/tests/phase6_helper_parity_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["determinism_evidence"]["checksum"]["c_parity_cases"] = 26
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(
            root,
            "zigux/tests/phase6_helper_parity_manifest.json: determinism_evidence.checksum.c_parity_cases=27",
        )

        write_fixture(root)
        helper_path = root / "lib/checksum.zig"
        helper_path.parent.mkdir(parents=True, exist_ok=True)
        helper_path.write_text("// unexpectedly restored helper marker\n", encoding="utf-8")
        expect_failure(root, "unexpected present file: lib/checksum.zig")

        print("PHASE6_CHECKSUM_PACKET_SELF_TEST=pass")
        print(
            "PHASE6_CHECKSUM_PACKET_REQUIRED_FILE_COUNT=%d"
            % (len(REQUIRED_PRESENT_FILE_PATHS) + len(REQUIRED_ABSENT_FILE_PATHS) + len(REQUIRED_SNIPPETS))
        )
        print(
            "PHASE6_CHECKSUM_PACKET_REQUIRED_SNIPPET_COUNT=%d"
            % sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker tests")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    missing = validate(Path(args.repo_root).resolve())
    if missing:
        print("PHASE6_CHECKSUM_PACKET=fail")
        print("MISSING_PHASE6_CHECKSUM_PACKET_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE6_CHECKSUM_PACKET_MARKERS_END")
        return 1

    print("PHASE6_CHECKSUM_PACKET=pass")
    print(
        "PHASE6_CHECKSUM_PACKET_REQUIRED_FILE_COUNT=%d"
        % (len(REQUIRED_PRESENT_FILE_PATHS) + len(REQUIRED_ABSENT_FILE_PATHS) + len(REQUIRED_SNIPPETS))
    )
    print(
        "PHASE6_CHECKSUM_PACKET_REQUIRED_SNIPPET_COUNT=%d"
        % sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())