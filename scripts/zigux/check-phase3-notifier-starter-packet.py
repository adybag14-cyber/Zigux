#!/usr/bin/env python3
"""Fail-close the current Phase 3 notifier starter packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


DOC_PATH = Path("Documentation/zigux/phase3-notifier-slice.md")
NOTIFIER_BINDING_PATH = Path("zigux/bindings/notifier_abi.zig")
TEST_PATH = Path("zigux/tests/phase3_notifier_starter_packet.zig")
BUILD_PATH = Path("zigux/tests/phase3_notifier_starter_packet_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase3_notifier_starter_packet_manifest.json")

EXPECTED_MANIFEST_FIELDS = {
    "phase": "Phase 3",
    "lane": "abi-runtime",
    "slug": "phase3-notifier-starter-packet",
    "status": "notifier_binding_starter_present",
    "scope": "notifier priority, list backlink, and hlist prev-link ABI replay",
    "next_safe_step": "keep notifier helper coverage bounded to priority and link-integrity replay before widening into callback ownership or broader runtime chain semantics",
}

REQUIRED_PACKET_FILES = (
    "Documentation/zigux/phase3-notifier-slice.md",
    "zigux/bindings/notifier_abi.zig",
    "zigux/tests/phase3_notifier_starter_packet.zig",
    "zigux/tests/phase3_notifier_starter_packet_build.zig",
    "zigux/tests/phase3_notifier_starter_packet_manifest.json",
    "scripts/zigux/check-phase3-notifier-starter-packet.py",
)

REQUIRED_REPLAY_ROUTES = (
    "python3 scripts/zigux/check-phase3-notifier-starter-packet.py --self-test",
    "python3 scripts/zigux/check-phase3-notifier-starter-packet.py --repo-root .",
    "zig build phase3-notifier-starter-packet-test --build-file zigux/tests/phase3_notifier_starter_packet_build.zig",
)

REQUIRED_REPO_REALITY_GAPS = ()

REQUIRED_MARKERS = {
    DOC_PATH: (
        "# Phase 3 notifier Slice",
        "- `Documentation/zigux/phase3-notifier-slice.md`",
        "- `zigux/bindings/notifier_abi.zig`",
        "- `zigux/tests/phase3_notifier_starter_packet.zig`",
        "This packet stays intentionally small:",
        "The landed packet only closes the bounded notifier ABI replay slice.",
    ),
    NOTIFIER_BINDING_PATH: (
        "pub const NotifierResult = enum(u32) {",
        "pub const NotifierBlock = extern struct {",
        "pub fn chainHasNonincreasingPriority(head: ?*const NotifierBlock) bool {",
        "pub fn firstChainPriorityIncrease(head: ?*const NotifierBlock) ?NotifierChainPriorityIncrease {",
        "pub fn firstBrokenBacklink(head: ?*const ListHead) ?ListBackLinkBreak {",
        "pub fn firstBrokenPrevLink(head: ?*const HListHead) ?HListPrevLinkBreak {",
        'test "notifier priority helper rejects increasing priority" {',
        'test "hlist helper rejects a broken prev-link" {',
    ),
    TEST_PATH: (
        'test "notifier starter packet keeps result bytes explicit" {',
        'test "notifier starter packet keeps layout anchors explicit" {',
        'test "notifier starter packet keeps nonincreasing priority chains accepted" {',
        'test "notifier starter packet reports the first priority increase" {',
        'test "notifier starter packet keeps list backlink drift explicit" {',
        'test "notifier starter packet keeps hlist prev-link drift explicit" {',
    ),
    BUILD_PATH: (
        '.root_source_file = b.path("../bindings/notifier_abi.zig"),',
        '.root_source_file = b.path("phase3_notifier_starter_packet.zig"),',
        'root_module.addImport("notifier_abi", notifier_abi);',
        '"phase3-notifier-starter-packet-test"',
    ),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _append_duplicate_list_entry_issues(
    manifest_name: str,
    field_name: str,
    values: list[object],
    issues: list[str],
) -> None:
    seen: dict[str, int] = {}
    for index, value in enumerate(values):
        key = repr(value)
        first_index = seen.get(key)
        if first_index is None:
            seen[key] = index
            continue
        issues.append(
            f"{manifest_name} duplicate {field_name} entry: "
            f"{value!r} (first index {first_index}, duplicate index {index})"
        )


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / relative_path
        try:
            text = _read(path)
        except FileNotFoundError:
            issues.append(f"missing repo file: {relative_path.as_posix()}")
            continue
        for marker in markers:
            if marker not in text:
                issues.append(f"missing {relative_path.as_posix()} marker: {marker}")

    manifest_path = repo_root / MANIFEST_PATH
    if manifest_path.exists():
        try:
            manifest = json.loads(_read(manifest_path))
        except json.JSONDecodeError as exc:
            issues.append(f"invalid JSON in {MANIFEST_PATH.as_posix()}: {exc}")
        else:
            for field, expected in EXPECTED_MANIFEST_FIELDS.items():
                actual = manifest.get(field)
                if actual != expected:
                    issues.append(
                        "phase3_notifier_starter_packet_manifest.json wrong "
                        f"{field}: {actual!r} != {expected!r}"
                    )

            packet_files = manifest.get("packet_files")
            replay_routes = manifest.get("replay_routes")
            repo_reality_gaps = manifest.get("repo_reality_gaps")
            if not isinstance(packet_files, list):
                issues.append("phase3_notifier_starter_packet_manifest.json packet_files is not a list")
            if not isinstance(replay_routes, list):
                issues.append("phase3_notifier_starter_packet_manifest.json replay_routes is not a list")
            if not isinstance(repo_reality_gaps, list):
                issues.append(
                    "phase3_notifier_starter_packet_manifest.json repo_reality_gaps is not a list"
                )
            if isinstance(packet_files, list):
                _append_duplicate_list_entry_issues(
                    "phase3_notifier_starter_packet_manifest.json",
                    "packet_files",
                    packet_files,
                    issues,
                )
                for required_path in REQUIRED_PACKET_FILES:
                    if required_path not in packet_files:
                        issues.append(
                            "phase3_notifier_starter_packet_manifest.json missing packet_files entry: "
                            f"{required_path}"
                        )
            if isinstance(replay_routes, list):
                _append_duplicate_list_entry_issues(
                    "phase3_notifier_starter_packet_manifest.json",
                    "replay_routes",
                    replay_routes,
                    issues,
                )
                for route in REQUIRED_REPLAY_ROUTES:
                    if route not in replay_routes:
                        issues.append(
                            "phase3_notifier_starter_packet_manifest.json missing replay route: "
                            f"{route}"
                        )
            if isinstance(repo_reality_gaps, list):
                _append_duplicate_list_entry_issues(
                    "phase3_notifier_starter_packet_manifest.json",
                    "repo_reality_gaps",
                    repo_reality_gaps,
                    issues,
                )
                for gap in repo_reality_gaps:
                    if (repo_root / gap).exists():
                        issues.append(
                            "phase3_notifier_starter_packet_manifest.json repo_reality_gaps entry is present on disk: "
                            f"{gap}"
                        )
                for gap in REQUIRED_REPO_REALITY_GAPS:
                    if gap not in repo_reality_gaps:
                        issues.append(
                            "phase3_notifier_starter_packet_manifest.json missing repo_reality_gaps entry: "
                            f"{gap}"
                        )
    return issues


def _populate_repo(root: Path) -> None:
    samples = {
        DOC_PATH: "\n".join(REQUIRED_MARKERS[DOC_PATH]) + "\n",
        NOTIFIER_BINDING_PATH: "\n".join(REQUIRED_MARKERS[NOTIFIER_BINDING_PATH]) + "\n",
        TEST_PATH: "\n".join(REQUIRED_MARKERS[TEST_PATH]) + "\n",
        BUILD_PATH: "\n".join(REQUIRED_MARKERS[BUILD_PATH]) + "\n",
        MANIFEST_PATH: json.dumps(
            {
                **EXPECTED_MANIFEST_FIELDS,
                "packet_files": list(REQUIRED_PACKET_FILES),
                "replay_routes": list(REQUIRED_REPLAY_ROUTES),
                "repo_reality_gaps": list(REQUIRED_REPO_REALITY_GAPS),
            },
            indent=2,
        )
        + "\n",
    }
    for relative_path, text in samples.items():
        _write(root / relative_path, text)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_notifier_starter_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_NOTIFIER_STARTER_PACKET_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        removal_cases = (
            (DOC_PATH, "# Phase 3 notifier Slice"),
            (NOTIFIER_BINDING_PATH, "pub const NotifierResult = enum(u32) {"),
            (TEST_PATH, 'test "notifier starter packet reports the first priority increase" {'),
            (BUILD_PATH, '"phase3-notifier-starter-packet-test"'),
        )
        for relative_path, marker in removal_cases:
            _populate_repo(root)
            path = root / relative_path
            path.write_text(_read(path).replace(marker, "", 1), encoding="utf-8")
            issues = validate_repo(root)
            expected = f"missing {relative_path.as_posix()} marker: {marker}"
            if expected not in issues:
                print("PHASE3_NOTIFIER_STARTER_PACKET_SELF_TEST=fail")
                print(f"expected missing marker was not reported: {expected}")
                return 1

        _populate_repo(root)
        manifest_path = root / MANIFEST_PATH
        manifest = json.loads(_read(manifest_path))
        manifest["replay_routes"].append(REQUIRED_REPLAY_ROUTES[0])
        _write(manifest_path, json.dumps(manifest, indent=2) + "\n")
        issues = validate_repo(root)
        expected_duplicate = (
            "phase3_notifier_starter_packet_manifest.json duplicate replay_routes entry: "
            "'python3 scripts/zigux/check-phase3-notifier-starter-packet.py --self-test' "
        )
        if not any(issue.startswith(expected_duplicate) for issue in issues):
            print("PHASE3_NOTIFIER_STARTER_PACKET_SELF_TEST=fail")
            print(f"expected duplicate replay-route guard was not reported: {expected_duplicate}")
            return 1

    print("PHASE3_NOTIFIER_STARTER_PACKET_SELF_TEST=pass")
    print("PHASE3_NOTIFIER_STARTER_PACKET_SELF_TEST_CASES=5")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 notifier starter packet."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 3 notifier starter packet",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_NOTIFIER_STARTER_PACKET=fail")
        for issue in issues:
            print(issue)
        return 1

    print(f"validated {args.repo_root / DOC_PATH}")
    print(f"validated {args.repo_root / TEST_PATH}")
    print(f"validated {args.repo_root / BUILD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
