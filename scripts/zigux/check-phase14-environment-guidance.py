#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

MARKERS = {
    "scripts/zigux/README.md": [
        "Phase 14 flow",
        "`make -C zigux phase14-validate`",
        "`make -C zigux phase14-smoke`",
        "`make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`",
        "`make -C zigux phase14-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase14-test ZIG=<attached-zig-path>`",
        "`make -C zigux phase14 ZIG=<attached-zig-path>`",
        "when `zig` is not on `PATH`",
    ],
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md": [
        "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate",
        "PHASE14_ATTACHED_TOOLCHAIN_FALLBACK=ZIG=<attached-zig-path>",
        "make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>",
        "make -C zigux phase14-smoke ZIG=<attached-zig-path>",
        "make -C zigux phase14-test ZIG=<attached-zig-path>",
        "make -C zigux phase14 ZIG=<attached-zig-path>",
    ],
    "zigux/tests/phase14_end_to_end_smoke_manifest.json": [
        "\"attached_toolchain_commands\"",
        "make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>",
        "make -C zigux phase14-smoke ZIG=<attached-zig-path>",
        "make -C zigux phase14-test ZIG=<attached-zig-path>",
        "make -C zigux phase14 ZIG=<attached-zig-path>",
    ],
    "zigux/Makefile": [
        "PYTHON ?= python3",
        "ZIG ?= zig",
        "phase14-validate:",
        "phase14-smoke:",
        "phase14-test:",
        "phase14: phase14-validate phase14-test",
    ],
    "scripts/zigux/validate-phase14.py": [
        "attached_toolchain_commands",
        "`make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>`",
        "`make -C zigux phase14-smoke ZIG=<attached-zig-path>`",
        "`make -C zigux phase14-test ZIG=<attached-zig-path>`",
        "`make -C zigux phase14 ZIG=<attached-zig-path>`",
        "when `zig` is not on `PATH`",
    ],
}


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def check_root(root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path, markers in MARKERS.items():
        path = root / relative_path
        if not path.exists():
            missing.append(f"missing:{relative_path}")
            continue
        content = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in content:
                missing.append(f"marker:{relative_path}:{marker}")
    return missing


def run_self_test() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="phase14-env-guidance-"))
    try:
        for relative_path, markers in MARKERS.items():
            path = temp_root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("\n".join(markers) + "\n", encoding="utf-8")
        missing = check_root(temp_root)
        if missing:
            print("PHASE14_ENV_GUIDANCE_SELF_TEST=fail")
            for item in missing:
                print(item)
            return 1
        print("PHASE14_ENV_GUIDANCE_SELF_TEST=pass")
        print(f"PHASE14_ENV_GUIDANCE_FILE_COUNT={len(MARKERS)}")
        print(f"PHASE14_ENV_GUIDANCE_MARKER_COUNT={sum(len(markers) for markers in MARKERS.values())}")
        return 0
    finally:
        shutil.rmtree(temp_root)


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--self-test":
        return run_self_test()
    if len(argv) != 1:
        print("usage: check-phase14-environment-guidance.py [--self-test]", file=sys.stderr)
        return 2

    missing = check_root(ROOT)
    if missing:
        print("PHASE14_ENV_GUIDANCE=fail")
        print("MISSING_PHASE14_ENV_GUIDANCE_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE14_ENV_GUIDANCE_MARKERS_END")
        return 1

    print("PHASE14_ENV_GUIDANCE=pass")
    print(f"PHASE14_ENV_GUIDANCE_FILE_COUNT={len(MARKERS)}")
    print(f"PHASE14_ENV_GUIDANCE_MARKER_COUNT={sum(len(markers) for markers in MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
