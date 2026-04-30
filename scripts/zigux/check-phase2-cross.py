#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_tool_manifest.json'
TARGETS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase2_cross_targets.json'
EXPECTED_PHASE = 'Phase 2'
EXPECTED_STATUS = 'closed'


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


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise SystemExit(f'phase2-cross:{label}_manifest_expected_object')
    return data


def validate_tool_manifest(manifest: dict[str, object]) -> list[Path]:
    if manifest.get('phase') != EXPECTED_PHASE:
        raise SystemExit('phase2-cross:tool_manifest_phase')
    if manifest.get('status') != EXPECTED_STATUS:
        raise SystemExit('phase2-cross:tool_manifest_status')

    tools = manifest.get('tools')
    if not isinstance(tools, list) or not tools:
        raise SystemExit('phase2-cross:tool_manifest_tools')
    if manifest.get('tool_count') != len(tools):
        raise SystemExit('phase2-cross:tool_count_mismatch')

    resolved_tools: list[Path] = []
    seen_tools: set[str] = set()
    for rel_tool in tools:
        if not isinstance(rel_tool, str) or not rel_tool:
            raise SystemExit('phase2-cross:tool_manifest_entry')
        if rel_tool in seen_tools:
            raise SystemExit(f'phase2-cross:duplicate_tool:{rel_tool}')
        seen_tools.add(rel_tool)

        tool_path = ROOT / rel_tool
        if not tool_path.exists():
            raise SystemExit(f'phase2-cross:tool_manifest_path_missing:{rel_tool}')
        resolved_tools.append(tool_path)

    return resolved_tools


def validate_targets_manifest(targets_doc: dict[str, object]) -> list[str]:
    if targets_doc.get('phase') != EXPECTED_PHASE:
        raise SystemExit('phase2-cross:targets_manifest_phase')
    if targets_doc.get('status') != EXPECTED_STATUS:
        raise SystemExit('phase2-cross:targets_manifest_status')

    targets = targets_doc.get('targets')
    if not isinstance(targets, list) or not targets:
        raise SystemExit('phase2-cross:targets_manifest_targets')
    if targets_doc.get('target_count') != len(targets):
        raise SystemExit('phase2-cross:target_count_mismatch')

    normalized_targets: list[str] = []
    seen_targets: set[str] = set()
    for target in targets:
        if not isinstance(target, str) or not target:
            raise SystemExit('phase2-cross:target_manifest_entry')
        if target in seen_targets:
            raise SystemExit(f'phase2-cross:duplicate_manifest_target:{target}')
        seen_targets.add(target)
        normalized_targets.append(target)

    return normalized_targets


def resolve_targets(explicit_targets: list[str] | None, allowed_targets: list[str]) -> list[str]:
    if not explicit_targets:
        return allowed_targets

    allowed = set(allowed_targets)
    selected: list[str] = []
    seen_targets: set[str] = set()
    unexpected_targets: list[str] = []

    for target in explicit_targets:
        if target in seen_targets:
            raise SystemExit(f'phase2-cross:duplicate_target:{target}')
        seen_targets.add(target)
        if target not in allowed:
            unexpected_targets.append(target)
            continue
        selected.append(target)

    if unexpected_targets:
        raise SystemExit('phase2-cross:unexpected_target:' + ','.join(unexpected_targets))

    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description='Compile bounded Phase 2 Zigux tools for cross targets.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    parser.add_argument('--target', action='append', help='Explicit target triple to compile')
    args = parser.parse_args()

    zig = find_zig(args.zig)
    manifest = load_json_object(MANIFEST, label='tool')
    targets_doc = load_json_object(TARGETS, label='targets')
    tools = validate_tool_manifest(manifest)
    allowed_targets = validate_targets_manifest(targets_doc)
    targets = resolve_targets(args.target, allowed_targets)

    with tempfile.TemporaryDirectory(prefix='zigux_phase2_cross_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for target in targets:
            for tool in tools:
                output = tmp_dir / f'{target}_{tool.stem}'
                run([zig, 'build-exe', str(tool), '-target', target, '-femit-bin=' + str(output)], cwd=str(ROOT))

    print('PHASE2_CROSS=pass')
    print(f'PHASE2_CROSS_TARGET_COUNT={len(targets)}')
    print(f'PHASE2_CROSS_TOOL_COUNT={len(tools)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
