#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PHASE2_CROSS_CHECKER = ROOT / "scripts" / "zigux" / "check-phase2-cross.py"
TARGETS_MANIFEST = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
CONF_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig"
CONFDATA_BRIDGE = ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig"

EXPECTED_PHASE = "Phase 2"
EXPECTED_LANE = 21
EXPECTED_STATUS = "starter"
EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]
EXPECTED_ZIG_TEST_FILES = [
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
]
CHECKER_REQUIRED_MARKERS = [
    'EXPECTED_LANE = 21',
    'EXPECTED_STATUS = "starter"',
    '    "scripts/zigux/kconfig/conf_bridge.zig",',
    '    "scripts/zigux/kconfig/confdata_bridge.zig",',
    '"--test-no-exec"',
    'print("PHASE2_CROSS_SELF_TEST=pass")',
    'print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")',
    "print(f\"PHASE2_CROSS_FILE_COUNT={len(payload['zig_test_files'])}\")",
]
CHECKER_FORBIDDEN_MARKERS = [
    '    "scripts/zigux/fixdep.zig",',
    '    "scripts/zigux/genksyms.zig",',
    'CHECK_ZIG_TOOLCHAIN = ROOT / "scripts" / "zigux" / "check-zig-toolchain.py"',
]

EXPECTED_SELF_TEST_CASE_COUNT = 13


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{label}:invalid_json:{exc.msg}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"{label}:expected_object")
    return payload


def validate_required_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    return [f"{label}:missing_marker:{marker}" for marker in markers if marker not in text]


def validate_forbidden_markers(text: str, *, label: str, markers: list[str]) -> list[str]:
    return [f"{label}:forbidden_marker:{marker}" for marker in markers if marker in text]


def validate_targets_manifest(payload: dict[str, object]) -> list[str]:
    issues: list[str] = []
    if payload.get("phase") != EXPECTED_PHASE:
        issues.append(f"targets:phase={payload.get('phase')!r}:expected={EXPECTED_PHASE!r}")
    if payload.get("lane") != EXPECTED_LANE:
        issues.append(f"targets:lane={payload.get('lane')!r}:expected={EXPECTED_LANE}")
    if payload.get("status") != EXPECTED_STATUS:
        issues.append(f"targets:status={payload.get('status')!r}:expected={EXPECTED_STATUS!r}")
    if payload.get("target_count") != len(EXPECTED_TARGETS):
        issues.append(
            f"targets:target_count={payload.get('target_count')!r}:expected={len(EXPECTED_TARGETS)}"
        )
    targets = payload.get("targets")
    if not isinstance(targets, list):
        issues.append("targets:targets:expected_list")
        return issues
    if targets != EXPECTED_TARGETS:
        issues.append("targets:targets=expected_exact_list")
    zig_test_files = payload.get("zig_test_files")
    if zig_test_files != EXPECTED_ZIG_TEST_FILES:
        issues.append("targets:zig_test_files=expected_exact_list")
    return issues


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    required_files = [
        PHASE2_CROSS_CHECKER,
        TARGETS_MANIFEST,
        CONF_BRIDGE,
        CONFDATA_BRIDGE,
    ]
    missing = [
        str(path.relative_to(ROOT))
        for path in required_files
        if not (root / path.relative_to(ROOT)).exists()
    ]
    if missing:
        return [f"missing:{item}" for item in missing]

    checker_text = (root / PHASE2_CROSS_CHECKER.relative_to(ROOT)).read_text(encoding="utf-8")
    issues.extend(
        validate_required_markers(
            checker_text,
            label="phase2_cross_checker",
            markers=CHECKER_REQUIRED_MARKERS,
        )
    )
    issues.extend(
        validate_forbidden_markers(
            checker_text,
            label="phase2_cross_checker",
            markers=CHECKER_FORBIDDEN_MARKERS,
        )
    )
    issues.extend(
        validate_targets_manifest(
            load_json_object(root / TARGETS_MANIFEST.relative_to(ROOT), label="targets")
        )
    )
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / PHASE2_CROSS_CHECKER.relative_to(ROOT),
        "\n".join(
            [
                'EXPECTED_LANE = 21',
                'EXPECTED_STATUS = "starter"',
                'EXPECTED_TARGETS = [',
                '    "x86_64-linux-musl",',
                '    "aarch64-linux-musl",',
                '    "riscv64-linux-musl",',
                ']',
                'EXPECTED_ZIG_TEST_FILES = [',
                '    "scripts/zigux/kconfig/conf_bridge.zig",',
                '    "scripts/zigux/kconfig/confdata_bridge.zig",',
                ']',
                '["zig", "test", rel_path, "-target", target, "--test-no-exec"]',
                'print("PHASE2_CROSS_SELF_TEST=pass")',
                'print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")',
                "print(f\"PHASE2_CROSS_FILE_COUNT={len(payload['zig_test_files'])}\")",
            ]
        )
        + "\n",
    )
    write_text(
        root / TARGETS_MANIFEST.relative_to(ROOT),
        json.dumps(
            {
                "phase": EXPECTED_PHASE,
                "lane": EXPECTED_LANE,
                "status": EXPECTED_STATUS,
                "target_count": len(EXPECTED_TARGETS),
                "targets": EXPECTED_TARGETS,
                "zig_test_files": EXPECTED_ZIG_TEST_FILES,
            },
            indent=2,
        )
        + "\n",
    )
    write_text(root / CONF_BRIDGE.relative_to(ROOT), 'test "stub" {}\n')
    write_text(root / CONFDATA_BRIDGE.relative_to(ROOT), 'test "stub" {}\n')


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="lane21_cross_alignment_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)

        build_self_test_root(tmp_root)
        if collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:valid_root")
        checks_run += 1

        build_self_test_root(tmp_root)
        manifest_path = tmp_root / TARGETS_MANIFEST.relative_to(ROOT)
        manifest = load_json_object(manifest_path, label="targets")
        manifest["status"] = "closed"
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        if "targets:status='closed':expected='starter'" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:status_mismatch")
        checks_run += 1

        build_self_test_root(tmp_root)
        manifest = load_json_object(manifest_path, label="targets")
        manifest["target_count"] = 2
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        if "targets:target_count=2:expected=3" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:target_count_mismatch")
        checks_run += 1

        build_self_test_root(tmp_root)
        manifest = load_json_object(manifest_path, label="targets")
        manifest["zig_test_files"] = ["scripts/zigux/genksyms.zig"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        if "targets:zig_test_files=expected_exact_list" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:zig_test_files_mismatch")
        checks_run += 1

        build_self_test_root(tmp_root)
        write_text(manifest_path, "{\n")
        try:
            collect_issues(tmp_root)
        except SystemExit as exc:
            if not str(exc).startswith("targets:invalid_json:"):
                raise
        else:
            raise SystemExit("phase2-cross-alignment:self-test:invalid_json_missing")
        checks_run += 1

        build_self_test_root(tmp_root)
        write_text(manifest_path, "[]\n")
        try:
            collect_issues(tmp_root)
        except SystemExit as exc:
            if str(exc) != "targets:expected_object":
                raise
        else:
            raise SystemExit("phase2-cross-alignment:self-test:expected_object_missing")
        checks_run += 1

        build_self_test_root(tmp_root)
        checker_path = tmp_root / PHASE2_CROSS_CHECKER.relative_to(ROOT)
        checker_text = checker_path.read_text(encoding="utf-8").replace(
            'EXPECTED_STATUS = "starter"\n',
            "",
            1,
        )
        write_text(checker_path, checker_text)
        if (
            'phase2_cross_checker:missing_marker:EXPECTED_STATUS = "starter"'
            not in collect_issues(tmp_root)
        ):
            raise SystemExit("phase2-cross-alignment:self-test:missing_checker_marker")
        checks_run += 1

        build_self_test_root(tmp_root)
        checker_text = checker_path.read_text(encoding="utf-8") + '    "scripts/zigux/genksyms.zig",\n'
        write_text(checker_path, checker_text)
        if (
            'phase2_cross_checker:forbidden_marker:    "scripts/zigux/genksyms.zig",'
            not in collect_issues(tmp_root)
        ):
            raise SystemExit("phase2-cross-alignment:self-test:forbidden_checker_marker")
        checks_run += 1

        build_self_test_root(tmp_root)
        (tmp_root / CONF_BRIDGE.relative_to(ROOT)).unlink()
        if "missing:scripts/zigux/kconfig/conf_bridge.zig" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:missing_conf_bridge")
        checks_run += 1

        build_self_test_root(tmp_root)
        (tmp_root / CONFDATA_BRIDGE.relative_to(ROOT)).unlink()
        if "missing:scripts/zigux/kconfig/confdata_bridge.zig" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:missing_confdata_bridge")
        checks_run += 1

        build_self_test_root(tmp_root)
        (tmp_root / PHASE2_CROSS_CHECKER.relative_to(ROOT)).unlink()
        if "missing:scripts/zigux/check-phase2-cross.py" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:missing_checker")
        checks_run += 1

        build_self_test_root(tmp_root)
        (tmp_root / TARGETS_MANIFEST.relative_to(ROOT)).unlink()
        if "missing:zigux/tests/fixtures/phase2_cross_targets.json" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:missing_manifest")
        checks_run += 1

        build_self_test_root(tmp_root)
        manifest = load_json_object(manifest_path, label="targets")
        manifest["targets"] = ["x86_64-linux-musl"]
        write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")
        if "targets:targets=expected_exact_list" not in collect_issues(tmp_root):
            raise SystemExit("phase2-cross-alignment:self-test:target_list_mismatch")
        checks_run += 1

    if checks_run != EXPECTED_SELF_TEST_CASE_COUNT:
        raise SystemExit(
            "phase2-cross-alignment:self-test:case_count:"
            f"actual={checks_run}:expected={EXPECTED_SELF_TEST_CASE_COUNT}"
        )

    print("PHASE2_CROSS_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE2_CROSS_ALIGNMENT_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Lane 21 Phase 2 cross-target starter packet aligned with its manifest and starter checker."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        issues = collect_issues(args.root)
    except SystemExit as exc:
        print("PHASE2_CROSS_ALIGNMENT=fail")
        print(str(exc))
        return 1

    if issues:
        print("PHASE2_CROSS_ALIGNMENT=fail")
        print("INVALID_PHASE2_CROSS_ALIGNMENT_START")
        for issue in issues:
            print(issue)
        print("INVALID_PHASE2_CROSS_ALIGNMENT_END")
        return 1

    print("PHASE2_CROSS_ALIGNMENT=pass")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(EXPECTED_TARGETS)}")
    print(f"PHASE2_CROSS_FILE_COUNT={len(EXPECTED_ZIG_TEST_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())