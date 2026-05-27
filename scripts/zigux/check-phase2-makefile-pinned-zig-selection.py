#!/usr/bin/env python3
"""Guard the Phase 2 Makefile pinned Zig selection contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()

MAKEFILE = Path("zigux/Makefile")
POLICY = Path("scripts/zigux/zig-toolchain-policy.json")
TOOLCHAIN_CHECK = Path("scripts/zigux/check-zig-toolchain.py")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")

EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGET = "x86_64-linux"
EXPECTED_ROUTES = (
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
)
EXPECTED_SELF_TEST_CASE_COUNT = 11

MAKEFILE_LINES = (
    "PHASE2_TOOLCHAIN_POLICY := ../scripts/zigux/zig-toolchain-policy.json",
    "ZIG_PINNED_CHANNEL := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"channel\"])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_TARGET := $(shell $(PYTHON) -c 'import json,sys; from pathlib import Path; print(json.loads(Path(sys.argv[1]).read_text(encoding=\"utf-8\"))[\"upgrade_policy\"][\"archive_target_scope\"][0])' $(PHASE2_TOOLCHAIN_POLICY) 2>/dev/null)",
    "ZIG_PINNED_EXTRACT_ROOT := $(ZIGUX_ROOT)/.zig-toolchain/zig-$(ZIG_PINNED_TARGET)-$(ZIG_PINNED_CHANNEL)",
    "ZIG_PINNED_EXECUTABLE := $(firstword $(wildcard $(ZIG_PINNED_EXTRACT_ROOT)/zig $(ZIG_PINNED_EXTRACT_ROOT)/bin/zig))",
    "ZIG_LOCAL_TOOLCHAIN := $(firstword $(wildcard $(ZIGUX_ROOT)/.zig-toolchain/*/zig $(ZIGUX_ROOT)/.zig-toolchain/*/bin/zig))",
    "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
)

TOOLCHAIN_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    'def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:',
    'add_search_root(root / ".zig-toolchain")',
    'add_search_root(root / "toolchains")',
    'add_search_root(root / ".toolchains")',
    'pinned_dirname = f"zig-x86_64-linux-{pinned_channel}"',
    'add_candidate_roots(base / pinned_dirname)',
)

NOTE_MARKERS = (
    "`scripts/zigux/check-zig-toolchain.py` is directly readable on current `master` and keeps the pinned-channel probe, repo-local `.zig-toolchain` fallback, and archive-integrity validation surface explicit beside the reminder guards.",
    "`scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`",
    "`make -C zigux phase2-toolchain`",
)


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def count_exact_lines(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def remove_exact_line(text: str, needle: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == needle:
            del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"line not found: {needle}")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (MAKEFILE, POLICY, TOOLCHAIN_CHECK, BOOTSTRAP_NOTES):
        if not resolve(root, rel).is_file():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    makefile_text = read_text(resolve(root, MAKEFILE))
    policy = json.loads(read_text(resolve(root, POLICY)))
    toolchain_text = read_text(resolve(root, TOOLCHAIN_CHECK))
    notes_text = read_text(resolve(root, BOOTSTRAP_NOTES))

    for marker in MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count != 1:
            failures.append(f"makefile_line_count:{count}:{marker}")

    if policy.get("channel") != EXPECTED_CHANNEL:
        failures.append(f"policy_channel:{policy.get('channel')!r}")
    if policy.get("minimum_version") != EXPECTED_CHANNEL:
        failures.append(f"policy_minimum_version:{policy.get('minimum_version')!r}")

    upgrade_policy = policy.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        failures.append("policy_upgrade_policy:missing_or_invalid")
    else:
        if upgrade_policy.get("channel_minimum_lockstep") is not True:
            failures.append("policy_lockstep:not_true")
        if upgrade_policy.get("archive_target_scope") != [EXPECTED_TARGET]:
            failures.append(f"policy_archive_target_scope:{upgrade_policy.get('archive_target_scope')!r}")
        if upgrade_policy.get("required_make_routes") != list(EXPECTED_ROUTES):
            failures.append(f"policy_required_make_routes:{upgrade_policy.get('required_make_routes')!r}")

    for marker in TOOLCHAIN_MARKERS:
        count = toolchain_text.count(marker)
        if count != 1:
            failures.append(f"toolchain_marker_count:{count}:{marker}")

    for marker in NOTE_MARKERS:
        if marker not in notes_text:
            failures.append(f"missing_note_marker:{marker}")

    return failures


def build_sample_root(root: Path) -> None:
    write_text(
        resolve(root, MAKEFILE),
        "\n".join(
            (
                "PYTHON ?= python3",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "ZIGUX_ROOT := ..",
                *MAKEFILE_LINES,
                "",
                ".PHONY: phase2-toolchain",
                "phase2-toolchain:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --self-test",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, POLICY),
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {
                    EXPECTED_TARGET: "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [EXPECTED_TARGET],
                    "required_make_routes": list(EXPECTED_ROUTES),
                },
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        resolve(root, TOOLCHAIN_CHECK),
        "\n".join(
            (
                "from pathlib import Path",
                'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
                "",
                'def load_pinned_channel(policy_path: Path = TOOLCHAIN_POLICY) -> str | None:',
                "    return None",
                "",
                "def iter_zig_search_roots(root: Path):",
                '    add_search_root(root / ".zig-toolchain")',
                '    add_search_root(root / "toolchains")',
                '    add_search_root(root / ".toolchains")',
                '    pinned_dirname = f"zig-x86_64-linux-{pinned_channel}"',
                "    add_candidate_roots(base / pinned_dirname)",
            )
        )
        + "\n",
    )
    write_text(
        resolve(root, BOOTSTRAP_NOTES),
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "## Current direct packet",
                "",
                f"- {NOTE_MARKERS[0]}",
                f"- {NOTE_MARKERS[1]} and keeps `{EXPECTED_TARGET}` in the archive scope.",
                f"- The rematerialized make-wrapper packet is directly readable on current `master` through {NOTE_MARKERS[2]}, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_makefile_pinned_zig_selection_") as tmpdir:
        root = Path(tmpdir)

        build_sample_root(root)
        assert collect_failures(root) == []
        checks += 1

        build_sample_root(root)
        resolve(root, MAKEFILE).write_text(
            remove_exact_line(read_text(resolve(root, MAKEFILE)), MAKEFILE_LINES[0]),
            encoding="utf-8",
        )
        assert any(MAKEFILE_LINES[0] in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        makefile_path = resolve(root, MAKEFILE)
        makefile_path.write_text(
            read_text(makefile_path) + MAKEFILE_LINES[-1] + "\n",
            encoding="utf-8",
        )
        assert any(MAKEFILE_LINES[-1] in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        policy_path = resolve(root, POLICY)
        policy = json.loads(read_text(policy_path))
        policy["channel"] = "0.17.0-dev.88+drift"
        write_text(policy_path, json.dumps(policy, indent=2) + "\n")
        assert any(failure.startswith("policy_channel:") for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(resolve(root, POLICY)))
        policy["upgrade_policy"]["archive_target_scope"] = ["aarch64-linux"]
        write_text(resolve(root, POLICY), json.dumps(policy, indent=2) + "\n")
        assert any("policy_archive_target_scope:" in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        policy = json.loads(read_text(resolve(root, POLICY)))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain", "phase2-tools"]
        write_text(resolve(root, POLICY), json.dumps(policy, indent=2) + "\n")
        assert any("policy_required_make_routes:" in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        toolchain_path = resolve(root, TOOLCHAIN_CHECK)
        toolchain_path.write_text(
            read_text(toolchain_path).replace('add_search_root(root / ".zig-toolchain")', "", 1),
            encoding="utf-8",
        )
        assert any('add_search_root(root / ".zig-toolchain")' in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        notes_path = resolve(root, BOOTSTRAP_NOTES)
        notes_path.write_text(
            read_text(notes_path).replace(NOTE_MARKERS[0], "", 1),
            encoding="utf-8",
        )
        assert any(failure.startswith("missing_note_marker:") for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        resolve(root, POLICY).unlink()
        assert f"missing_file:{POLICY.as_posix()}" in collect_failures(root)
        checks += 1

        build_sample_root(root)
        makefile_path.write_text(
            read_text(makefile_path).replace(
                "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_PINNED_EXECUTABLE),$(ZIG_PINNED_EXECUTABLE),$(ZIG_LOCAL_TOOLCHAIN))",
                "ZIG_PINNED_TOOLCHAIN := $(if $(ZIG_LOCAL_TOOLCHAIN),$(ZIG_LOCAL_TOOLCHAIN),$(ZIG_PINNED_EXECUTABLE))",
                1,
            ),
            encoding="utf-8",
        )
        assert any("ZIG_PINNED_TOOLCHAIN :=" in failure for failure in collect_failures(root))
        checks += 1

        build_sample_root(root)
        notes_path.write_text(
            read_text(notes_path).replace("`make -C zigux phase2-toolchain`", "`make -C zigux phase2-toolchain-drift`", 1),
            encoding="utf-8",
        )
        assert any("make -C zigux phase2-toolchain" in failure for failure in collect_failures(root))
        checks += 1

    assert checks == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_MAKEFILE_PINNED_ZIG_SELECTION_SELF_TEST=pass")
    print(f"PHASE2_MAKEFILE_PINNED_ZIG_SELECTION_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE2_MAKEFILE_PINNED_ZIG_SELECTION=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE2_MAKEFILE_PINNED_ZIG_SELECTION=pass")
    print(f"PHASE2_MAKEFILE_PINNED_ZIG_SELECTION_MAKEFILE_LINE_COUNT={len(MAKEFILE_LINES)}")
    print(f"PHASE2_MAKEFILE_PINNED_ZIG_SELECTION_TOOLCHAIN_MARKER_COUNT={len(TOOLCHAIN_MARKERS)}")
    print(f"PHASE2_MAKEFILE_PINNED_ZIG_SELECTION_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
