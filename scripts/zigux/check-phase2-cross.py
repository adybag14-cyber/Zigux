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


def compile_tools_for_targets(
    zig: str,
    tools: list[Path],
    targets: list[str],
    *,
    runner=run,
    work_root: Path | None = None,
) -> None:
    if work_root is None:
        with tempfile.TemporaryDirectory(prefix='zigux_phase2_cross_') as tmp_dir_str:
            compile_tools_for_targets(
                zig,
                tools,
                targets,
                runner=runner,
                work_root=Path(tmp_dir_str),
            )
        return

    for target in targets:
        for tool in tools:
            output = work_root / f'{target}_{tool.stem}'
            runner([zig, 'build-exe', str(tool), '-target', target, '-femit-bin=' + str(output)], cwd=str(ROOT))


def expect_system_exit(label: str, callback, expected_message: str) -> None:
    try:
        callback()
    except SystemExit as exc:
        actual_message = str(exc)
        if actual_message != expected_message:
            raise SystemExit(
                f'phase2-cross:self-test:{label}:expected={expected_message!r}:actual={actual_message!r}'
            ) from exc
        return
    raise SystemExit(f'phase2-cross:self-test:{label}:missing_system_exit:{expected_message!r}')


def run_self_test() -> int:
    manifest = load_json_object(MANIFEST, label='tool')
    targets_doc = load_json_object(TARGETS, label='targets')

    tools = validate_tool_manifest(manifest)
    if len(tools) != manifest.get('tool_count'):
        raise SystemExit('phase2-cross:self-test:tool_count_round_trip')

    allowed_targets = validate_targets_manifest(targets_doc)
    if resolve_targets(None, allowed_targets) != allowed_targets:
        raise SystemExit('phase2-cross:self-test:default_target_selection')
    explicit_zig = '/tmp/zigux-phase2-cross-selftest-zig'
    if find_zig(explicit_zig) != explicit_zig:
        raise SystemExit('phase2-cross:self-test:explicit_zig_passthrough')

    explicit_targets = [allowed_targets[1], allowed_targets[0]]
    if resolve_targets(explicit_targets, allowed_targets) != explicit_targets:
        raise SystemExit('phase2-cross:self-test:explicit_target_selection')

    expect_system_exit(
        'duplicate_target',
        lambda: resolve_targets([allowed_targets[0], allowed_targets[0]], allowed_targets),
        f'phase2-cross:duplicate_target:{allowed_targets[0]}',
    )
    expect_system_exit(
        'unexpected_target',
        lambda: resolve_targets(['sparc64-linux-musl'], allowed_targets),
        'phase2-cross:unexpected_target:sparc64-linux-musl',
    )

    bad_manifest = dict(manifest)
    bad_manifest['tool_count'] = len(tools) + 1
    expect_system_exit(
        'tool_count_mismatch',
        lambda: validate_tool_manifest(bad_manifest),
        'phase2-cross:tool_count_mismatch',
    )

    duplicate_tool_manifest = dict(manifest)
    duplicate_tool_manifest['tools'] = [tools[0].relative_to(ROOT).as_posix(), tools[0].relative_to(ROOT).as_posix()]
    duplicate_tool_manifest['tool_count'] = 2
    expect_system_exit(
        'duplicate_tool',
        lambda: validate_tool_manifest(duplicate_tool_manifest),
        f'phase2-cross:duplicate_tool:{tools[0].relative_to(ROOT).as_posix()}',
    )

    missing_path_manifest = dict(manifest)
    missing_path_manifest['tools'] = ['scripts/zigux/missing_tool.zig']
    missing_path_manifest['tool_count'] = 1
    expect_system_exit(
        'tool_manifest_path_missing',
        lambda: validate_tool_manifest(missing_path_manifest),
        'phase2-cross:tool_manifest_path_missing:scripts/zigux/missing_tool.zig',
    )

    bad_targets = dict(targets_doc)
    bad_targets['target_count'] = len(allowed_targets) + 1
    expect_system_exit(
        'target_count_mismatch',
        lambda: validate_targets_manifest(bad_targets),
        'phase2-cross:target_count_mismatch',
    )

    duplicate_target_manifest = dict(targets_doc)
    duplicate_target_manifest['targets'] = [allowed_targets[0], allowed_targets[0]]
    duplicate_target_manifest['target_count'] = 2
    expect_system_exit(
        'duplicate_manifest_target',
        lambda: validate_targets_manifest(duplicate_target_manifest),
        f'phase2-cross:duplicate_manifest_target:{allowed_targets[0]}',
    )

    compile_attempts: list[list[str]] = []
    expected_tool = str(tools[0])
    expected_target = allowed_targets[0]

    def failing_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
        del kwargs
        compile_attempts.append(cmd)
        raise subprocess.CalledProcessError(1, cmd)

    with tempfile.TemporaryDirectory(prefix='zigux_phase2_cross_selftest_') as tmp_dir_str:
        try:
            compile_tools_for_targets(
                'zig',
                [tools[0]],
                [expected_target],
                runner=failing_run,
                work_root=Path(tmp_dir_str),
            )
        except subprocess.CalledProcessError as exc:
            if not compile_attempts:
                raise SystemExit('phase2-cross:self-test:explicit_target_failure:no_compile_attempt') from exc
            attempted_cmd = compile_attempts[0]
            if expected_tool not in attempted_cmd or expected_target not in attempted_cmd:
                raise SystemExit(
                    'phase2-cross:self-test:explicit_target_failure:'
                    f'expected_tool={expected_tool!r}:expected_target={expected_target!r}:actual_cmd={attempted_cmd!r}'
                ) from exc
            if exc.cmd != attempted_cmd:
                raise SystemExit(
                    'phase2-cross:self-test:explicit_target_failure:'
                    f'expected_cmd={attempted_cmd!r}:actual_cmd={exc.cmd!r}'
                ) from exc
        else:
            raise SystemExit(
                'phase2-cross:self-test:explicit_target_failure:missing_called_process_error'
            )

    print('PHASE2_CROSS_SELF_TEST=pass')
    print('PHASE2_CROSS_SELF_TEST_CASE_COUNT=9')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Compile bounded Phase 2 Zigux tools for cross targets.')
    parser.add_argument('--zig', help='Explicit zig executable path')
    parser.add_argument('--self-test', action='store_true', help='Run built-in manifest, tool-selection, and target-selection checks')
    parser.add_argument('--target', action='append', help='Explicit target triple to compile')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    zig = find_zig(args.zig)
    manifest = load_json_object(MANIFEST, label='tool')
    targets_doc = load_json_object(TARGETS, label='targets')
    tools = validate_tool_manifest(manifest)
    allowed_targets = validate_targets_manifest(targets_doc)
    targets = resolve_targets(args.target, allowed_targets)
    compile_tools_for_targets(zig, tools, targets)

    print('PHASE2_CROSS=pass')
    print(f'PHASE2_CROSS_TARGET_COUNT={len(targets)}')
    print(f'PHASE2_CROSS_TOOL_COUNT={len(tools)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
