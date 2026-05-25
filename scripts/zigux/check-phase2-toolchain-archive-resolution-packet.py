#!/usr/bin/env python3
"""Guard the current Lane 03 pinned archive search and resolution packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"

TOOLCHAIN_CHECKER_MARKERS = (
    "ARCHIVE_DUPLICATE_SUFFIX_RE = re.compile(",
    "TOOLCHAIN_POLICY = ROOT / \"scripts\" / \"zigux\" / \"zig-toolchain-policy.json\"",
    "def policy_archive_filename(",
    "def iter_archive_search_roots(",
    "def archive_name_has_duplicate_suffix(",
    "def archive_name_matches_policy(",
    "def describe_missing_archive(",
    "def describe_invalid_explicit_archive_path(",
    "def iter_repo_local_archive_candidates(",
    "def resolve_policy_archive(",
    "def expected_archive_metadata(",
    "def validate_policy_archive(",
    'parser.add_argument("--archive-only", action="store_true", help="Validate the pinned Zig archive artifact without probing a zig executable.")',
    'parser.add_argument("--archive", help="Explicit Zig archive path for archive-integrity validation.")',
    'parser.add_argument("--archive-target", help="Archive target key from scripts/zigux/zig-toolchain-policy.json.")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=missing")',
    'print("ZIG_TOOLCHAIN_ARCHIVE_STATUS=invalid")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_SEARCH_ROOTS={search_roots_summary}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_FILENAME={expected_filename}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_EXPECTED_SHA256={validated_expected_sha}")',
    'print(f"ZIG_TOOLCHAIN_ARCHIVE_ACTUAL_SHA256={actual_sha}")',
)

ARCHIVE_SEARCH_ROOT_ORDER = (
    'add_search_root(root / ".zig-toolchain")',
    'add_search_root(root / "toolchains")',
    'add_search_root(root / ".toolchains")',
    'add_search_root(root / "third_party")',
    'add_search_root(root / "agent_files")',
    'add_search_root(parent / ".toolchains")',
    'add_search_root(parent / "toolchains")',
    'add_search_root(parent / "agent_files")',
)

WORKFLOW_MARKERS = (
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'repo_archive_parts_dir="${repo_archive_path}.parts"',
    'python3 scripts/zigux/stage-pinned-zig-archive.py                 --root "$GITHUB_WORKSPACE"                 --parts-dir "$repo_archive_parts_dir" || return 1',
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'if [ ! -d "$repo_archive_parts_dir" ]; then',
)

WORKFLOW_STEP_LINE = 'run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing'
MAKEFILE_STEP_LINE = '$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing'

EXPECTED_PHASE = "Phase 2"
EXPECTED_CHANNEL = "0.17.0-dev.87+9b177a7d2"
EXPECTED_TARGET_SCOPE = ["x86_64-linux"]
EXPECTED_REQUIRED_ROUTES = [
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str = "") -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            if replacement:
                lines[index] = replacement
            else:
                del lines[index]
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_marker_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = text.count(marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_line_issues(text: str, marker: str, missing_code: str, duplicate_code: str) -> list[tuple[str, str]]:
    count = count_exact_lines(text, marker)
    if count == 0:
        return [(missing_code, marker)]
    if count != 1:
        return [(duplicate_code, f"{marker}:count={count}")]
    return []


def collect_order_issues(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    previous = -1
    for marker in markers:
        index = text.find(marker)
        if index < 0:
            return []
        if index <= previous:
            return [(code, marker)]
        previous = index
    return []


def validate_policy(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]

    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))
    if payload.get("channel") != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY", f"channel={payload.get('channel')!r}"))
    if payload.get("minimum_version") != EXPECTED_CHANNEL:
        issues.append(("INVALID_POLICY", f"minimum_version={payload.get('minimum_version')!r}"))

    archive_sha256 = payload.get("archive_sha256")
    if not isinstance(archive_sha256, dict):
        issues.append(("INVALID_POLICY", "archive_sha256"))
    else:
        if list(archive_sha256.keys()) != EXPECTED_TARGET_SCOPE:
            issues.append(("INVALID_POLICY", f"archive_sha256_keys={list(archive_sha256.keys())!r}"))
        for target, digest in archive_sha256.items():
            if not isinstance(digest, str) or len(digest) != 64:
                issues.append(("INVALID_POLICY", f"archive_sha256[{target}]"))

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        issues.append(("INVALID_POLICY", "upgrade_policy"))
    else:
        if upgrade_policy.get("channel_minimum_lockstep") is not True:
            issues.append(("INVALID_POLICY", "channel_minimum_lockstep"))
        if upgrade_policy.get("archive_target_scope") != EXPECTED_TARGET_SCOPE:
            issues.append(("INVALID_POLICY", "archive_target_scope"))
        if upgrade_policy.get("required_make_routes") != EXPECTED_REQUIRED_ROUTES:
            issues.append(("INVALID_POLICY", "required_make_routes"))

    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    checker_text = read_text(resolve_path(root, TOOLCHAIN_CHECKER))
    issues.extend(
        collect_marker_issues(
            checker_text,
            TOOLCHAIN_CHECKER_MARKERS,
            "MISSING_TOOLCHAIN_CHECKER_MARKER",
            "DUPLICATE_TOOLCHAIN_CHECKER_MARKER",
        )
    )
    issues.extend(
        collect_marker_issues(
            checker_text,
            ARCHIVE_SEARCH_ROOT_ORDER,
            "MISSING_ARCHIVE_SEARCH_ROOT_MARKER",
            "DUPLICATE_ARCHIVE_SEARCH_ROOT_MARKER",
        )
    )
    issues.extend(collect_order_issues(checker_text, ARCHIVE_SEARCH_ROOT_ORDER, "ARCHIVE_SEARCH_ROOT_ORDER_DRIFT"))

    workflow_text = read_text(resolve_path(root, WORKFLOW))
    issues.extend(
        collect_marker_issues(
            workflow_text,
            WORKFLOW_MARKERS,
            "MISSING_WORKFLOW_MARKER",
            "DUPLICATE_WORKFLOW_MARKER",
        )
    )
    issues.extend(
        collect_line_issues(
            workflow_text,
            WORKFLOW_STEP_LINE,
            "MISSING_WORKFLOW_STEP_LINE",
            "DUPLICATE_WORKFLOW_STEP_LINE",
        )
    )

    makefile_text = read_text(resolve_path(root, MAKEFILE))
    issues.extend(
        collect_line_issues(
            makefile_text,
            MAKEFILE_STEP_LINE,
            "MISSING_MAKEFILE_STEP_LINE",
            "DUPLICATE_MAKEFILE_STEP_LINE",
        )
    )

    policy_path = resolve_path(root, TOOLCHAIN_POLICY)
    try:
        payload = json.loads(read_text(policy_path))
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
    else:
        issues.extend(validate_policy(payload))

    return issues


def build_current_like_root(root: Path) -> None:
    write_text(
        resolve_path(root, TOOLCHAIN_CHECKER),
        "\n".join(
            [
                "#!/usr/bin/env python3",
                *TOOLCHAIN_CHECKER_MARKERS,
                *ARCHIVE_SEARCH_ROOT_ORDER,
            ]
        )
        + "\n",
    )
    write_text(
        resolve_path(root, WORKFLOW),
        "\n".join(["name: zigux-bootstrap", *WORKFLOW_MARKERS, WORKFLOW_STEP_LINE]) + "\n",
    )
    write_text(resolve_path(root, MAKEFILE), "\n".join(["phase2-toolchain:", MAKEFILE_STEP_LINE]) + "\n")
    write_text(
        resolve_path(root, TOOLCHAIN_POLICY),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "channel": EXPECTED_CHANNEL,
                "minimum_version": EXPECTED_CHANNEL,
                "archive_sha256": {"x86_64-linux": "3" * 64},
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": EXPECTED_TARGET_SCOPE,
                    "required_make_routes": EXPECTED_REQUIRED_ROUTES,
                },
            },
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_archive_resolution_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_current_like_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in TOOLCHAIN_CHECKER_MARKERS:
            build_current_like_root(root)
            checker_path = resolve_path(root, TOOLCHAIN_CHECKER)
            checker_path.write_text(
                replace_once(checker_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_TOOLCHAIN_CHECKER_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        checker_path = resolve_path(root, TOOLCHAIN_CHECKER)
        checker_path.write_text(
            replace_once(
                checker_path.read_text(encoding="utf-8"),
                ARCHIVE_SEARCH_ROOT_ORDER[0],
                ARCHIVE_SEARCH_ROOT_ORDER[0] + ARCHIVE_SEARCH_ROOT_ORDER[0],
            ),
            encoding="utf-8",
        )
        assert (
            "DUPLICATE_ARCHIVE_SEARCH_ROOT_MARKER",
            f"{ARCHIVE_SEARCH_ROOT_ORDER[0]}:count=2",
        ) in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        checker_path = resolve_path(root, TOOLCHAIN_CHECKER)
        checker_text = checker_path.read_text(encoding="utf-8")
        checker_text = checker_text.replace(
            ARCHIVE_SEARCH_ROOT_ORDER[2] + "\n" + ARCHIVE_SEARCH_ROOT_ORDER[3],
            ARCHIVE_SEARCH_ROOT_ORDER[3] + "\n" + ARCHIVE_SEARCH_ROOT_ORDER[2],
            1,
        )
        checker_path.write_text(checker_text, encoding="utf-8")
        assert ("ARCHIVE_SEARCH_ROOT_ORDER_DRIFT", ARCHIVE_SEARCH_ROOT_ORDER[3]) in collect_issues(root)
        checks_run += 1

        for marker in WORKFLOW_MARKERS:
            build_current_like_root(root)
            workflow_path = resolve_path(root, WORKFLOW)
            workflow_path.write_text(
                replace_once(workflow_path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            duplicate_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_STEP_LINE),
            encoding="utf-8",
        )
        assert ("DUPLICATE_WORKFLOW_STEP_LINE", f"{WORKFLOW_STEP_LINE}:count=2") in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(
            replace_exact_line(workflow_path.read_text(encoding="utf-8"), WORKFLOW_STEP_LINE),
            encoding="utf-8",
        )
        assert ("MISSING_WORKFLOW_STEP_LINE", WORKFLOW_STEP_LINE) in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            duplicate_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_STEP_LINE),
            encoding="utf-8",
        )
        assert ("DUPLICATE_MAKEFILE_STEP_LINE", f"{MAKEFILE_STEP_LINE}:count=2") in collect_issues(root)
        checks_run += 1

        build_current_like_root(root)
        makefile_path = resolve_path(root, MAKEFILE)
        makefile_path.write_text(
            replace_exact_line(makefile_path.read_text(encoding="utf-8"), MAKEFILE_STEP_LINE),
            encoding="utf-8",
        )
        assert ("MISSING_MAKEFILE_STEP_LINE", MAKEFILE_STEP_LINE) in collect_issues(root)
        checks_run += 1

        policy_cases = (
            (lambda payload: payload.__setitem__("phase", "Phase 3"), ("INVALID_POLICY", "phase='Phase 3'")),
            (
                lambda payload: payload["upgrade_policy"].__setitem__("archive_target_scope", ["aarch64-linux"]),
                ("INVALID_POLICY", "archive_target_scope"),
            ),
            (
                lambda payload: payload["upgrade_policy"].__setitem__("required_make_routes", ["phase2-toolchain"]),
                ("INVALID_POLICY", "required_make_routes"),
            ),
            (
                lambda payload: payload["archive_sha256"].__setitem__("x86_64-linux", "short"),
                ("INVALID_POLICY", "archive_sha256[x86_64-linux]"),
            ),
        )
        for mutator, expected in policy_cases:
            build_current_like_root(root)
            policy_path = resolve_path(root, TOOLCHAIN_POLICY)
            payload = json.loads(policy_path.read_text(encoding="utf-8"))
            mutator(payload)
            policy_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            assert expected in collect_issues(root)
            checks_run += 1

        build_current_like_root(root)
        policy_path = resolve_path(root, TOOLCHAIN_POLICY)
        policy_path.write_text("{not-json}\n", encoding="utf-8")
        assert any(code == "INVALID_POLICY_JSON" for code, _ in collect_issues(root))
        checks_run += 1

        for path in (TOOLCHAIN_CHECKER, WORKFLOW, MAKEFILE, TOOLCHAIN_POLICY):
            build_current_like_root(root)
            resolve_path(root, path).unlink()
            try:
                collect_issues(root)
            except SystemExit as exc:
                assert "required file missing" in str(exc)
                checks_run += 1
            else:
                raise AssertionError(f"missing file did not abort: {path}")

    print("PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_PACKET_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_PACKET_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 03 pinned archive search and resolution packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        print("PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_PACKET=fail")
        for code, value in issues:
            print(f"{code}:{value}")
        return 1

    print("PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_PACKET=pass")
    print(f"PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_MARKER_COUNT={len(TOOLCHAIN_CHECKER_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_SEARCH_ROOT_COUNT={len(ARCHIVE_SEARCH_ROOT_ORDER)}")
    print(f"PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_WORKFLOW_MARKER_COUNT={len(WORKFLOW_MARKERS)}")
    print("PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_WORKFLOW_STEP_LINE_COUNT=1")
    print("PHASE2_TOOLCHAIN_ARCHIVE_RESOLUTION_MAKEFILE_STEP_LINE_COUNT=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
