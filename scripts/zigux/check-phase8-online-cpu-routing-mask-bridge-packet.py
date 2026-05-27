#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path


def _default_root() -> Path:
    resolved = Path(__file__).resolve()
    if len(resolved.parents) >= 3:
        return resolved.parents[2]
    return resolved.parent


ROOT = _default_root()
SURVEY = Path("Documentation/zigux/phase8-libbpf-segment-survey.md")
HELPER = Path("tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig")
VERIFY = Path("tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig")
BUILD = Path("zigux/tests/phase8_online_cpu_routing_mask_bridge_only_build.zig")

REQUIRED_FILES = (
    SURVEY,
    HELPER,
    VERIFY,
    BUILD,
)

FILE_MARKERS: dict[Path, tuple[str, ...]] = {
    SURVEY: (
        "`tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge.zig`",
        "`tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig`",
        "cpu-mask-backed helper-local routing bridges below the still-deferred setup-side routing boundary.",
        "online-CPU mask-bridge next-route CPU-index and buffer-FD wrappers",
    ),
    HELPER: (
        "pub fn summarizeNextOnlineCpuRouteFromString(",
        "pub fn summarizeNextOnlineCpuRouteFromReader(",
        "pub fn summarizeOnlineCpuRoutingFromString(",
        "pub fn summarizeOnlineCpuRoutingFromReader(",
        "pub fn resolveNextOnlineCpuRouteCpuIndexFromString(",
        "pub fn resolveNextOnlineCpuRouteCpuIndexReturnFromReader(",
        "pub fn resolveNextOnlineCpuRouteBufferFdFromString(",
        "pub fn resolveNextOnlineCpuRouteBufferFdReturnFromReader(",
    ),
    VERIFY: (
        'test "phase8 online-cpu routing mask bridge entrypoints stay explicit" {',
        'test "phase8 online-cpu routing mask bridge keeps typed direct wrappers stable" {',
        'test "phase8 online-cpu routing mask bridge keeps route failures explicit across mask-backed wrappers" {',
        'test "phase8 online-cpu routing mask bridge keeps malformed mask inputs fail-closed" {',
        "resolveNextOnlineCpuRouteCpuIndexFromReader(",
        "resolveNextOnlineCpuRouteBufferFdReturnFromReader(",
    ),
    BUILD: (
        "../../tools/lib/bpf/zigux_segments/online_cpu_routing_mask_bridge_verify.zig",
        "phase8-online-cpu-routing-mask-bridge-tests",
        'b.step("test", "Run focused Phase 8 online-cpu routing mask-bridge tests.")',
    ),
}


@dataclass
class ValidationResult:
    missing_files: list[str]
    missing_markers: list[str]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_root(root: Path) -> ValidationResult:
    missing_files = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    missing_markers: list[str] = []
    for relative_path, markers in FILE_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            continue
        text = _read(path)
        for marker in markers:
            if marker not in text:
                missing_markers.append(f"{relative_path}:{marker}")
    return ValidationResult(missing_files=missing_files, missing_markers=missing_markers)


def emit_result(result: ValidationResult) -> int:
    if result.missing_files or result.missing_markers:
        print("PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET=fail")
        if result.missing_files:
            print("PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_MISSING_FILES_START")
            for item in result.missing_files:
                print(item)
            print("PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_MISSING_FILES_END")
        if result.missing_markers:
            print("PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_MISSING_MARKERS_START")
            for item in result.missing_markers:
                print(item)
            print("PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_MISSING_MARKERS_END")
        return 1
    print("PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET=pass")
    print(f"PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_MARKER_COUNT="
        f"{sum(len(markers) for markers in FILE_MARKERS.values())}"
    )
    return 0


def _passing_fixture(root: Path) -> None:
    for path, markers in FILE_MARKERS.items():
        _write(root / path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase8-online-cpu-routing-mask-bridge-") as tmp:
        root = Path(tmp)
        _passing_fixture(root)

        result = validate_root(root)
        if result.missing_files or result.missing_markers:
            raise AssertionError("expected passing fixture to validate")
        case_count += 1

        for relative_path, markers in FILE_MARKERS.items():
            original = _read(root / relative_path)
            for marker in markers:
                _write(root / relative_path, original.replace(marker, "", 1))
                result = validate_root(root)
                expected = f"{relative_path}:{marker}"
                if expected not in result.missing_markers:
                    raise AssertionError(f"expected missing marker to be reported: {expected}")
                _write(root / relative_path, original)
                case_count += 1

        for relative_path in REQUIRED_FILES:
            original = _read(root / relative_path)
            (root / relative_path).unlink()
            result = validate_root(root)
            if relative_path.as_posix() not in result.missing_files:
                raise AssertionError(f"expected missing file to be reported: {relative_path}")
            _write(root / relative_path, original)
            case_count += 1

    print("PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_SELF_TEST=pass")
    print(f"PHASE8_ONLINE_CPU_ROUTING_MASK_BRIDGE_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    return emit_result(validate_root(args.root))


if __name__ == "__main__":
    raise SystemExit(main())
