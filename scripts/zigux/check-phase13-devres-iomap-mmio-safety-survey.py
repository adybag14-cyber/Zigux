#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase13-devres-iomap-mmio-safety-survey.md")
MMIO_HELPER_PATH = Path("zigux/helpers/mmio.zig")
WRAPPER_REPLAY_PATH = Path("zigux/tests/phase3_low_level_wrappers.zig")
DEVRES_HELPER_PATH = Path("lib/devres.zig")
IOMAP_PLANNER_NOTE_PATH = Path("Documentation/zigux/phase13-devres-iomap-planner.md")
IOMAP_PLANNER_REPLAY_PATH = Path("zigux/tests/phase13_devres_iomap_planner.zig")

REQUIRED_MARKERS = {
    NOTE_PATH: [
        "shared MMIO safety substrate in `zigux/helpers/mmio.zig`",
        "`unsafe_scope = 1` with `reserved = 0` is the allowed volatile-MMIO byte-policy form",
        "`unsafe_scope = 0` is denied with `error.UnsafeScopeDenied`",
        "`unsafe_scope = 2` is denied for MMIO",
        "non-zero reserved byte is rejected as `error.InvalidInteropPolicy`",
        "denied MMIO writes stay side-effect free",
        "the shipped helper descriptor in `lib/devres.zig` keeps `.touches_live_mmio = false`",
        "the shared MMIO helper owns the actual volatile-MMIO access gate",
    ],
    MMIO_HELPER_PATH: [
        "pub fn allowsInteropPolicyBytes",
        "pub fn requireInteropPolicyBytes",
        "pub fn readScoped",
        "pub fn writeScoped",
        "pub fn readInteropPolicyBytes",
        "pub fn writeInteropPolicyBytes",
        "pub fn exchangeInteropPolicyBytes",
        "pub fn writeMaskedInteropPolicyBytes",
    ],
    WRAPPER_REPLAY_PATH: [
        "phase3 low-level wrappers keep MMIO unsafe-scope gates explicit across shared handoff",
        "phase3 low-level wrappers keep MMIO byte-policy shorthand aligned with reserved-byte gates",
        "phase3 low-level wrappers keep MMIO single-byte interop-policy shorthands explicit",
        "phase3 low-level wrappers keep whole-record MMIO interop-policy helpers explicit",
        "phase3 low-level wrappers keep direct MMIO scope gates explicit",
        "expectError(error.UnsafeScopeDenied, mmio.writeInteropPolicyBytes(u32, 0, 0, register_ptr, state))",
        "expectError(error.InvalidInteropPolicy, mmio.readInteropPolicyBytes(u32, 1, 1, const_register_ptr))",
        "try mmio.writeInteropPolicyBytes(u32, 1, 0, register_ptr, state)",
        "expectError(error.UnsafeScopeDenied, mmio.writeScoped(u32, raw_scope, register_ptr, 0xAABB_CCDD))",
    ],
    DEVRES_HELPER_PATH: [
        ".touches_live_mmio = false",
        ".provides_of_iomap_planning = true",
        "pub fn planDeviceTreeIomap",
    ],
    IOMAP_PLANNER_NOTE_PATH: [
        "pure `devm_of_iomap()` planning surface",
        "does not claim live MMIO mapping state",
    ],
    IOMAP_PLANNER_REPLAY_PATH: [
        "phase13 devres iomap planning stops before managed ioremap resource when translation is missing",
        "phase13 devres iomap planning preserves translated size on request-region denial",
        "phase13 devres iomap planning releases the requested region when remap later fails",
        "phase13 devres iomap cleanup handoff materializes helper-first iounmap cleanup after successful remap",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    for rel in REQUIRED_MARKERS:
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel.as_posix()}")
    if issues:
        return issues

    for rel, markers in REQUIRED_MARKERS.items():
        text = read_text(root / rel)
        for marker in markers:
            if marker not in text:
                issues.append(f"{rel.as_posix()}:missing_marker:{marker}")
    return issues


def seed_fixture_tree(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        write_text(root / rel, "\n".join(markers) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase13-devres-iomap-mmio-safety-") as tmp:
        root = Path(tmp)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        (root / NOTE_PATH).unlink()
        assert_only(
            validate(root),
            [f"missing_file:{NOTE_PATH.as_posix()}"],
            "missing_note_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / NOTE_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[NOTE_PATH]
                if marker != "`unsafe_scope = 2` is denied for MMIO"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "Documentation/zigux/phase13-devres-iomap-mmio-safety-survey.md:missing_marker:`unsafe_scope = 2` is denied for MMIO",
            ],
            "missing_scope_two_note_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / WRAPPER_REPLAY_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[WRAPPER_REPLAY_PATH]
                if marker != "expectError(error.InvalidInteropPolicy, mmio.readInteropPolicyBytes(u32, 1, 1, const_register_ptr))"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                "zigux/tests/phase3_low_level_wrappers.zig:missing_marker:expectError(error.InvalidInteropPolicy, mmio.readInteropPolicyBytes(u32, 1, 1, const_register_ptr))",
            ],
            "missing_reserved_gate_replay_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / DEVRES_HELPER_PATH,
            "\n".join(
                marker
                for marker in REQUIRED_MARKERS[DEVRES_HELPER_PATH]
                if marker != ".touches_live_mmio = false"
            )
            + "\n",
        )
        assert_only(
            validate(root),
            ["lib/devres.zig:missing_marker:.touches_live_mmio = false"],
            "missing_devres_mmio_boundary_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_IOMAP_MMIO_SAFETY_SURVEY_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_IOMAP_MMIO_SAFETY_SURVEY_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        for issue in issues:
            print(issue)
        print("PHASE13_DEVRES_IOMAP_MMIO_SAFETY_SURVEY=fail")
        return 1

    print("PHASE13_DEVRES_IOMAP_MMIO_SAFETY_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
