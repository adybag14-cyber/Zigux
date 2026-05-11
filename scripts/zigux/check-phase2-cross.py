#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json"
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
MAKEFILE = ROOT / "zigux" / "Makefile"
DOCS_ROOT = ROOT / "Documentation" / "zigux" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"

EXPECTED_TARGETS = [
    "x86_64-linux-musl",
    "aarch64-linux-musl",
    "riscv64-linux-musl",
]

EXPECTED_ZIG_TEST_FILES = [
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_crc.zig",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/mk_elfconfig.zig",
]

REQUIRED_FILES = [
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    *EXPECTED_ZIG_TEST_FILES,
]

FILE_MARKERS = {
    ".github/workflows/zigux-bootstrap.yml": [
        "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
        "run: python3 scripts/zigux/check-phase2-cross.py --target ${{ matrix.zig_target }}",
        "scripts/zigux/check-phase2-cross.py|scripts/zigux/check-phase2-cross-selftest-alignment.py|scripts/zigux/zig-toolchain-policy\\.json|scripts/zigux/fixdep\\.zig",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "- x86_64-linux-musl",
        "- aarch64-linux-musl",
        "- riscv64-linux-musl",
    ],
    "Documentation/zigux/README.md": [
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "make -C zigux phase2-cross",
    ],
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md": [
        "python3 scripts/zigux/check-phase2-cross.py --self-test",
        "python3 scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
    ],
    "Documentation/zigux/phase2-closure.md": [
        "shared cross compile self-test: `python3 scripts/zigux/check-phase2-cross.py --self-test`",
        "shared cross compile gate: `python3 scripts/zigux/check-phase2-cross.py`",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "make -C zigux phase2-cross",
    ],
    "Documentation/zigux/review-checklist.md": [
        "scripts/zigux/check-phase2-cross.py",
        "zigux/tests/fixtures/phase2_cross_targets.json",
        "make -C zigux phase2-cross",
    ],
    "scripts/zigux/README.md": [
        "the broader `phase2-toolchain`, `phase2-validate`, `phase2-tools`, `phase2-kconfig`, `phase2-cross`, and `phase2` route inventory",
        "the broader Phase 2 fixdep, genksyms, kconfig bridge, artifact-tools, manifest, cross-target, and closure-route inventory",
    ],
    "zigux/Makefile": [
        "phase2-cross:",
        "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-cross.py",
        "phase2: phase2-validate phase2-tools phase2-kconfig phase2-cross",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).is_file()]


def collect_missing_markers(root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path, markers in FILE_MARKERS.items():
        text = read_text(root / rel_path)
        for marker in markers:
            if marker not in text:
                issues.append(f"{rel_path}:missing:{marker}")
    return issues


def load_fixture(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fixture must be a JSON object")
    return payload


def validate_fixture(root: Path) -> list[str]:
    issues: list[str] = []
    payload = load_fixture(root / "zigux/tests/fixtures/phase2_cross_targets.json")

    if payload.get("phase") != "Phase 2":
        issues.append(f"fixture:phase:{payload.get('phase')!r}")

    targets = payload.get("targets")
    if targets != EXPECTED_TARGETS:
        issues.append(f"fixture:targets:{targets!r}")

    zig_test_files = payload.get("zig_test_files")
    if zig_test_files != EXPECTED_ZIG_TEST_FILES:
        issues.append(f"fixture:zig_test_files:{zig_test_files!r}")
    return issues


def run_cross_compile(root: Path, target: str) -> int:
    zig = shutil.which("zig")
    if zig is None:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=zig not found on PATH")
        return 1

    payload = load_fixture(root / "zigux/tests/fixtures/phase2_cross_targets.json")
    targets = payload.get("targets")
    if not isinstance(targets, list) or target not in targets:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_TARGET={target}")
        print("PHASE2_CROSS_NOTE=target not listed in fixture")
        return 1

    zig_test_files = payload.get("zig_test_files")
    if not isinstance(zig_test_files, list) or not all(isinstance(item, str) for item in zig_test_files):
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_NOTE=fixture zig_test_files is invalid")
        return 1

    for rel_path in zig_test_files:
        completed = subprocess.run(
            [zig, "test", rel_path, "-target", target],
            cwd=root,
            check=False,
        )
        if completed.returncode != 0:
            print("PHASE2_CROSS=fail")
            print(f"PHASE2_CROSS_TARGET={target}")
            print(f"PHASE2_CROSS_FAILED_FILE={rel_path}")
            return completed.returncode

    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET={target}")
    print(f"PHASE2_CROSS_FILE_COUNT={len(zig_test_files)}")
    return 0


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        if rel_path.endswith(".json"):
            continue
        write_text(root / rel_path, "")

    for rel_path, markers in FILE_MARKERS.items():
        write_text(root / rel_path, "\n".join(markers) + "\n")

    fixture = {
        "phase": "Phase 2",
        "targets": EXPECTED_TARGETS,
        "zig_test_files": EXPECTED_ZIG_TEST_FILES,
    }
    write_text(
        root / "zigux/tests/fixtures/phase2_cross_targets.json",
        json.dumps(fixture, indent=2) + "\n",
    )

    for rel_path in EXPECTED_ZIG_TEST_FILES:
        write_text(root / rel_path, "test {}\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase2_cross_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert require_files(root) == []
        assert collect_missing_markers(root) == []
        assert validate_fixture(root) == []
        case_count += 1

        build_self_test_root(root)
        (root / "zigux/tests/fixtures/phase2_cross_targets.json").write_text(
            json.dumps(
                {
                    "phase": "Phase 2",
                    "targets": EXPECTED_TARGETS[:-1],
                    "zig_test_files": EXPECTED_ZIG_TEST_FILES,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        issues = validate_fixture(root)
        assert any(issue.startswith("fixture:targets:") for issue in issues)
        case_count += 1

        build_self_test_root(root)
        path = root / "Documentation/zigux/phase2-closure.md"
        path.write_text(path.read_text(encoding="utf-8").replace("make -C zigux phase2-cross", "", 1), encoding="utf-8")
        issues = collect_missing_markers(root)
        assert any("Documentation/zigux/phase2-closure.md:missing:make -C zigux phase2-cross" == issue for issue in issues)
        case_count += 1

        build_self_test_root(root)
        (root / "scripts/zigux/genksyms.zig").unlink()
        missing = require_files(root)
        assert "scripts/zigux/genksyms.zig" in missing
        case_count += 1

    print("PHASE2_CROSS_SELF_TEST=pass")
    print(f"PHASE2_CROSS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 2 cross-target matrix packet and optionally replay one cross compile target."
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument("--target", help="Run cross-target Zig test replays for one configured target.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = require_files(ROOT)
    if missing:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_MISSING_FILES_START")
        for rel_path in missing:
            print(rel_path)
        print("PHASE2_CROSS_MISSING_FILES_END")
        return 1

    try:
        issues = collect_missing_markers(ROOT)
        issues.extend(validate_fixture(ROOT))
    except json.JSONDecodeError as exc:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_NOTE=invalid fixture JSON: {exc.msg}")
        return 1
    except ValueError as exc:
        print("PHASE2_CROSS=fail")
        print(f"PHASE2_CROSS_NOTE={exc}")
        return 1

    if issues:
        print("PHASE2_CROSS=fail")
        print("PHASE2_CROSS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE2_CROSS_ISSUES_END")
        return 1

    if args.target:
        return run_cross_compile(ROOT, args.target)

    payload = load_fixture(FIXTURE)
    targets = payload["targets"]
    print("PHASE2_CROSS=pass")
    print(f"PHASE2_CROSS_TARGET_COUNT={len(targets)}")
    print(f"PHASE2_CROSS_TARGETS={','.join(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
