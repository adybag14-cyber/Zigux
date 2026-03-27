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


def main() -> int:
    parser = argparse.ArgumentParser(description='Compile bounded Phase 2 Zigux tools for cross targets.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    parser.add_argument('--target', action='append', help='Explicit target triple to compile')
    args = parser.parse_args()

    zig = find_zig(args.zig)
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    targets_doc = json.loads(TARGETS.read_text(encoding='utf-8'))
    targets = args.target if args.target else targets_doc['targets']

    with tempfile.TemporaryDirectory(prefix='zigux_phase2_cross_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        for target in targets:
            for rel_tool in manifest['tools']:
                tool = ROOT / rel_tool
                output = tmp_dir / f"{target}_{tool.stem}"
                run([zig, 'build-exe', str(tool), '-target', target, '-femit-bin=' + str(output)], cwd=str(ROOT))

    print('PHASE2_CROSS=pass')
    print(f'PHASE2_CROSS_TARGET_COUNT={len(targets)}')
    print(f'PHASE2_CROSS_TOOL_COUNT={len(manifest["tools"])}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
