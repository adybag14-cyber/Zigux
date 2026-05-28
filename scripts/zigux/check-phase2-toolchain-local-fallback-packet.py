#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
MAKEFILE = Path("zigux/Makefile")
NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
TESTS_README = Path("zigux/tests/README.md")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_ARCHIVE_TARGET = "x86_64-linux"
EXPECTED_REQUIRED_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]

MAKEFILE_FALLBACK_LINES = [
    'ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c \'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["channel"])\' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)',
    'ZIG_PINNED_TARGET := $(shell $(PYTHON) -c \'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["upgrade_policy"]["archive_target_scope"][0])\' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)',
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
]

TOOLCHAIN_ROUTE_LINES = [
    "phase2-toolchain:",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/install-zig.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
]

SURFACE_MARKERS = {
    NOTES: [
        "repo-local `.zig-toolchain` fallback",
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/install-zig.py",
        "scripts/zigux/stage-pinned-zig-archive.py",
        "make -C zigux phase2-toolchain",
        "phase2-genksyms",
        "phase2-fixdep",
    ],
    TESTS_README: [
        "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
        "scripts/zigux/check-zig-toolchain.py",
        "scripts/zigux/install-zig.py",
        "make -C zigux phase2-toolchain",
    ],
    WORKFLOW: [
        "ZIGUX_ZIG_TARGET",
        "ZIGUX_ZIG_FILENAME",
        "community-mirrors.txt",
        'python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
        "make -C zigux phase2-toolchain",
    ],
}


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f"duplicate_key:{key}")
        payload[key] = value
    return payload


def read_text(root: Path, relative: Path) -> str:
    path = root / relative
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"{relative}:missing")


def load_policy(root: Path) -> dict[str, object]:
    try:
        payload = json.loads(
            read_text(root, POLICY), object_pairs_hook=reject_duplicate_json_keys
        )
    except ValueError as exc:
        raise SystemExit(f"{POLICY}:{exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{POLICY}:expected_object")
    return payload


def as_str_list(value: object, *, label: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SystemExit(f"{label}:expected_string_list")
    return value


def require_equal(actual: object, expected: object, *, label: str, issues: list[str]) -> None:
    if actual != expected:
        issues.append(f"{label}:expected {expected!r}, got {actual!r}")


def require_markers(text: str, markers: list[str], *, label: str, issues: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            issues.append(f"{label}:missing marker {marker!r}")


def require_exact_once(text: str, markers: list[str], *, label: str, issues: list[str]) -> None:
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            issues.append(f"{label}:expected one {marker!r}, found {count}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    policy = load_policy(root)
    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"{POLICY}:upgrade_policy:expected_object")

    require_equal(policy.get("channel"), EXPECTED_CHANNEL, label="policy.channel", issues=issues)
    require_equal(
        policy.get("minimum_version"),
        EXPECTED_CHANNEL,
        label="policy.minimum_version",
        issues=issues,
    )
    require_equal(
        as_str_list(upgrade_policy.get("archive_target_scope"), label="policy.archive_target_scope"),
        [EXPECTED_ARCHIVE_TARGET],
        label="policy.archive_target_scope",
        issues=issues,
    )
    require_equal(
        as_str_list(upgrade_policy.get("required_make_routes"), label="policy.required_make_routes"),
        EXPECTED_REQUIRED_ROUTES,
        label="policy.required_make_routes",
        issues=issues,
    )

    makefile = read_text(root, MAKEFILE)
    require_exact_once(makefile, MAKEFILE_FALLBACK_LINES, label=str(MAKEFILE), issues=issues)
    require_markers(makefile, TOOLCHAIN_ROUTE_LINES, label=str(MAKEFILE), issues=issues)

    for relative, markers in SURFACE_MARKERS.items():
        require_markers(read_text(root, relative), markers, label=str(relative), issues=issues)

    return issues


def write_sample_root(root: Path) -> None:
    for relative in [POLICY, MAKEFILE, NOTES, TESTS_README, WORKFLOW]:
        (root / relative).parent.mkdir(parents=True, exist_ok=True)

    (root / POLICY).write_text(
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {EXPECTED_ARCHIVE_TARGET: "0" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [EXPECTED_ARCHIVE_TARGET],
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / MAKEFILE).write_text(
        "\n".join(MAKEFILE_FALLBACK_LINES + ["", *TOOLCHAIN_ROUTE_LINES, ""]),
        encoding="utf-8",
    )
    (root / NOTES).write_text("\n".join(SURFACE_MARKERS[NOTES]) + "\n", encoding="utf-8")
    (root / TESTS_README).write_text(
        "\n".join(SURFACE_MARKERS[TESTS_README]) + "\n", encoding="utf-8"
    )
    (root / WORKFLOW).write_text(
        "\n".join(SURFACE_MARKERS[WORKFLOW]) + "\n", encoding="utf-8"
    )


def run_self_test() -> None:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux-toolchain-local-fallback-") as tmp:
        root = Path(tmp)
        write_sample_root(root)
        issues = validate(root)
        if issues:
            raise SystemExit("selftest:baseline_failed:" + "; ".join(issues))
        cases += 1

        policy_path = root / POLICY
        original_policy = policy_path.read_text(encoding="utf-8")
        policy = json.loads(original_policy)
        policy["upgrade_policy"]["required_make_routes"] = EXPECTED_REQUIRED_ROUTES[:-1]
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        if not any("policy.required_make_routes" in issue for issue in validate(root)):
            raise SystemExit("selftest:missing_policy_route_failure")
        policy_path.write_text(original_policy, encoding="utf-8")
        cases += 1

        makefile_path = root / MAKEFILE
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(MAKEFILE_FALLBACK_LINES[-1], ""), encoding="utf-8"
        )
        if not any("ZIG ?=" in issue for issue in validate(root)):
            raise SystemExit("selftest:missing_makefile_fallback_failure")
        makefile_path.write_text(original_makefile, encoding="utf-8")
        cases += 1

        notes_path = root / NOTES
        original_notes = notes_path.read_text(encoding="utf-8")
        notes_path.write_text(
            original_notes.replace("repo-local `.zig-toolchain` fallback", ""),
            encoding="utf-8",
        )
        if not any("repo-local `.zig-toolchain` fallback" in issue for issue in validate(root)):
            raise SystemExit("selftest:missing_notes_marker_failure")
        cases += 1

    print("PHASE2_TOOLCHAIN_LOCAL_FALLBACK_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FALLBACK_PACKET_SELF_TEST_CASE_COUNT={cases}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0
    if args.write_sample_root:
        write_sample_root(args.write_sample_root)
        return 0

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(f"PHASE2_TOOLCHAIN_LOCAL_FALLBACK_PACKET_ERROR={issue}")
        return 1
    print("PHASE2_TOOLCHAIN_LOCAL_FALLBACK_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FALLBACK_PACKET_REQUIRED_ROUTE_COUNT={len(EXPECTED_REQUIRED_ROUTES)}")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FALLBACK_PACKET_MAKEFILE_FALLBACK_LINE_COUNT={len(MAKEFILE_FALLBACK_LINES)}")
    print(f"PHASE2_TOOLCHAIN_LOCAL_FALLBACK_PACKET_SURFACE_COUNT={len(SURFACE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
