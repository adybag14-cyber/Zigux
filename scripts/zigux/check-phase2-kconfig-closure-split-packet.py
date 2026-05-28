#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
CONF_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json")
KCONFIG_CASES_REL = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def format_backticked_list(values: list[str]) -> str:
    if not values:
        raise SystemExit("expected non-empty packet when building closure marker")
    if len(values) == 1:
        return f"`{values[0]}`"
    if len(values) == 2:
        return f"`{values[0]}` and `{values[1]}`"
    return ", ".join(f"`{value}`" for value in values[:-1]) + f", and `{values[-1]}`"


def expected_packets(root: Path) -> tuple[list[str], list[str], list[str]]:
    manifest = read_json(root / CONF_MANIFEST_REL)
    cases_payload = read_json(root / KCONFIG_CASES_REL)

    if not isinstance(manifest, dict):
        raise SystemExit(f"invalid manifest shape: {root / CONF_MANIFEST_REL}")
    if not isinstance(cases_payload, dict):
        raise SystemExit(f"invalid cases shape: {root / KCONFIG_CASES_REL}")

    allconfig_sentinel_packet = manifest.get("allconfig_sentinel_packet")
    explicit_override_modes = manifest.get("helper_local_allconfig_explicit_override_modes")
    conf_cases = cases_payload.get("conf_cases")

    if not isinstance(allconfig_sentinel_packet, list) or not all(
        isinstance(item, str) for item in allconfig_sentinel_packet
    ):
        raise SystemExit(f"invalid allconfig_sentinel_packet in {root / CONF_MANIFEST_REL}")
    if not isinstance(explicit_override_modes, list) or not all(
        isinstance(item, str) for item in explicit_override_modes
    ):
        raise SystemExit(
            f"invalid helper_local_allconfig_explicit_override_modes in {root / CONF_MANIFEST_REL}"
        )
    if not isinstance(conf_cases, list) or not all(isinstance(item, dict) for item in conf_cases):
        raise SystemExit(f"invalid conf_cases in {root / KCONFIG_CASES_REL}")

    override_modes: list[str] = []
    sentinel_modes: list[str] = []
    sentinel_expected = set(allconfig_sentinel_packet)
    for case in conf_cases:
        mode = case.get("mode")
        expected = case.get("expected")
        if not isinstance(mode, str) or not isinstance(expected, str):
            raise SystemExit(f"invalid conf case entry in {root / KCONFIG_CASES_REL}")
        if "allconfig" in case:
            override_modes.append(mode)
        if expected in sentinel_expected:
            sentinel_modes.append(mode)

    if sorted(set(override_modes)) != sorted(override_modes):
        override_modes = sorted(set(override_modes))
    if sorted(set(sentinel_modes)) != sorted(sentinel_modes):
        sentinel_modes = sorted(set(sentinel_modes))

    explicit_override_modes = sorted(dict.fromkeys(explicit_override_modes))
    return override_modes, sentinel_modes, explicit_override_modes


def collect_issues(root: Path) -> list[tuple[str, str]]:
    closure_text = read_text(root / PHASE2_CLOSURE_REL)
    override_modes, sentinel_modes, explicit_override_modes = expected_packets(root)
    issues: list[tuple[str, str]] = []

    required_markers = (
        "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
        "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
        f"request-plan `allconfig` overrides stay limited to {format_backticked_list(override_modes)}",
        f"`allconfig_sentinel_packet` still covers {format_backticked_list(sentinel_modes)}",
        "helper-local explicit-override roster remains broader by design",
    )
    for marker in required_markers:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    helper_local_line = (
        "the helper-local explicit-override roster remains broader by design"
    )
    if closure_text.count(helper_local_line) != 1:
        issues.append(("EXACT_CLOSURE_LINE_COUNT", f"{closure_text.count(helper_local_line)}::{helper_local_line}"))

    if not set(override_modes).issubset(explicit_override_modes):
        issues.append(
            (
                "OVERRIDE_PACKET_NOT_SUBSET_OF_HELPER_LOCAL_PACKET",
                f"override={override_modes!r}:helper_local={explicit_override_modes!r}",
            )
        )
    if set(override_modes) == set(explicit_override_modes):
        issues.append(
            (
                "HELPER_LOCAL_PACKET_NOT_BROADER",
                f"override={override_modes!r}:helper_local={explicit_override_modes!r}",
            )
        )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    write_text(
        root / PHASE2_CLOSURE_REL,
        """# Phase 2 Closure

## Repo-Reality Gaps

- `PHASE2_CURRENT_GAP_PACKET=Documentation/zigux/phase2-kconfig-bridge-gap-survey.md`
- current authenticated repo reads do not expose `scripts/kconfig/conf.c` or `scripts/kconfig/confdata.c` on `master`, so the shipped kconfig bridge packet remains fixture-backed rather than same-tree differential
- the next same-family truthfulness pass should keep reminder surfaces aligned with the live split recorded in `zigux/tests/fixtures/kconfig_bridge/cases.json` and `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`: request-plan `allconfig` overrides stay limited to `allmodconfig`, `alldefconfig`, and `randconfig`, `allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`, and the helper-local explicit-override roster remains broader by design
""",
    )
    write_text(
        root / CONF_MANIFEST_REL,
        json.dumps(
            {
                "allconfig_sentinel_packet": [
                    "allnoconfig_expected.json",
                    "allyesconfig_expected.json",
                ],
                "helper_local_allconfig_explicit_override_modes": [
                    "allmodconfig",
                    "allnoconfig",
                    "allyesconfig",
                    "alldefconfig",
                    "randconfig",
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / KCONFIG_CASES_REL,
        json.dumps(
            {
                "conf_cases": [
                    {"mode": "allnoconfig", "expected": "allnoconfig_expected.json"},
                    {"mode": "allyesconfig", "expected": "allyesconfig_expected.json"},
                    {"mode": "allmodconfig", "expected": "allmodconfig_expected.json", "allconfig": ""},
                    {"mode": "alldefconfig", "expected": "alldefconfig_expected.json", "allconfig": "mini-all.config"},
                    {"mode": "randconfig", "expected": "randconfig_expected.json", "allconfig": ""},
                ]
            },
            indent=2,
        )
        + "\n",
    )


def write_sample_root(root: Path) -> int:
    build_sample_root(root)
    print(f"PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET_SAMPLE_ROOT={root}")
    return 0


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_kconfig_closure_split_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "`allconfig_sentinel_packet` still covers `allnoconfig` and `allyesconfig`",
                "`allconfig_sentinel_packet` still covers `allyesconfig` only",
                1,
            ),
            encoding="utf-8",
        )
        assert any(code == "MISSING_CLOSURE_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        manifest_path = root / CONF_MANIFEST_REL
        manifest = read_json(manifest_path)
        assert isinstance(manifest, dict)
        manifest["helper_local_allconfig_explicit_override_modes"] = [
            "allmodconfig",
            "alldefconfig",
            "randconfig",
        ]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        assert any(code == "HELPER_LOCAL_PACKET_NOT_BROADER" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        cases_path = root / KCONFIG_CASES_REL
        cases = read_json(cases_path)
        assert isinstance(cases, dict)
        conf_cases = cases["conf_cases"]
        assert isinstance(conf_cases, list)
        conf_cases.append({"mode": "allyesconfig", "expected": "allyesconfig_expected.json", "allconfig": ""})
        write_text(cases_path, json.dumps(cases, indent=2) + "\n")
        assert any(code == "MISSING_CLOSURE_MARKER" for code, _ in collect_issues(root))
        checks_run += 1

        build_sample_root(root)
        closure_path = root / PHASE2_CLOSURE_REL
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "the helper-local explicit-override roster remains broader by design",
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert (
            "EXACT_CLOSURE_LINE_COUNT",
            "0::the helper-local explicit-override roster remains broader by design",
        ) in collect_issues(root)
        checks_run += 1

    print("PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET_SELF_TEST=pass")
    print(f"PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 closure note's shared kconfig split aligned with live fixtures."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in checker self-test")
    parser.add_argument("--write-sample-root", type=Path, help="Write a minimal passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root.resolve())

    override_modes, sentinel_modes, explicit_override_modes = expected_packets(args.root.resolve())
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET=pass")
    print(f"PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET_OVERRIDE_MODE_COUNT={len(override_modes)}")
    print(f"PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET_SENTINEL_MODE_COUNT={len(sentinel_modes)}")
    print(
        "PHASE2_KCONFIG_CLOSURE_SPLIT_PACKET_HELPER_LOCAL_EXPLICIT_MODE_COUNT="
        f"{len(explicit_override_modes)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
