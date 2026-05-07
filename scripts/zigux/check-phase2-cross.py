#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
CROSS_PACKET = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json'


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    env = shutil.which('zig')
    if env:
        return env
    fallback = ROOT.parent / 'toolchains' / 'zig-master' / 'current' / 'zig.exe'
    if fallback.exists():
        return str(fallback)
    raise SystemExit('zig not found; pass --zig or add zig to PATH')


def reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    payload: dict[str, object] = {}
    for key, value in pairs:
        if key in payload:
            raise ValueError(f'duplicate_key:{key}')
        payload[key] = value
    return payload


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    try:
        payload = json.loads(
            path.read_text(encoding='utf-8'),
            object_pairs_hook=reject_duplicate_json_keys,
        )
    except ValueError as exc:
        raise SystemExit(f'{label}:{exc}') from exc
    if not isinstance(payload, dict):
        raise SystemExit(f'{label}:expected_object')
    return payload


def require_string_list(payload: dict[str, object], *, key: str, label: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise SystemExit(f'{label}:{key}:expected_list')
    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            raise SystemExit(f'{label}:{key}[{index}]:expected_nonempty_string')
        result.append(item)
    return result


def require_unique_strings(values: list[str], *, label: str) -> None:
    seen: set[str] = set()
    for item in values:
        if item in seen:
            raise SystemExit(f'{label}:duplicate:{item}')
        seen.add(item)


def load_cross_packet(path: Path) -> tuple[list[str], list[str]]:
    payload = load_json_object(path, label='phase2_cross_targets')
    if payload.get('phase') != 'Phase 2':
        raise SystemExit(f"phase2_cross_targets:phase:expected='Phase 2':actual={payload.get('phase')!r}")
    if payload.get('status') != 'closed':
        raise SystemExit(f"phase2_cross_targets:status:expected='closed':actual={payload.get('status')!r}")

    targets = require_string_list(payload, key='targets', label='phase2_cross_targets')
    require_unique_strings(targets, label='phase2_cross_targets:targets')
    declared_target_count = payload.get('target_count')
    if declared_target_count != len(targets):
        raise SystemExit(
            f'phase2_cross_targets:target_count_mismatch:{declared_target_count}:{len(targets)}'
        )

    tools = require_string_list(payload, key='tools', label='phase2_cross_targets')
    require_unique_strings(tools, label='phase2_cross_targets:tools')
    declared_tool_count = payload.get('tool_count')
    if declared_tool_count != len(tools):
        raise SystemExit(
            f'phase2_cross_targets:tool_count_mismatch:{declared_tool_count}:{len(tools)}'
        )
    return tools, targets


def resolve_targets(allowed_targets: list[str], requested_targets: list[str] | None) -> list[str]:
    if not requested_targets:
        return allowed_targets

    require_unique_strings(requested_targets, label='phase2_cross_requested_targets')
    unexpected = [target for target in requested_targets if target not in set(allowed_targets)]
    if unexpected:
        raise SystemExit(f'phase2_cross_requested_targets:unexpected:{unexpected[0]}')
    return requested_targets


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase2_cross_selftest_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        packet_path = tmp_dir / 'phase2_cross_targets.json'

        packet_path.write_text(
            json.dumps(
                {
                    'phase': 'Phase 2',
                    'status': 'closed',
                    'target_count': 3,
                    'targets': [
                        'x86_64-linux-musl',
                        'aarch64-linux-musl',
                        'riscv64-linux-musl',
                    ],
                    'tool_count': 2,
                    'tools': [
                        'scripts/zigux/fixdep.zig',
                        'scripts/zigux/genksyms.zig',
                    ],
                }
            ),
            encoding='utf-8',
        )

        tools, allowed_targets = load_cross_packet(packet_path)
        assert tools == [
            'scripts/zigux/fixdep.zig',
            'scripts/zigux/genksyms.zig',
        ]
        assert resolve_targets(allowed_targets, None) == allowed_targets
        assert resolve_targets(allowed_targets, ['aarch64-linux-musl']) == ['aarch64-linux-musl']

        packet_path.write_text(
            '{"phase":"Phase 2","status":"closed","target_count":3,"targets":["x86_64-linux-musl"],"targets":["riscv64-linux-musl"],"tool_count":2,"tools":["scripts/zigux/fixdep.zig","scripts/zigux/genksyms.zig"]}',
            encoding='utf-8',
        )
        try:
            load_cross_packet(packet_path)
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_targets:duplicate_key:targets'
        else:
            raise AssertionError('expected duplicate target key to fail')

        packet_path.write_text(
            json.dumps(
                {
                    'phase': 'Phase 2',
                    'status': 'closed',
                    'target_count': 3,
                    'targets': [
                        'x86_64-linux-musl',
                        'x86_64-linux-musl',
                        'riscv64-linux-musl',
                    ],
                    'tool_count': 2,
                    'tools': [
                        'scripts/zigux/fixdep.zig',
                        'scripts/zigux/genksyms.zig',
                    ],
                }
            ),
            encoding='utf-8',
        )
        try:
            load_cross_packet(packet_path)
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_targets:targets:duplicate:x86_64-linux-musl'
        else:
            raise AssertionError('expected duplicate manifest target to fail')

        packet_path.write_text(
            json.dumps(
                {
                    'phase': 'Phase 2',
                    'status': 'closed',
                    'target_count': 4,
                    'targets': [
                        'x86_64-linux-musl',
                        'aarch64-linux-musl',
                        'riscv64-linux-musl',
                    ],
                    'tool_count': 2,
                    'tools': [
                        'scripts/zigux/fixdep.zig',
                        'scripts/zigux/genksyms.zig',
                    ],
                }
            ),
            encoding='utf-8',
        )
        try:
            load_cross_packet(packet_path)
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_targets:target_count_mismatch:4:3'
        else:
            raise AssertionError('expected target-count drift to fail')

        packet_path.write_text(
            '{"phase":"Phase 2","status":"closed","target_count":3,"targets":["x86_64-linux-musl","aarch64-linux-musl","riscv64-linux-musl"],"tool_count":2,"tools":["scripts/zigux/fixdep.zig"],"tools":["scripts/zigux/genksyms.zig"]}',
            encoding='utf-8',
        )
        try:
            load_cross_packet(packet_path)
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_targets:duplicate_key:tools'
        else:
            raise AssertionError('expected duplicate tool key to fail')

        packet_path.write_text(
            json.dumps(
                {
                    'phase': 'Phase 2',
                    'status': 'closed',
                    'target_count': 3,
                    'targets': [
                        'x86_64-linux-musl',
                        'aarch64-linux-musl',
                        'riscv64-linux-musl',
                    ],
                    'tool_count': 2,
                    'tools': [
                        'scripts/zigux/fixdep.zig',
                        'scripts/zigux/fixdep.zig',
                    ],
                }
            ),
            encoding='utf-8',
        )
        try:
            load_cross_packet(packet_path)
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_targets:tools:duplicate:scripts/zigux/fixdep.zig'
        else:
            raise AssertionError('expected duplicate manifest tool to fail')

        packet_path.write_text(
            json.dumps(
                {
                    'phase': 'Phase 2',
                    'status': 'closed',
                    'target_count': 3,
                    'targets': [
                        'x86_64-linux-musl',
                        'aarch64-linux-musl',
                        'riscv64-linux-musl',
                    ],
                    'tool_count': 3,
                    'tools': [
                        'scripts/zigux/fixdep.zig',
                        'scripts/zigux/genksyms.zig',
                    ],
                }
            ),
            encoding='utf-8',
        )
        try:
            load_cross_packet(packet_path)
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_targets:tool_count_mismatch:3:2'
        else:
            raise AssertionError('expected tool-count drift to fail')

        try:
            resolve_targets(
                ['x86_64-linux-musl', 'aarch64-linux-musl'],
                ['x86_64-linux-musl', 'x86_64-linux-musl'],
            )
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_requested_targets:duplicate:x86_64-linux-musl'
        else:
            raise AssertionError('expected duplicate explicit target to fail')

        try:
            resolve_targets(
                ['x86_64-linux-musl', 'aarch64-linux-musl'],
                ['riscv64-linux-musl'],
            )
        except SystemExit as exc:
            assert str(exc) == 'phase2_cross_requested_targets:unexpected:riscv64-linux-musl'
        else:
            raise AssertionError('expected unexpected explicit target to fail')

    print('PHASE2_CROSS_SELF_TEST=pass')
    print('PHASE2_CROSS_SELF_TEST_CASE_COUNT=9')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Compile bounded Phase 2 Zigux tools for cross targets.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    parser.add_argument('--target', action='append', help='Explicit target triple to compile')
    parser.add_argument(
        '--self-test',
        action='store_true',
        help='Run built-in packet and target validation coverage without compiling.',
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = find_zig(args.zig)
    tools, allowed_targets = load_cross_packet(CROSS_PACKET)
    targets = resolve_targets(allowed_targets, args.target)

    with tempfile.TemporaryDirectory(prefix='zigux_phase2_cross_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for target in targets:
            for rel_tool in tools:
                tool = ROOT / rel_tool
                output = tmp_dir / f"{target}_{tool.stem}"
                run([zig, 'build-exe', str(tool), '-target', target, '-femit-bin=' + str(output)], cwd=str(ROOT))

    print('PHASE2_CROSS=pass')
    print(f'PHASE2_CROSS_TARGET_COUNT={len(targets)}')
    print(f'PHASE2_CROSS_TOOL_COUNT={len(tools)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
