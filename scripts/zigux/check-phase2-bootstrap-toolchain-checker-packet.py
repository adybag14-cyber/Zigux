#!/usr/bin/env python3
"""Fail-closed guard for the live bootstrap toolchain-checker packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) >= 3 else Path.cwd()

WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
TOOLCHAIN_CHECKER = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"
TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
INSTALL_ZIG = ROOT / "scripts" / "zigux" / "install-zig.py"
LOCAL_FIRST_ARCHIVE_CHECKER = ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py"
LOCAL_ARCHIVE_README_CHECKER = ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py"
LOCAL_ARCHIVE_README = ROOT / "third_party" / "README.md"
FIXDEP_GATE_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py"

REQUIRED_FILES = (
    WORKFLOW,
    TOOLCHAIN_CHECKER,
    TOOLCHAIN_POLICY,
    INSTALL_ZIG,
    LOCAL_FIRST_ARCHIVE_CHECKER,
    LOCAL_ARCHIVE_README_CHECKER,
    LOCAL_ARCHIVE_README,
    FIXDEP_GATE_CHECKER,
)

WORKFLOW_EXACT_LINES = (
    "- name: Setup pinned Zig toolchain",
    "- name: Compile current scripts",
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "- name: Self-test current Phase 2 fixdep gate checker",
)

WORKFLOW_REQUIRED_MARKERS = (
    "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
    "echo 'no Python scripts found under scripts/zigux' >&2",
    'python3 -m py_compile "${scripts[@]}"',
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'targets = policy["upgrade_policy"]["archive_target_scope"]',
    'channel = policy["channel"]',
    'filename = f"zig-{target}-{channel}.tar.xz"',
    'url = f"https://ziglang.org/builds/{filename}"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    "try_local_archive() {",
    'python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if try_download "$ZIGUX_ZIG_URL"; then',
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
)

WORKFLOW_ORDER = (
    ("- name: Setup pinned Zig toolchain", "- name: Compile current scripts"),
    ("- name: Compile current scripts", "run: python3 scripts/zigux/check-zig-toolchain.py --self-test"),
    ("run: python3 scripts/zigux/check-zig-toolchain.py --self-test", "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only"),
    ("run: python3 scripts/zigux/check-zig-toolchain.py --policy-only", "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing"),
    ("run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing", "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test"),
    ("run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test", "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py"),
    ("run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py", "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test"),
    ("run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test", "run: python3 scripts/zigux/check-lane05-local-archive-readme.py"),
    ("run: python3 scripts/zigux/check-lane05-local-archive-readme.py", "run: python3 scripts/zigux/install-zig.py --self-test"),
    ("run: python3 scripts/zigux/install-zig.py --self-test", "- name: Self-test current Phase 2 fixdep gate checker"),
    ('policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))', 'targets = policy["upgrade_policy"]["archive_target_scope"]'),
    ('targets = policy["upgrade_policy"]["archive_target_scope"]', 'channel = policy["channel"]'),
    ('channel = policy["channel"]', 'filename = f"zig-{target}-{channel}.tar.xz"'),
    ('filename = f"zig-{target}-{channel}.tar.xz"', 'url = f"https://ziglang.org/builds/{filename}"'),
    ('mirror_file=".zig-toolchain/community-mirrors.txt"', "try_local_archive() {"),
)

TOOLCHAIN_CHECKER_MARKERS = (
    'TOOLCHAIN_POLICY = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"',
    "def resolve_zig_executable(",
    "def resolve_policy_archive(",
    "def validate_policy_archive(",
    'parser.add_argument("--policy-only"',
    'parser.add_argument("--archive-only"',
    'parser.add_argument("--archive"',
    'parser.add_argument("--archive-target"',
    'print("ZIG_TOOLCHAIN_SELF_TEST=pass")',
)

INSTALL_ZIG_MARKERS = (
    "INDEX_URL = 'https://ziglang.org/download/index.json'",
    "TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'",
    "def load_policy_channel(",
    "def load_policy_archive_sha256(",
    "def verify_archive_sha256(",
    "def copy_url_to_file(",
    "def resolve_target(",
    "def run_self_test() -> int:",
    "print('ZIG_INSTALL_SELF_TEST=pass')",
)

LOCAL_FIRST_ARCHIVE_CHECKER_MARKERS = (
    "POLICY_STEP = \"- name: Check current Zig toolchain policy packet\"",
    "ARCHIVE_CHECK_STEP = \"- name: Check current pinned Zig archive packet\"",
    "README_SELF_TEST_STEP = \"- name: Self-test current Lane 05 local archive README checker\"",
    "print(\"LANE05_LOCAL_FIRST_ARCHIVE_WORKFLOW_SELF_TEST=pass\")",
)

LOCAL_ARCHIVE_README_CHECKER_MARKERS = (
    'README_PATH = Path("third_party/README.md")',
    "EXPECTED_ARCHIVE_SIZES = {",
    "def validate_readme(",
    'print("LANE05_LOCAL_ARCHIVE_README_SELF_TEST=pass")',
)

LOCAL_ARCHIVE_README_MARKERS = (
    "# Zigux third-party archives",
    "Lane 05 bootstrap CI",
    "`third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
)

FIXDEP_GATE_CHECKER_MARKERS = (
    '"""Check the current fixdep governance packet against live Phase 2 surfaces."""',
    'print("PHASE2_FIXDEP_GATE_SELF_TEST=pass")',
)

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel": "0.17.0-dev.87+9b177a7d2",
    "minimum_version": "0.17.0-dev.87+9b177a7d2",
    "archive_sha256": {
        "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
    },
    "upgrade_policy": {
        "channel_minimum_lockstep": True,
        "archive_target_scope": ["x86_64-linux"],
        "required_make_routes": ["phase2-toolchain", "phase2-validate"],
    },
}

EXPECTED_SELF_TEST_CASE_COUNT = (
    1
    + len(WORKFLOW_EXACT_LINES)
    + len(WORKFLOW_EXACT_LINES)
    + len(WORKFLOW_REQUIRED_MARKERS)
    + len(WORKFLOW_ORDER)
    + len(TOOLCHAIN_CHECKER_MARKERS)
    + len(INSTALL_ZIG_MARKERS)
    + len(LOCAL_FIRST_ARCHIVE_CHECKER_MARKERS)
    + len(LOCAL_ARCHIVE_README_CHECKER_MARKERS)
    + len(LOCAL_ARCHIVE_README_MARKERS)
    + 4
    + len(REQUIRED_FILES)
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def collect_exact_line_issues(
    text: str,
    markers: tuple[str, ...],
    missing_code: str,
    duplicate_code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for marker in markers:
        count = count_exact_lines(text, marker)
        if count == 0:
            issues.append((missing_code, marker))
        elif count != 1:
            issues.append((duplicate_code, f"{marker}:count={count}"))
    return issues


def collect_missing_marker_issues(
    text: str,
    markers: tuple[str, ...],
    code: str,
) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def collect_order_issues(
    text: str,
    marker_pairs: tuple[tuple[str, str], ...],
    code: str,
) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    line_positions: dict[str, int] = {}
    for index, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if stripped not in line_positions:
            line_positions[stripped] = index
    for earlier, later in marker_pairs:
        earlier_index = line_positions.get(earlier)
        later_index = line_positions.get(later)
        if earlier_index is None or later_index is None:
            continue
        if earlier_index >= later_index:
            issues.append((code, f"{earlier} -> {later}"))
    return issues


def validate_policy(payload: object) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_POLICY", "expected JSON object")]

    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("INVALID_POLICY", f"phase={payload.get('phase')!r}"))
    if payload.get("channel") != EXPECTED_POLICY["channel"]:
        issues.append(("INVALID_POLICY", f"channel={payload.get('channel')!r}"))
    if payload.get("minimum_version") != EXPECTED_POLICY["minimum_version"]:
        issues.append(
            ("INVALID_POLICY", f"minimum_version={payload.get('minimum_version')!r}")
        )
    if payload.get("archive_sha256") != EXPECTED_POLICY["archive_sha256"]:
        issues.append(("INVALID_POLICY", "archive_sha256"))
    if payload.get("upgrade_policy") != EXPECTED_POLICY["upgrade_policy"]:
        issues.append(("INVALID_POLICY", "upgrade_policy"))
    return issues


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []

    for path in REQUIRED_FILES:
        resolved = root / path.relative_to(ROOT)
        if not resolved.exists():
            issues.append(("MISSING_REQUIRED_FILE", path.relative_to(ROOT).as_posix()))
    if issues:
        return issues

    workflow_text = read_text(root / WORKFLOW.relative_to(ROOT))
    toolchain_checker_text = read_text(root / TOOLCHAIN_CHECKER.relative_to(ROOT))
    install_zig_text = read_text(root / INSTALL_ZIG.relative_to(ROOT))
    local_first_archive_checker_text = read_text(
        root / LOCAL_FIRST_ARCHIVE_CHECKER.relative_to(ROOT)
    )
    local_archive_readme_checker_text = read_text(
        root / LOCAL_ARCHIVE_README_CHECKER.relative_to(ROOT)
    )
    local_archive_readme_text = read_text(root / LOCAL_ARCHIVE_README.relative_to(ROOT))
    fixdep_gate_checker_text = read_text(root / FIXDEP_GATE_CHECKER.relative_to(ROOT))
    policy_text = read_text(root / TOOLCHAIN_POLICY.relative_to(ROOT))

    issues.extend(
        collect_exact_line_issues(
            workflow_text,
            WORKFLOW_EXACT_LINES,
            "MISSING_WORKFLOW_LINE",
            "DUPLICATE_WORKFLOW_LINE",
        )
    )
    issues.extend(
        collect_missing_marker_issues(
            workflow_text,
            WORKFLOW_REQUIRED_MARKERS,
            "MISSING_WORKFLOW_MARKER",
        )
    )
    issues.extend(
        collect_order_issues(
            workflow_text,
            WORKFLOW_ORDER,
            "MISORDERED_WORKFLOW_MARKERS",
        )
    )
    issues.extend(
        collect_missing_marker_issues(
            toolchain_checker_text,
            TOOLCHAIN_CHECKER_MARKERS,
            "MISSING_TOOLCHAIN_CHECKER_MARKER",
        )
    )
    issues.extend(
        collect_missing_marker_issues(
            install_zig_text,
            INSTALL_ZIG_MARKERS,
            "MISSING_INSTALL_ZIG_MARKER",
        )
    )
    issues.extend(
        collect_missing_marker_issues(
            local_first_archive_checker_text,
            LOCAL_FIRST_ARCHIVE_CHECKER_MARKERS,
            "MISSING_LOCAL_FIRST_ARCHIVE_CHECKER_MARKER",
        )
    )
    issues.extend(
        collect_missing_marker_issues(
            local_archive_readme_checker_text,
            LOCAL_ARCHIVE_README_CHECKER_MARKERS,
            "MISSING_LOCAL_ARCHIVE_README_CHECKER_MARKER",
        )
    )
    issues.extend(
        collect_missing_marker_issues(
            local_archive_readme_text,
            LOCAL_ARCHIVE_README_MARKERS,
            "MISSING_LOCAL_ARCHIVE_README_MARKER",
        )
    )
    issues.extend(
        collect_missing_marker_issues(
            fixdep_gate_checker_text,
            FIXDEP_GATE_CHECKER_MARKERS,
            "MISSING_FIXDEP_GATE_MARKER",
        )
    )

    try:
        payload = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        issues.append(("INVALID_POLICY_JSON", exc.msg))
    else:
        issues.extend(validate_policy(payload))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=fail")
    print("INVALID_PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_START")
    for code, values in grouped.items():
        for value in values:
            print(f"{code}:{value}")
    print("INVALID_PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_END")
    return 1


def build_self_test_root(root: Path) -> None:
    workflow_lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Setup pinned Zig toolchain",
        "        run: |",
        "          mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)",
        "          echo 'no Python scripts found under scripts/zigux' >&2",
        '          python3 -m py_compile "${scripts[@]}"',
        '          policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
        '          targets = policy["upgrade_policy"]["archive_target_scope"]',
        '          channel = policy["channel"]',
        '          filename = f"zig-{target}-{channel}.tar.xz"',
        '          url = f"https://ziglang.org/builds/{filename}"',
        '          mirror_file=".zig-toolchain/community-mirrors.txt"',
        "          try_local_archive() {",
        '            python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"',
        "          }",
        "          try_download() {",
        "            return 0",
        "          }",
        '          if [ "${#scripts[@]}" -eq 0 ]; then',
        "            return 1",
        "          fi",
        '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
        "            true",
        "          fi",
        '          if try_download "$ZIGUX_ZIG_URL"; then',
        "            true",
        "          fi",
        "          echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
        "      - name: Compile current scripts",
        "        run: python3 -m py_compile scripts/zigux/*.py",
        "      - name: Self-test current Zig toolchain checker",
        "        run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
        "      - name: Check current Zig toolchain policy packet",
        "        run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
        "      - name: Check current pinned Zig archive packet",
        "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
        "      - name: Self-test current Lane 05 local-first archive checker",
        "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
        "      - name: Check current Lane 05 local-first archive packet",
        "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
        "      - name: Self-test current Lane 05 local archive README checker",
        "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
        "      - name: Check current Lane 05 local archive README packet",
        "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
        "      - name: Self-test current Zig installer helper",
        "        run: python3 scripts/zigux/install-zig.py --self-test",
        "      - name: Self-test current Phase 2 fixdep gate checker",
        "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    ]
    write_text(root / WORKFLOW.relative_to(ROOT), "\n".join(workflow_lines) + "\n")
    write_text(
        root / TOOLCHAIN_CHECKER.relative_to(ROOT),
        "\n".join(("#!/usr/bin/env python3", *TOOLCHAIN_CHECKER_MARKERS)) + "\n",
    )
    write_text(
        root / INSTALL_ZIG.relative_to(ROOT),
        "\n".join(("#!/usr/bin/env python3", *INSTALL_ZIG_MARKERS)) + "\n",
    )
    write_text(
        root / LOCAL_FIRST_ARCHIVE_CHECKER.relative_to(ROOT),
        "\n".join(("#!/usr/bin/env python3", *LOCAL_FIRST_ARCHIVE_CHECKER_MARKERS))
        + "\n",
    )
    write_text(
        root / LOCAL_ARCHIVE_README_CHECKER.relative_to(ROOT),
        "\n".join(("#!/usr/bin/env python3", *LOCAL_ARCHIVE_README_CHECKER_MARKERS))
        + "\n",
    )
    write_text(
        root / LOCAL_ARCHIVE_README.relative_to(ROOT),
        "\n".join(LOCAL_ARCHIVE_README_MARKERS) + "\n",
    )
    write_text(
        root / FIXDEP_GATE_CHECKER.relative_to(ROOT),
        "\n".join(("#!/usr/bin/env python3", *FIXDEP_GATE_CHECKER_MARKERS)) + "\n",
    )
    write_text(
        root / TOOLCHAIN_POLICY.relative_to(ROOT),
        json.dumps(EXPECTED_POLICY, indent=2) + "\n",
    )


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_bootstrap_toolchain_packet_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        for marker in WORKFLOW_EXACT_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            path.write_text(
                replace_exact_line(path.read_text(encoding="utf-8"), marker, "run: python3 broken.py"),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_LINE", marker) in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_EXACT_LINES:
            build_self_test_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            path.write_text(
                duplicate_exact_line(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2") in collect_issues(root)
            checks_run += 1

        for marker in WORKFLOW_REQUIRED_MARKERS:
            build_self_test_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_WORKFLOW_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for earlier, later in WORKFLOW_ORDER:
            build_self_test_root(root)
            path = root / WORKFLOW.relative_to(ROOT)
            text = path.read_text(encoding="utf-8")
            earlier_with_newline = earlier + "\n"
            later_with_newline = later + "\n"
            if earlier_with_newline in text and later_with_newline in text:
                text = text.replace(earlier_with_newline, "__EARLIER__\n", 1)
                text = text.replace(later_with_newline, earlier_with_newline, 1)
                text = text.replace("__EARLIER__\n", later_with_newline, 1)
            else:
                text = replace_once(text, earlier, f"{earlier}\n{later}")
            path.write_text(text, encoding="utf-8")
            assert (
                "MISORDERED_WORKFLOW_MARKERS",
                f"{earlier} -> {later}",
            ) in collect_issues(root)
            checks_run += 1

        for marker in TOOLCHAIN_CHECKER_MARKERS:
            build_self_test_root(root)
            path = root / TOOLCHAIN_CHECKER.relative_to(ROOT)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_TOOLCHAIN_CHECKER_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in INSTALL_ZIG_MARKERS:
            build_self_test_root(root)
            path = root / INSTALL_ZIG.relative_to(ROOT)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_INSTALL_ZIG_MARKER", marker) in collect_issues(root)
            checks_run += 1

        for marker in LOCAL_FIRST_ARCHIVE_CHECKER_MARKERS:
            build_self_test_root(root)
            path = root / LOCAL_FIRST_ARCHIVE_CHECKER.relative_to(ROOT)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (
                "MISSING_LOCAL_FIRST_ARCHIVE_CHECKER_MARKER",
                marker,
            ) in collect_issues(root)
            checks_run += 1

        for marker in LOCAL_ARCHIVE_README_CHECKER_MARKERS:
            build_self_test_root(root)
            path = root / LOCAL_ARCHIVE_README_CHECKER.relative_to(ROOT)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert (
                "MISSING_LOCAL_ARCHIVE_README_CHECKER_MARKER",
                marker,
            ) in collect_issues(root)
            checks_run += 1

        for marker in LOCAL_ARCHIVE_README_MARKERS:
            build_self_test_root(root)
            path = root / LOCAL_ARCHIVE_README.relative_to(ROOT)
            path.write_text(
                replace_once(path.read_text(encoding="utf-8"), marker),
                encoding="utf-8",
            )
            assert ("MISSING_LOCAL_ARCHIVE_README_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_self_test_root(root)
        path = root / TOOLCHAIN_POLICY.relative_to(ROOT)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["channel"] = "0.17.0"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "channel='0.17.0'") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / TOOLCHAIN_POLICY.relative_to(ROOT)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["archive_sha256"] = {"x86_64-linux": "deadbeef"}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("INVALID_POLICY", "archive_sha256") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = root / TOOLCHAIN_POLICY.relative_to(ROOT)
        path.write_text("{not-json}\n", encoding="utf-8")
        issues = collect_issues(root)
        assert any(code == "INVALID_POLICY_JSON" for code, _ in issues)
        checks_run += 1

        build_self_test_root(root)
        path = root / FIXDEP_GATE_CHECKER.relative_to(ROOT)
        path.write_text(
            replace_once(path.read_text(encoding="utf-8"), FIXDEP_GATE_CHECKER_MARKERS[1]),
            encoding="utf-8",
        )
        assert ("MISSING_FIXDEP_GATE_MARKER", FIXDEP_GATE_CHECKER_MARKERS[1]) in collect_issues(root)
        checks_run += 1

        for required_file in REQUIRED_FILES:
            build_self_test_root(root)
            (root / required_file.relative_to(ROOT)).unlink()
            assert (
                "MISSING_REQUIRED_FILE",
                required_file.relative_to(ROOT).as_posix(),
            ) in collect_issues(root)
            checks_run += 1

    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST=pass")
    print(
        f"PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_SELF_TEST_CASE_COUNT={checks_run}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current bootstrap toolchain-checker packet stays aligned."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET=pass")
    print(
        "PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_REQUIRED_FILE_COUNT="
        f"{len(REQUIRED_FILES)}"
    )
    print(
        "PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_WORKFLOW_LINE_COUNT="
        f"{len(WORKFLOW_EXACT_LINES)}"
    )
    print(
        "PHASE2_BOOTSTRAP_TOOLCHAIN_CHECKER_PACKET_WORKFLOW_MARKER_COUNT="
        f"{len(WORKFLOW_REQUIRED_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())