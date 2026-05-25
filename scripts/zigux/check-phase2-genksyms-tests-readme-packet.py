#!/usr/bin/env python3
"""Guard the Lane 25 Phase 2 tests-root genksyms reminder packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

GENKSYMS_SURVEY = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")
TESTS_README = Path("zigux/tests/README.md")
TESTS_ALIGNMENT = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")
PHASE2_TOOL_MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

REQUIRED_FILES = (
    GENKSYMS_SURVEY,
    TESTS_README,
    TESTS_ALIGNMENT,
    PHASE2_TOOL_MANIFEST,
)

SURVEY_MARKERS = (
    "- The narrower tests-root undercount is no longer current: live `zigux/tests/README.md` now explicitly names `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, the dedicated `manifest.json`, the returned dash-prefixed-long-option-arguments-as-data expected-output fixture, and the restored process-output fixture packet, while `scripts/zigux/check-phase2-tests-readme-alignment.py` now fail-closes on that fuller reminder packet together with the current shared docs-root and manifest-backed Phase 2 surfaces.",
    "- Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`; the live work is a bounded wrapper-first dual-implementation packet whose checker-owned manifest, process-output fixtures, standalone proofs, and shared reminder surfaces have already returned. The remaining same-family gap is now narrower and checker-local: current `master` still lacks the dedicated `scripts/zigux/check-phase2-genksyms-survey-packet.py` guard that would fail closed on this survey note against the returned closure-side, scripts-root, and tests-root packet.",
)

TESTS_README_MARKERS = (
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
)

ALIGNMENT_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
)

MANIFEST_REQUIRED_STRINGS = (
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "make -C zigux phase2-genksyms",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
)

SAMPLE_SURVEY = """# Phase 2 genksyms dual-implementation survey

- The narrower tests-root undercount is no longer current: live `zigux/tests/README.md` now explicitly names `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, the dedicated `manifest.json`, the returned dash-prefixed-long-option-arguments-as-data expected-output fixture, and the restored process-output fixture packet, while `scripts/zigux/check-phase2-tests-readme-alignment.py` now fail-closes on that fuller reminder packet together with the current shared docs-root and manifest-backed Phase 2 surfaces.
- Relative to the roadmap and ledger, the older inventory-shaped governance gap is no longer truthful on current `master`; the live work is a bounded wrapper-first dual-implementation packet whose checker-owned manifest, process-output fixtures, standalone proofs, and shared reminder surfaces have already returned. The remaining same-family gap is now narrower and checker-local: current `master` still lacks the dedicated `scripts/zigux/check-phase2-genksyms-survey-packet.py` guard that would fail closed on this survey note against the returned closure-side, scripts-root, and tests-root packet.
"""

SAMPLE_TESTS_README = """# zigux/tests

## Phase 2 review packet

current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder

- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`
"""

SAMPLE_ALIGNMENT = """#!/usr/bin/env python3
REQUIRED_TESTS_README_MARKERS = (
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/genksyms.zig`",
    "`make -C zigux phase2-genksyms`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
    "current `master` also directly materializes `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, `make -C zigux phase2-genksyms`, and the `zigux/tests/fixtures/genksyms_bridge/` packet, so keep that returned checker, bridge helper, wrapper, and fixture roster explicit here instead of leaving it outside the tests-root reminder",
)
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 genksyms tests-readme checker missing file: {path}") from exc


def read_manifest(root: Path) -> dict[str, object]:
    path = root / PHASE2_TOOL_MANIFEST
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"phase2 genksyms tests-readme checker missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"phase2 genksyms tests-readme checker invalid json {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"phase2 genksyms tests-readme checker invalid manifest shape: {path}")
    return payload


def require_paths(root: Path) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            raise SystemExit(f"phase2 genksyms tests-readme checker missing required path: {root / rel}")


def require_markers(text: str, markers: tuple[str, ...], label: str) -> None:
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"phase2 genksyms tests-readme checker missing {label} marker: {marker}")


def collect_strings(value: object) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        strings: set[str] = set()
        for item in value:
            strings.update(collect_strings(item))
        return strings
    if isinstance(value, dict):
        strings: set[str] = set()
        for item in value.values():
            strings.update(collect_strings(item))
        return strings
    return set()


def check_root(root: Path) -> None:
    require_paths(root)
    require_markers(read_text(root, GENKSYMS_SURVEY), SURVEY_MARKERS, "survey")
    require_markers(read_text(root, TESTS_README), TESTS_README_MARKERS, "tests README")
    require_markers(read_text(root, TESTS_ALIGNMENT), ALIGNMENT_MARKERS, "tests alignment")
    manifest_strings = collect_strings(read_manifest(root))
    for marker in MANIFEST_REQUIRED_STRINGS:
        if marker not in manifest_strings:
            raise SystemExit(f"phase2 genksyms tests-readme checker missing manifest marker: {marker}")
    if read_manifest(root).get("repo_reality_gaps") != []:
        raise SystemExit("phase2 genksyms tests-readme checker expected empty repo_reality_gaps")


def write_sample_root(root: Path) -> None:
    write_text(root / GENKSYMS_SURVEY, SAMPLE_SURVEY)
    write_text(root / TESTS_README, SAMPLE_TESTS_README)
    write_text(root / TESTS_ALIGNMENT, SAMPLE_ALIGNMENT)
    write_text(
        root / PHASE2_TOOL_MANIFEST,
        json.dumps(
            {
                "phase": "Phase 2",
                "present_surfaces": {
                    "checkers": [
                        "scripts/zigux/check-genksyms-bridge.py",
                        "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
                    ],
                    "bridge_helpers": [
                        "scripts/zigux/genksyms.zig",
                        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
                        "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
                    ],
                    "make_wrappers": ["make -C zigux phase2-genksyms"],
                    "fixture_roster": [
                        "zigux/tests/fixtures/genksyms_bridge/cases.json",
                        "zigux/tests/fixtures/genksyms_bridge/manifest.json",
                        "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
                        "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
                    ],
                },
                "repo_reality_gaps": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane25_genksyms_tests_readme_") as tmp:
        root = Path(tmp)

        write_sample_root(root)
        check_root(root)
        case_count += 1

        (root / TESTS_README).unlink()
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing required path" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected missing required path failure")

        write_sample_root(root)
        write_text(root / GENKSYMS_SURVEY, "# broken\n")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing survey marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected survey marker failure")

        write_sample_root(root)
        write_text(root / TESTS_README, "# broken\n")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing tests README marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected tests README marker failure")

        write_sample_root(root)
        write_text(root / TESTS_ALIGNMENT, "# broken\n")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing tests alignment marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected tests alignment marker failure")

        write_sample_root(root)
        manifest = read_manifest(root)
        manifest["present_surfaces"]["fixture_roster"] = []
        write_text(root / PHASE2_TOOL_MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "missing manifest marker" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected manifest marker failure")

        write_sample_root(root)
        manifest = read_manifest(root)
        manifest["repo_reality_gaps"] = ["gap"]
        write_text(root / PHASE2_TOOL_MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        try:
            check_root(root)
        except SystemExit as exc:
            assert "repo_reality_gaps" in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected repo_reality_gaps failure")

    print("PHASE2_GENKSYMS_TESTS_README_PACKET_SELF_TEST=pass")
    print(f"PHASE2_GENKSYMS_TESTS_README_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 2 tests-root genksyms reminder packet stays aligned."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_GENKSYMS_TESTS_README_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    check_root(args.root.resolve())
    print("PHASE2_GENKSYMS_TESTS_README_PACKET=pass")
    print(f"PHASE2_GENKSYMS_TESTS_README_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE2_GENKSYMS_TESTS_README_PACKET_SURVEY_MARKER_COUNT={len(SURVEY_MARKERS)}")
    print(f"PHASE2_GENKSYMS_TESTS_README_PACKET_TESTS_MARKER_COUNT={len(TESTS_README_MARKERS)}")
    print(f"PHASE2_GENKSYMS_TESTS_README_PACKET_ALIGNMENT_MARKER_COUNT={len(ALIGNMENT_MARKERS)}")
    print(f"PHASE2_GENKSYMS_TESTS_README_PACKET_MANIFEST_MARKER_COUNT={len(MANIFEST_REQUIRED_STRINGS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
