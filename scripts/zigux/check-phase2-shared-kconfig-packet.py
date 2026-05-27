#!/usr/bin/env python3
"""Guard the shared Phase 2 kconfig bridge reminder packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()

REVIEW_CHECKLIST = ROOT / "Documentation/zigux/review-checklist.md"
TESTS_README = ROOT / "zigux/tests/README.md"
KCONFIG_SELFTEST_ALIGNMENT = ROOT / "scripts/zigux/check-phase2-kconfig-selftest-alignment.py"
CONF_BRIDGE = ROOT / "scripts/zigux/kconfig/conf_bridge.zig"
CONFDATA_BRIDGE = ROOT / "scripts/zigux/kconfig/confdata_bridge.zig"
MAKEFILE = ROOT / "zigux/Makefile"

REQUIRED_PATHS = (
    REVIEW_CHECKLIST,
    TESTS_README,
    KCONFIG_SELFTEST_ALIGNMENT,
    CONF_BRIDGE,
    CONFDATA_BRIDGE,
    MAKEFILE,
)

REVIEW_MARKERS = (
    "if the change touches the shared Phase 2 kconfig bridge packet",
    "`Documentation/zigux/review-checklist.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`make -C zigux phase2-kconfig`",
)

TESTS_MARKERS = (
    "Keep the current direct-readback Phase 2 kconfig, genksyms, and fixdep packet:",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "Keep the rematerialized make-wrapper packet explicit through `make -C zigux phase2-toolchain`, `make -C zigux phase2-tools`, `make -C zigux phase2-kconfig`, `make -C zigux phase2-cross`, `make -C zigux phase2-genksyms`, `make -C zigux phase2-fixdep`, `make -C zigux phase2-validate`, and `make -C zigux phase2`.",
)

SELFTEST_ALIGNMENT_MARKERS = (
    "WORKFLOW_LINES = (",
    "MAKEFILE_LINES = (",
    'SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"',
    'TESTS_README = ROOT / "zigux" / "tests" / "README.md"',
    'REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"',
    '"run: python3 scripts/zigux/check-kconfig-bridge.py --self-test"',
    '"run: python3 scripts/zigux/check-kconfig-bridge.py"',
    '"run: zig test scripts/zigux/kconfig/conf_bridge.zig"',
    '"run: zig test scripts/zigux/kconfig/confdata_bridge.zig"',
    '"run: make -C zigux phase2-kconfig"',
    '"run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test"',
    '"run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py"',
)

CONF_BRIDGE_MARKERS = (
    "pub const Mode = enum {",
    "helpnewconfig,",
    "pub const Request = struct {",
    "fn modeAcceptsAllConfigOverride(mode: Mode) bool {",
    "pub fn runConfBridge(writer: anytype, request: Request) !void {",
)

CONFDATA_BRIDGE_MARKERS = (
    'const config_prefix = "CONFIG_";',
    "const EntryKind = enum {",
    "pub const Entry = struct {",
    "pub const Summary = struct {",
    "fn parseUnsetSymbol(line: []const u8) ?[]const u8 {",
    "pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {",
)

MAKEFILE_LINES = (
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
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


def collect_occurrence_issues(
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


def validate(root: Path) -> list[tuple[str, str]]:
    review_text = read_text(root / REVIEW_CHECKLIST.relative_to(ROOT))
    tests_text = read_text(root / TESTS_README.relative_to(ROOT))
    selftest_text = read_text(root / KCONFIG_SELFTEST_ALIGNMENT.relative_to(ROOT))
    conf_bridge_text = read_text(root / CONF_BRIDGE.relative_to(ROOT))
    confdata_text = read_text(root / CONFDATA_BRIDGE.relative_to(ROOT))
    makefile_text = read_text(root / MAKEFILE.relative_to(ROOT))

    issues: list[tuple[str, str]] = []
    issues.extend(collect_occurrence_issues(review_text, REVIEW_MARKERS, "REVIEW_MARKER_MISSING", "REVIEW_MARKER_DUPLICATED"))
    issues.extend(collect_occurrence_issues(tests_text, TESTS_MARKERS, "TESTS_MARKER_MISSING", "TESTS_MARKER_DUPLICATED"))
    issues.extend(
        collect_occurrence_issues(
            selftest_text,
            SELFTEST_ALIGNMENT_MARKERS,
            "SELFTEST_ALIGNMENT_MARKER_MISSING",
            "SELFTEST_ALIGNMENT_MARKER_DUPLICATED",
        )
    )
    issues.extend(
        collect_occurrence_issues(
            conf_bridge_text,
            CONF_BRIDGE_MARKERS,
            "CONF_BRIDGE_MARKER_MISSING",
            "CONF_BRIDGE_MARKER_DUPLICATED",
        )
    )
    issues.extend(
        collect_occurrence_issues(
            confdata_text,
            CONFDATA_BRIDGE_MARKERS,
            "CONFDATA_BRIDGE_MARKER_MISSING",
            "CONFDATA_BRIDGE_MARKER_DUPLICATED",
        )
    )
    issues.extend(collect_exact_line_issues(makefile_text, MAKEFILE_LINES, "MAKEFILE_LINE_MISSING", "MAKEFILE_LINE_DUPLICATED"))
    return issues


def sample_markdown(title: str, markers: tuple[str, ...]) -> str:
    lines = [f"# {title}", ""]
    for marker in markers:
        lines.append(f"- {marker}")
    lines.append("")
    return "\n".join(lines)


def sample_exact_lines(lines: tuple[str, ...]) -> str:
    return "\n".join(lines) + "\n"


def sample_selftest_alignment() -> str:
    return "\n".join(
        [
            "#!/usr/bin/env python3",
            "WORKFLOW_LINES = (",
            '    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",',
            '    "run: python3 scripts/zigux/check-kconfig-bridge.py",',
            '    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",',
            '    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",',
            '    "run: make -C zigux phase2-kconfig",',
            '    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",',
            '    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",',
            ")",
            "MAKEFILE_LINES = (",
            ")",
            'SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"',
            'TESTS_README = ROOT / "zigux" / "tests" / "README.md"',
            'REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"',
            "",
        ]
    )


def sample_conf_bridge() -> str:
    return "\n".join(
        [
            "pub const Mode = enum {",
            "    helpnewconfig,",
            "};",
            "pub const Request = struct {",
            "    mode: Mode,",
            "};",
            "fn modeAcceptsAllConfigOverride(mode: Mode) bool {",
            "    return mode == .helpnewconfig;",
            "}",
            "pub fn runConfBridge(writer: anytype, request: Request) !void {",
            "    _ = writer;",
            "    _ = request;",
            "}",
            "",
        ]
    )


def sample_confdata_bridge() -> str:
    return "\n".join(
        [
            'const config_prefix = "CONFIG_";',
            "const EntryKind = enum {",
            "    unset,",
            "};",
            "pub const Entry = struct {",
            "    name: []const u8,",
            "};",
            "pub const Summary = struct {",
            "    entries: []Entry,",
            "};",
            "fn parseUnsetSymbol(line: []const u8) ?[]const u8 {",
            "    return line;",
            "}",
            "pub fn parseConfig(allocator: std.mem.Allocator, input: []const u8) !Summary {",
            "    _ = allocator;",
            "    _ = input;",
            "    unreachable;",
            "}",
            "",
        ]
    )


def write_sample_root(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST.relative_to(ROOT), sample_markdown("Review Checklist", REVIEW_MARKERS))
    write_text(root / TESTS_README.relative_to(ROOT), sample_markdown("Tests README", TESTS_MARKERS))
    write_text(root / KCONFIG_SELFTEST_ALIGNMENT.relative_to(ROOT), sample_selftest_alignment())
    write_text(root / CONF_BRIDGE.relative_to(ROOT), sample_conf_bridge())
    write_text(root / CONFDATA_BRIDGE.relative_to(ROOT), sample_confdata_bridge())
    write_text(root / MAKEFILE.relative_to(ROOT), sample_exact_lines(MAKEFILE_LINES))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="lane25_shared_kconfig_packet_") as tempdir:
        root = Path(tempdir)
        write_sample_root(root)

        pass_issues = validate(root)
        if pass_issues:
            raise SystemExit(f"sample root should pass, found: {pass_issues}")

        broken_tests = read_text(root / TESTS_README.relative_to(ROOT)).replace(TESTS_MARKERS[0], "", 1)
        write_text(root / TESTS_README.relative_to(ROOT), broken_tests)
        fail_issues = validate(root)
        if not any(code == "TESTS_MARKER_MISSING" and detail == TESTS_MARKERS[0] for code, detail in fail_issues):
            raise SystemExit(f"expected missing tests marker failure, found: {fail_issues}")

    print("PHASE2_SHARED_KCONFIG_PACKET_SELF_TEST=pass")
    print("PHASE2_SHARED_KCONFIG_PACKET_SELF_TEST_CASE_COUNT=2")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repo root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--write-sample-root", type=Path, help="write a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    if args.write_sample_root:
        write_sample_root(args.write_sample_root)
        print(f"PHASE2_SHARED_KCONFIG_PACKET_SAMPLE_ROOT={args.write_sample_root}")
        return

    issues = validate(args.root)
    if issues:
        for code, detail in issues:
            print(f"{code}={detail}")
        raise SystemExit(1)

    print("PHASE2_SHARED_KCONFIG_PACKET=pass")
    print(f"PHASE2_SHARED_KCONFIG_PACKET_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(
        "PHASE2_SHARED_KCONFIG_PACKET_MARKER_COUNT="
        f"{len(REVIEW_MARKERS) + len(TESTS_MARKERS) + len(SELFTEST_ALIGNMENT_MARKERS) + len(CONF_BRIDGE_MARKERS) + len(CONFDATA_BRIDGE_MARKERS) + len(MAKEFILE_LINES)}"
    )


if __name__ == "__main__":
    main()
