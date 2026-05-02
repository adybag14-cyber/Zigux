#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BUILD_PATH = ROOT / "zigux/tests/phase12_libbpf_only_build.zig"
NOTE_PATH = ROOT / "Documentation/zigux/phase12-libbpf-segment-survey.md"
MAKE_PATH = ROOT / "zigux/Makefile"

BUILD_MARKERS = [
    'phase12-libbpf-segment-survey-tests',
    'phase12-libbpf-reviewability-tests',
    'Run focused Phase 12 libbpf survey and reviewability tests',
    'phase12_libbpf_segments.zig',
    'phase12_libbpf_reviewability.zig',
    'test_step.dependOn(&run_phase12_libbpf_segments_tests.step);',
    'test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);',
]

MAKE_MARKERS = [
    'scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test',
    'scripts/zigux/check-phase12-libbpf-focused-replay.py',
]

NOTE_MARKERS = [
    'zigux/tests/phase12_libbpf_only_build.zig',
    'python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test',
    'python3 scripts/zigux/check-phase12-libbpf-focused-replay.py',
    'zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all',
    'focused libbpf-only replay',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def check_paths(build_path: Path, note_path: Path, make_path: Path) -> list[str]:
    missing: list[str] = []
    if not build_path.exists():
        missing.append(f'missing_file:{build_path.as_posix()}')
    if not note_path.exists():
        missing.append(f'missing_file:{note_path.as_posix()}')
    if not make_path.exists():
        missing.append(f'missing_file:{make_path.as_posix()}')
    if missing:
        return missing

    build_text = read_text(build_path)
    note_text = read_text(note_path)
    make_text = read_text(make_path)

    for marker in BUILD_MARKERS:
        if marker not in build_text:
            missing.append(f'build:{marker}')
    for marker in MAKE_MARKERS:
        if marker not in make_text:
            missing.append(f'make:{marker}')
    for marker in NOTE_MARKERS:
        if marker not in note_text:
            missing.append(f'note:{marker}')
    return missing


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build_self_test_tree(root: Path) -> None:
    write(
        root / 'zigux/tests/phase12_libbpf_only_build.zig',
        '\n'.join(BUILD_MARKERS) + '\n',
    )
    write(
        root / 'Documentation/zigux/phase12-libbpf-segment-survey.md',
        '\n'.join(NOTE_MARKERS) + '\n',
    )
    write(
        root / 'zigux/Makefile',
        '\n'.join(MAKE_MARKERS) + '\n',
    )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase12_libbpf_focused_replay_') as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_tree(root)
        missing = check_paths(
            root / 'zigux/tests/phase12_libbpf_only_build.zig',
            root / 'Documentation/zigux/phase12-libbpf-segment-survey.md',
            root / 'zigux/Makefile',
        )
        if missing:
            raise SystemExit('phase12-libbpf-focused-replay:self-test:unexpected_failures:' + ','.join(missing))

        build_self_test_tree(root)
        build_path = root / 'zigux/tests/phase12_libbpf_only_build.zig'
        build_path.write_text(build_path.read_text(encoding='utf-8').replace(BUILD_MARKERS[0], 'phase12-libbpf-segment-survey-test'), encoding='utf-8')
        missing = check_paths(
            build_path,
            root / 'Documentation/zigux/phase12-libbpf-segment-survey.md',
            root / 'zigux/Makefile',
        )
        if f'build:{BUILD_MARKERS[0]}' not in missing:
            raise SystemExit('phase12-libbpf-focused-replay:self-test:build_marker_detection')

        build_self_test_tree(root)
        note_path = root / 'Documentation/zigux/phase12-libbpf-segment-survey.md'
        note_path.write_text(note_path.read_text(encoding='utf-8').replace(NOTE_MARKERS[2], 'python3 scripts/zigux/check-phase12-focused-replay.py'), encoding='utf-8')
        missing = check_paths(
            root / 'zigux/tests/phase12_libbpf_only_build.zig',
            note_path,
            root / 'zigux/Makefile',
        )
        if f'note:{NOTE_MARKERS[2]}' not in missing:
            raise SystemExit('phase12-libbpf-focused-replay:self-test:note_marker_detection')

        build_self_test_tree(root)
        make_path = root / 'zigux/Makefile'
        make_path.write_text(make_path.read_text(encoding='utf-8').replace(MAKE_MARKERS[0], 'scripts/zigux/check-phase12-libbpf-focused-replay.py --phase12-self-test'), encoding='utf-8')
        missing = check_paths(
            root / 'zigux/tests/phase12_libbpf_only_build.zig',
            root / 'Documentation/zigux/phase12-libbpf-segment-survey.md',
            make_path,
        )
        if f'make:{MAKE_MARKERS[0]}' not in missing:
            raise SystemExit('phase12-libbpf-focused-replay:self-test:make_marker_detection')

        build_self_test_tree(root)
        note_path = root / 'Documentation/zigux/phase12-libbpf-segment-survey.md'
        note_path.unlink()
        missing = check_paths(
            root / 'zigux/tests/phase12_libbpf_only_build.zig',
            note_path,
            root / 'zigux/Makefile',
        )
        if 'missing_file:' + note_path.as_posix() not in missing:
            raise SystemExit('phase12-libbpf-focused-replay:self-test:missing_file_detection')

    print('PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST=pass')
    print('PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST_CASE_COUNT=5')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Check the focused Phase 12 libbpf-only replay packet.'
    )
    parser.add_argument('--self-test', action='store_true', help='Run a synthetic self-test.')
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    missing = check_paths(BUILD_PATH, NOTE_PATH, MAKE_PATH)
    if missing:
        print('PHASE12_LIBBPF_FOCUSED_REPLAY=fail')
        print('PHASE12_LIBBPF_FOCUSED_REPLAY_MISSING_START')
        for item in missing:
            print(item)
        print('PHASE12_LIBBPF_FOCUSED_REPLAY_MISSING_END')
        return 1

    print('PHASE12_LIBBPF_FOCUSED_REPLAY=pass')
    print(f'PHASE12_LIBBPF_FOCUSED_REPLAY_BUILD_MARKER_COUNT={len(BUILD_MARKERS)}')
    print(f'PHASE12_LIBBPF_FOCUSED_REPLAY_MAKE_MARKER_COUNT={len(MAKE_MARKERS)}')
    print(f'PHASE12_LIBBPF_FOCUSED_REPLAY_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
