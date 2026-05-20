#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SCRIPT_PATH = Path("scripts/zigux/check-zig-toolchain.py")
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGET = "x86_64-linux"
EXPECTED_SHA256 = "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
EXPECTED_REQUIRED_MAKE_ROUTES = ("phase2-toolchain", "phase2-validate")

SCRIPT_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    'parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")',
    'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
    'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
    'parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")',
    'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
    'parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")',
    'add_search_root(root / ".zig-toolchain")',
    'add_search_root(root / "toolchains")',
    'add_search_root(root / ".toolchains")',
    'add_search_root(root / "third_party")',
    'add_search_root(root / "agent_files")',
    'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
    'print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload[\'channel\']}")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or \'unresolved\'}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")',
    'return 0 if args.allow_missing else 1',
)

WORKFLOW_MARKERS = (
    "- name: Self-test current Zig toolchain checker",
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "- name: Check current Zig toolchain policy packet",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "- name: Check current pinned Zig archive packet",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"expected exactly {expected} occurrences of {label} {marker!r}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(f"expected {label} {earlier!r} before {later!r}")


def load_policy(root: Path) -> dict[str, object]:
    policy_path = root / POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")
    return payload


def validate_policy(payload: dict[str, object]) -> None:
    channel = payload.get("channel")
    minimum_version = payload.get("minimum_version")
    archives = payload.get("archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")

    if channel != EXPECTED_CHANNEL:
        raise ValueError(f"expected channel {EXPECTED_CHANNEL}, found {channel!r}")
    if minimum_version != EXPECTED_CHANNEL:
        raise ValueError(
            f"expected minimum_version {EXPECTED_CHANNEL}, found {minimum_version!r}"
        )
    if not isinstance(archives, dict):
        raise ValueError("invalid archive_sha256 payload")
    if archives.get(EXPECTED_TARGET) != EXPECTED_SHA256:
        raise ValueError(
            f"expected archive_sha256[{EXPECTED_TARGET}] {EXPECTED_SHA256}, found {archives.get(EXPECTED_TARGET)!r}"
        )
    if not isinstance(upgrade_policy, dict):
        raise ValueError("invalid upgrade_policy payload")
    if upgrade_policy.get("channel_minimum_lockstep") is not True:
        raise ValueError("expected channel_minimum_lockstep to stay true")
    if upgrade_policy.get("archive_target_scope") != [EXPECTED_TARGET]:
        raise ValueError(
            f"expected archive_target_scope [{EXPECTED_TARGET!r}], found {upgrade_policy.get('archive_target_scope')!r}"
        )
    if upgrade_policy.get("required_make_routes") != list(EXPECTED_REQUIRED_MAKE_ROUTES):
        raise ValueError(
            "expected required_make_routes "
            f"{list(EXPECTED_REQUIRED_MAKE_ROUTES)!r}, found {upgrade_policy.get('required_make_routes')!r}"
        )


def validate_script(script_text: str) -> None:
    for marker in SCRIPT_MARKERS:
        require_marker(script_text, marker, "toolchain script marker")

    require_exact_count(script_text, 'add_search_root(root / ".zig-toolchain")', 1, "search-root marker")
    require_exact_count(script_text, 'add_search_root(root / "toolchains")', 1, "search-root marker")
    require_exact_count(script_text, 'add_search_root(root / ".toolchains")', 1, "search-root marker")
    require_exact_count(script_text, 'add_search_root(root / "third_party")', 1, "search-root marker")
    require_exact_count(script_text, 'add_search_root(root / "agent_files")', 1, "search-root marker")
    require_exact_count(script_text, 'print("ZIG_TOOLCHAIN_POLICY_STATUS=present")', 1, "policy summary marker")
    require_exact_count(script_text, 'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")', 1, "archive-status marker")
    require_exact_count(script_text, 'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")', 1, "archive-status marker")
    require_exact_count(script_text, "return 0 if args.allow_missing else 1", 2, "allow-missing exit path")

    require_order(
        script_text,
        'parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
        'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
        "CLI flag order",
    )
    require_order(
        script_text,
        'add_search_root(root / ".toolchains")',
        'add_search_root(root / "third_party")',
        "archive search-root order",
    )
    require_order(
        script_text,
        'add_search_root(root / "third_party")',
        'add_search_root(root / "agent_files")',
        "archive search-root order",
    )
    require_order(
        script_text,
        'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
        'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")',
        "archive status order",
    )


def validate_workflow(workflow_text: str) -> None:
    for marker in WORKFLOW_MARKERS:
        require_marker(workflow_text, marker, "workflow marker")

    require_exact_count(
        workflow_text,
        "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
        1,
        "workflow self-test command",
    )
    require_exact_count(
        workflow_text,
        "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        1,
        "workflow policy command",
    )
    require_exact_count(
        workflow_text,
        "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        1,
        "workflow archive command",
    )
    require_order(
        workflow_text,
        "- name: Self-test current Zig toolchain checker",
        "- name: Check current Zig toolchain policy packet",
        "workflow step order",
    )
    require_order(
        workflow_text,
        "- name: Check current Zig toolchain policy packet",
        "- name: Check current pinned Zig archive packet",
        "workflow step order",
    )
    require_order(
        workflow_text,
        'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        'python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
        "workflow local archive validation order",
    )


def validate_root(root: Path) -> tuple[int, int]:
    script_text = (root / SCRIPT_PATH).read_text(encoding="utf-8")
    workflow_text = (root / WORKFLOW_PATH).read_text(encoding="utf-8")
    policy_payload = load_policy(root)

    validate_script(script_text)
    validate_workflow(workflow_text)
    validate_policy(policy_payload)

    return len(SCRIPT_MARKERS), len(WORKFLOW_MARKERS)


def write_sample_root(root: Path) -> None:
    (root / SCRIPT_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / POLICY_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / WORKFLOW_PATH.parent).mkdir(parents=True, exist_ok=True)

    script_lines = [
        '#!/usr/bin/env python3',
        'ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()',
        'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
        'def iter_archive_search_roots(root: Path = ROOT) -> list[Path]:',
        '    add_search_root(root / ".zig-toolchain")',
        '    add_search_root(root / "toolchains")',
        '    add_search_root(root / ".toolchains")',
        '    add_search_root(root / "third_party")',
        '    add_search_root(root / "agent_files")',
        'def main() -> int:',
        '    parser = argparse.ArgumentParser(description="Check local Zig toolchain availability for Zigux bootstrap work.")',
        '    parser.add_argument("--allow-missing", action="store_true", help="Return success when zig is unavailable.")',
        '    parser.add_argument("--policy-only", action="store_true", help="Validate and summarize the pinned Zig policy without probing a zig executable.")',
        '    parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
        '    parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")',
        '    parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
        '    parser.add_argument("--self-test", action="store_true", help="Run built-in parser and ordering checks.")',
        '    print("ZIG_TOOLCHAIN_POLICY_STATUS=present")',
        '    print(f"ZIG_TOOLCHAIN_PINNED_CHANNEL={payload[\'channel\']}")',
        '    print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
        '    print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")',
        '    return 0 if args.allow_missing else 1',
        '    print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")',
        '    print(f"ZIG_TOOLCHAIN_ARCHIVE_TARGET={archive_target or \'unresolved\'}")',
        '    print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")',
        '    print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}")',
        '    return 0 if args.allow_missing else 1',
    ]
    (root / SCRIPT_PATH).write_text("\n".join(script_lines) + "\n", encoding="utf-8")

    policy_payload = {
        "phase": "Phase 2",
        "channel": EXPECTED_CHANNEL,
        "minimum_version": EXPECTED_CHANNEL,
        "archive_sha256": {
            EXPECTED_TARGET: EXPECTED_SHA256,
        },
        "upgrade_policy": {
            "channel_minimum_lockstep": True,
            "archive_target_scope": [EXPECTED_TARGET],
            "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
        },
    }
    (root / POLICY_PATH).write_text(json.dumps(policy_payload, indent=2) + "\n", encoding="utf-8")

    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Setup pinned Zig toolchain",
        "        run: |",
        '          python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        '          python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"',
        "      - name: Self-test current Zig toolchain checker",
        "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "      - name: Check current Zig toolchain policy packet",
        "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        "      - name: Check current pinned Zig archive packet",
        "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    ]
    (root / WORKFLOW_PATH).write_text("\n".join(workflow_lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    case_count = 0

    def expect_pass() -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_toolchain_contract_pass_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            assert validate_root(root) == (len(SCRIPT_MARKERS), len(WORKFLOW_MARKERS))
            case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_toolchain_contract_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                validate_root(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected validate_root to fail")

    expect_pass()
    expect_failure(
        lambda root: (root / SCRIPT_PATH).write_text(
            (root / SCRIPT_PATH).read_text(encoding="utf-8").replace(
                'add_search_root(root / "agent_files")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'add_search_root(root / "agent_files")',
    )
    expect_failure(
        lambda root: (root / SCRIPT_PATH).write_text(
            (root / SCRIPT_PATH).read_text(encoding="utf-8").replace(
                'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=present")',
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(
                "      - name: Check current Zig toolchain policy packet\n"
                "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\n",
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "Check current Zig toolchain policy packet",
    )
    expect_failure(
        lambda root: (root / WORKFLOW_PATH).write_text(
            (root / WORKFLOW_PATH).read_text(encoding="utf-8").replace(
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
                'python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
                1,
            ),
            encoding="utf-8",
        ),
        '--archive "$repo_archive_path"',
    )
    expect_failure(
        lambda root: (root / POLICY_PATH).write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": EXPECTED_CHANNEL,
                    "minimum_version": EXPECTED_CHANNEL,
                    "archive_sha256": {EXPECTED_TARGET: EXPECTED_SHA256},
                    "upgrade_policy": {
                        "channel_minimum_lockstep": True,
                        "archive_target_scope": ["aarch64-linux"],
                        "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        ),
        "archive_target_scope",
    )
    expect_failure(
        lambda root: (root / POLICY_PATH).write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "channel": EXPECTED_CHANNEL,
                    "minimum_version": EXPECTED_CHANNEL,
                    "archive_sha256": {EXPECTED_TARGET: EXPECTED_SHA256},
                    "upgrade_policy": {
                        "channel_minimum_lockstep": False,
                        "archive_target_scope": [EXPECTED_TARGET],
                        "required_make_routes": list(EXPECTED_REQUIRED_MAKE_ROUTES),
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        ),
        "channel_minimum_lockstep",
    )

    print("LANE05_ZIG_TOOLCHAIN_CONTRACT_SELF_TEST=pass")
    print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the live Lane 05 Zig toolchain script, policy, and workflow packet stay aligned."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repo root to validate. Defaults to the current repository root.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-like sample root for checker replay.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    try:
        script_marker_count, workflow_marker_count = validate_root(args.root.resolve())
    except (FileNotFoundError, ValueError) as exc:
        print("LANE05_ZIG_TOOLCHAIN_CONTRACT=fail")
        print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_ROOT={args.root.resolve()}")
        print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_NOTE={exc}")
        return 1

    print("LANE05_ZIG_TOOLCHAIN_CONTRACT=pass")
    print(f"LANE05_ZIG_TOOLCHAIN_CONTRACT_ROOT={args.root.resolve()}")
    print(f"LANE05_ZIG_TOOLCHAIN_SCRIPT_MARKER_COUNT={script_marker_count}")
    print(f"LANE05_ZIG_TOOLCHAIN_WORKFLOW_MARKER_COUNT={workflow_marker_count}")
    print(f"LANE05_ZIG_TOOLCHAIN_TARGET={EXPECTED_TARGET}")
    print(f"LANE05_ZIG_TOOLCHAIN_CHANNEL={EXPECTED_CHANNEL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
