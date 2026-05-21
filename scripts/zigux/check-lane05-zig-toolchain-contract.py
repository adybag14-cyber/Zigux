#!/usr/bin/env python3
"""Fail-closed guard for the Lane 05 Zig toolchain contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
SCRIPT_REL = Path("scripts/zigux/check-zig-toolchain.py")
POLICY_REL = Path("scripts/zigux/zig-toolchain-policy.json")

EXPECTED_TARGET = "x86_64-linux"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_REQUIRED_MAKE_ROUTES = [
    "phase2-toolchain",
    "phase2-validate",
    "phase2-cross",
]

SCRIPT_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    'add_search_root(root / ".zig-toolchain")',
    'add_search_root(root / "toolchains")',
    'add_search_root(root / ".toolchains")',
    'add_search_root(root / "third_party")',
    'add_search_root(root / "agent_files")',
    'add_search_root(parent / ".toolchains")',
    'add_search_root(parent / "toolchains")',
    'add_search_root(parent / "agent_files")',
    'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
    'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
    'parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")',
    'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
    "archive_targets = payload[\"upgrade_policy\"][\"archive_target_scope\"]",
    'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
    'print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload[\'channel\']}")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_TARGETS=" + ",".join(str(target) for target in upgrade_policy["archive_target_scope"]))',
    'print("ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=" + ",".join(str(route) for route in upgrade_policy["required_make_routes"]))',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or \'unresolved\'}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")',
)

WORKFLOW_MARKERS = (
    '- name: Setup pinned Zig toolchain',
    'targets = policy["upgrade_policy"]["archive_target_scope"]',
    'channel = policy["channel"]',
    'print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
    'print(f"ZIGUX_ZIG_CHANNEL=\'{channel}\'")',
    'print(f"ZIGUX_ZIG_FILENAME=\'{filename}\'")',
    'print(f"ZIGUX_ZIG_URL=\'{url}\'")',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    '- name: Check current Zig toolchain policy packet',
    'run: python3 scripts/zigux/check-zig-toolchain.py --policy-only',
    '- name: Check current pinned Zig archive packet',
    'run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
    '- name: Self-test current Zig installer helper',
    'run: python3 scripts/zigux/install-zig.py --self-test',
)


def load_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"expected {expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"expected {label} `{earlier}` before `{later}`")


def validate_policy(root: Path) -> tuple[str, str]:
    payload = json.loads(load_text(root, POLICY_REL))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {POLICY_REL}: expected object")

    if payload.get("channel") != EXPECTED_CHANNEL:
        raise ValueError(f"unexpected channel in {POLICY_REL}: {payload.get('channel')!r}")
    if payload.get("minimum_version") != EXPECTED_CHANNEL:
        raise ValueError(
            f"unexpected minimum_version in {POLICY_REL}: {payload.get('minimum_version')!r}"
        )

    archive_sha256 = payload.get("archive_sha256")
    if archive_sha256 != {
        EXPECTED_TARGET: "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
    }:
        raise ValueError(f"unexpected archive_sha256 contract in {POLICY_REL}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {POLICY_REL}")

    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        raise ValueError(f"expected channel_minimum_lockstep=true in {POLICY_REL}")
    if upgrade_policy.get("archive_target_scope") != [EXPECTED_TARGET]:
        raise ValueError(f"unexpected archive_target_scope in {POLICY_REL}")
    if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_MAKE_ROUTES:
        raise ValueError(f"unexpected required_make_routes in {POLICY_REL}")

    return EXPECTED_TARGET, EXPECTED_CHANNEL


def validate_script(root: Path) -> int:
    text = load_text(root, SCRIPT_REL)

    for marker in SCRIPT_MARKERS:
        require_marker(text, marker, "script marker")

    require_exact_count(text, 'add_search_root(root / ".zig-toolchain")', 1, "search-root marker")
    require_exact_count(text, 'add_search_root(root / "third_party")', 1, "search-root marker")
    require_exact_count(text, 'add_search_root(root / "agent_files")', 1, "search-root marker")
    require_exact_count(
        text,
        'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
        1,
        "policy-only cli marker",
    )
    require_exact_count(
        text,
        'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
        1,
        "archive-only cli marker",
    )
    require_order(
        text,
        'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
        'print("ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=" + ",".join(str(route) for route in upgrade_policy["required_make_routes"]))',
        "policy summary order",
    )

    return len(SCRIPT_MARKERS)


def validate_workflow(root: Path) -> int:
    text = load_text(root, WORKFLOW_REL)

    for marker in WORKFLOW_MARKERS:
        require_marker(text, marker, "workflow marker")

    require_exact_count(
        text,
        'run: python3 scripts/zigux/check-zig-toolchain.py --policy-only',
        1,
        "workflow policy-only call",
    )
    require_exact_count(
        text,
        'run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
        1,
        "workflow archive-only call",
    )
    require_exact_count(
        text,
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        1,
        "workflow repo-local archive call",
    )
    require_order(
        text,
        '- name: Check current Zig toolchain policy packet',
        '- name: Check current pinned Zig archive packet',
        "workflow step order",
    )
    require_order(
        text,
        '- name: Check current pinned Zig archive packet',
        '- name: Self-test current Zig installer helper',
        "workflow step order",
    )

    return len(WORKFLOW_MARKERS)


def validate_root(root: Path) -> tuple[int, int, str, str]:
    target, channel = validate_policy(root)
    script_marker_count = validate_script(root)
    workflow_marker_count = validate_workflow(root)
    return script_marker_count, workflow_marker_count, target, channel


def write_fixture(root: Path) -> None:
    (root / SCRIPT_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW_REL).parent.mkdir(parents=True, exist_ok=True)
    (root / POLICY_REL).parent.mkdir(parents=True, exist_ok=True)

    (root / SCRIPT_REL).write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
                'add_search_root(root / ".zig-toolchain")',
                'add_search_root(root / "toolchains")',
                'add_search_root(root / ".toolchains")',
                'add_search_root(root / "third_party")',
                'add_search_root(root / "agent_files")',
                'add_search_root(parent / ".toolchains")',
                'add_search_root(parent / "toolchains")',
                'add_search_root(parent / "agent_files")',
                'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
                'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
                'parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")',
                'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
                'archive_targets = payload["upgrade_policy"]["archive_target_scope"]',
                'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
                'print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload[\'channel\']}")',
                'print("ZIG_TOOLCHAIN_ARCHIVE_TARGETS=" + ",".join(str(target) for target in upgrade_policy["archive_target_scope"]))',
                'print("ZIG_TOOLCHAIN_REQUIRED_MAKE_ROUTES=" + ",".join(str(route) for route in upgrade_policy["required_make_routes"]))',
                'print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or \'unresolved\'}")',
                'print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (root / WORKFLOW_REL).write_text(
        "\n".join(
            [
                "name: zigux-bootstrap",
                "- name: Setup pinned Zig toolchain",
                'targets = policy["upgrade_policy"]["archive_target_scope"]',
                'channel = policy["channel"]',
                'print(f"ZIGUX_ZIG_TARGET=\'{target}\'")',
                'print(f"ZIGUX_ZIG_CHANNEL=\'{channel}\'")',
                'print(f"ZIGUX_ZIG_FILENAME=\'{filename}\'")',
                'print(f"ZIGUX_ZIG_URL=\'{url}\'")',
                'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
                '- name: Check current Zig toolchain policy packet',
                'run: python3 scripts/zigux/check-zig-toolchain.py --policy-only',
                '- name: Check current pinned Zig archive packet',
                'run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
                '- name: Self-test current Zig installer helper',
                'run: python3 scripts/zigux/install-zig.py --self-test',
                "",
            ]
        ),
        encoding="utf-8",
    )

    (root / POLICY_REL).write_text(
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
                    "required_make_routes": EXPECTED_REQUIRED_MAKE_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def rewrite_text(path: Path, old: str, new: str) -> None:
    path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    cases = [
        ("baseline", None),
        (
            "missing_agent_files_search_root",
            lambda root: rewrite_text(root / SCRIPT_REL, 'add_search_root(root / "agent_files")\n', ""),
        ),
        (
            "missing_policy_step",
            lambda root: rewrite_text(
                root / WORKFLOW_REL,
                'run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n',
                "",
            ),
        ),
        (
            "missing_repo_archive_call",
            lambda root: rewrite_text(
                root / WORKFLOW_REL,
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"\n',
                "",
            ),
        ),
        (
            "wrong_archive_target_scope",
            lambda root: (root / POLICY_REL).write_text(
                json.dumps(
                    {
                        **json.loads(load_text(root, POLICY_REL)),
                        "upgrade_policy": {
                            **json.loads(load_text(root, POLICY_REL))["upgrade_policy"],
                            "archive_target_scope": ["aarch64-linux"],
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            ),
        ),
        (
            "missing_phase2_cross_route",
            lambda root: (root / POLICY_REL).write_text(
                json.dumps(
                    {
                        **json.loads(load_text(root, POLICY_REL)),
                        "upgrade_policy": {
                            **json.loads(load_text(root, POLICY_REL))["upgrade_policy"],
                            "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            ),
        ),
    ]

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="lane05-zig-toolchain-contract-") as tmp_dir:
            root = Path(tmp_dir)
            write_fixture(root)
            if mutate is not None:
                mutate(root)
            try:
                validate_root(root)
            except ValueError:
                if name == "baseline":
                    raise
            else:
                if name != "baseline":
                    raise AssertionError(f"expected {name} to fail")
            case_count += 1

    print("LANE05_ZIG_TOOLCHAIN_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def write_sample_root(destination: Path) -> None:
    write_fixture(destination)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 Zig toolchain contract stays aligned across script, policy, and workflow surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for standalone validation.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        script_marker_count, workflow_marker_count, target, channel = validate_root(
            args.root.resolve()
        )
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print("LANE05_ZIG_TOOLCHAIN_CONTRACT=fail")
        print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_ZIG_TOOLCHAIN_CONTRACT=pass")
    print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_ZIG_TOOLCHAIN_SCRIPT_MARKER_COUNT={script_marker_count}")
    print(f"LANE05_ZIG_TOOLCHAIN_WORKFLOW_MARKER_COUNT={workflow_marker_count}")
    print(f"LANE05_ZIG_TOOLCHAIN_TARGET={target}")
    print(f"LANE05_ZIG_TOOLCHAIN_CHANNEL={channel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
