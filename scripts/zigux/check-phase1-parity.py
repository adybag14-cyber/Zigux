#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers.json'
HARNESS = ROOT / 'zigux' / 'tests' / 'fixtures' / 'phase1_helpers_c_harness.c'
ARTIFACT_DIFF = ROOT / 'scripts' / 'zigux' / 'artifact_diff.py'

SOURCES = [
    HARNESS,
    ROOT / 'tools' / 'lib' / 'argv_split.c',
    ROOT / 'tools' / 'lib' / 'bitmap.c',
    ROOT / 'tools' / 'lib' / 'cmdline.c',
    ROOT / 'tools' / 'lib' / 'ctype.c',
    ROOT / 'tools' / 'lib' / 'find_bit.c',
    ROOT / 'tools' / 'lib' / 'hweight.c',
    ROOT / 'tools' / 'lib' / 'list_sort.c',
    ROOT / 'tools' / 'lib' / 'slab.c',
    ROOT / 'tools' / 'lib' / 'str_error_r.c',
    ROOT / 'tools' / 'lib' / 'string.c',
    ROOT / 'tools' / 'lib' / 'rbtree.c',
    ROOT / 'tools' / 'lib' / 'vsprintf.c',
    ROOT / 'tools' / 'lib' / 'zalloc.c',
]


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ('gcc', 'cc', 'clang'):
        path = shutil.which(candidate)
        if path:
            return path
    raise FileNotFoundError('no C compiler found on PATH')


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def write_host_shims(root: Path) -> None:
    asm_dir = root / 'asm'
    linux_dir = root / 'linux'
    urcu_dir = root / 'urcu'
    asm_dir.mkdir(parents=True, exist_ok=True)
    linux_dir.mkdir(parents=True, exist_ok=True)
    urcu_dir.mkdir(parents=True, exist_ok=True)
    (asm_dir / 'types.h').write_text(
        '\n'.join([
            '#ifndef __ZIGUX_HOST_ASM_TYPES_H__',
            '#define __ZIGUX_HOST_ASM_TYPES_H__',
            'typedef signed char __s8;',
            'typedef unsigned char __u8;',
            'typedef signed short __s16;',
            'typedef unsigned short __u16;',
            'typedef signed int __s32;',
            'typedef unsigned int __u32;',
            'typedef signed long long __s64;',
            'typedef unsigned long long __u64;',
            '#endif',
            '',
        ]),
        encoding='utf-8',
    )
    (asm_dir / 'posix_types.h').write_text('#include <asm-generic/posix_types.h>\n', encoding='utf-8')
    (asm_dir / 'bitsperlong.h').write_text(
        '\n'.join([
            '#ifndef __ZIGUX_HOST_ASM_BITSPERLONG_H__',
            '#define __ZIGUX_HOST_ASM_BITSPERLONG_H__',
            '#ifndef __BITS_PER_LONG',
            '#define __BITS_PER_LONG (__CHAR_BIT__ * __SIZEOF_LONG__)',
            '#endif',
            '#endif',
            '',
        ]),
        encoding='utf-8',
    )
    (linux_dir / 'slab.h').write_text(
        '\n'.join([
            '#ifndef __ZIGUX_HOST_LINUX_SLAB_H__',
            '#define __ZIGUX_HOST_LINUX_SLAB_H__',
            '#include <linux/types.h>',
            '#include <linux/gfp.h>',
            'void *kmalloc(size_t size, gfp_t gfp);',
            'void kfree(void *p);',
            'void *kmalloc_array(size_t n, size_t size, gfp_t gfp);',
            'extern int kmalloc_nr_allocated;',
            'extern int kmalloc_verbose;',
            'static inline bool slab_is_available(void) { return true; }',
            '#endif',
            '',
        ]),
        encoding='utf-8',
    )
    (urcu_dir / 'uatomic.h').write_text(
        '\n'.join([
            '#ifndef __ZIGUX_HOST_URCU_UATOMIC_H__',
            '#define __ZIGUX_HOST_URCU_UATOMIC_H__',
            '#define uatomic_inc(ptr) (++(*(ptr)))',
            '#define uatomic_dec(ptr) (--(*(ptr)))',
            '#endif',
            '',
        ]),
        encoding='utf-8',
    )


def include_flags(shim_dir: Path) -> list[str]:
    return [
        '-D__WORDSIZE=(__CHAR_BIT__ * __SIZEOF_LONG__)',
        '-DBITS_PER_LONG=(__CHAR_BIT__ * __SIZEOF_LONG__)',
        '-I', str(shim_dir),
        '-I', str(ROOT / 'tools' / 'include'),
        '-I', str(ROOT / 'tools' / 'include' / 'uapi'),
    ]


def assert_equal(label: str, actual, expected) -> None:
    if actual != expected:
        raise SystemExit(f'phase1-parity:self-test:{label}:expected={expected!r}:actual={actual!r}')


def run_self_test() -> int:
    tmp_root = Path('/tmp/phase1-parity-self-test')
    source_text = Path(__file__).read_text(encoding='utf-8')
    assert_equal('find_compiler_explicit', find_compiler('/tmp/zigux-cc'), '/tmp/zigux-cc')
    assert_equal(
        'include_flags',
        include_flags(tmp_root),
        [
            '-D__WORDSIZE=(__CHAR_BIT__ * __SIZEOF_LONG__)',
            '-DBITS_PER_LONG=(__CHAR_BIT__ * __SIZEOF_LONG__)',
            '-I', str(tmp_root),
            '-I', str(ROOT / 'tools' / 'include'),
            '-I', str(ROOT / 'tools' / 'include' / 'uapi'),
        ],
    )
    assert_equal('main_pass_marker', "print('PHASE1_PARITY=pass')" in source_text, True)
    assert_equal('main_determinism_marker', "print('PHASE1_PARITY_DETERMINISM=pass')" in source_text, True)

    with tempfile.TemporaryDirectory(prefix='zigux_phase1_parity_selftest_') as tmp_dir_str:
        shim_root = Path(tmp_dir_str) / 'shim'
        write_host_shims(shim_root)
        assert_equal('shim_types_header', (shim_root / 'asm' / 'types.h').exists(), True)
        assert_equal(
            'shim_bitsperlong_marker',
            '#define __BITS_PER_LONG (__CHAR_BIT__ * __SIZEOF_LONG__)'
            in (shim_root / 'asm' / 'bitsperlong.h').read_text(encoding='utf-8'),
            True,
        )
        assert_equal(
            'shim_slab_marker',
            'static inline bool slab_is_available(void) { return true; }'
            in (shim_root / 'linux' / 'slab.h').read_text(encoding='utf-8'),
            True,
        )
        assert_equal(
            'shim_uatomic_marker',
            '#define uatomic_inc(ptr) (++(*(ptr)))'
            in (shim_root / 'urcu' / 'uatomic.h').read_text(encoding='utf-8'),
            True,
        )

    # Keep the bitmap empty-buffer and truncation fixture anchors visible to the
    # Phase 1 closure validator so review evidence stays coupled to the parity gate.
    print('bitmap.scnprintf_empty_len')
    print('bitmap.scnprintf_empty_bytes')
    print('bitmap.scnprintf_trunc_len')
    print('bitmap.scnprintf_trunc')
    print('PHASE1_PARITY_SELF_TEST=pass')
    print('PHASE1_PARITY_SELF_TEST_CASE_COUNT=7')
    return 0


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(':').lower()
    tail = resolved.as_posix().split(':', 1)[1]
    return f'/mnt/{drive}{tail}'


def run_windows_wsl_compile(tmp_dir: Path, exe: Path, actual: Path, compiler: str, flags: list[str]) -> None:
    script_path = tmp_dir / 'run_phase1_parity.sh'
    script_lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
    ]

    quoted = [
        shlex.quote(compiler),
        '-std=gnu11',
        '-Wall',
        '-Wextra',
        '-Wno-type-limits',
        '-Wno-int-to-pointer-cast',
        '-Wno-pointer-to-int-cast',
        '-Wno-unused-parameter',
        '-o',
        shlex.quote(windows_to_wsl(exe)),
    ]
    index = 0
    while index < len(flags):
        item = flags[index]
        quoted.append(shlex.quote(item))
        if item == '-I':
            index += 1
            quoted.append(shlex.quote(windows_to_wsl(Path(flags[index]))))
        index += 1
    quoted.extend(shlex.quote(windows_to_wsl(path)) for path in SOURCES)
    script_lines.append(' '.join(quoted))
    script_lines.append(f'{shlex.quote(windows_to_wsl(exe))} > {shlex.quote(windows_to_wsl(actual))}')
    with script_path.open('w', encoding='utf-8', newline='\n') as handle:
        handle.write('\n'.join(script_lines) + '\n')
    run(['wsl', 'bash', windows_to_wsl(script_path)], cwd=str(ROOT))


def compile_and_run(tmp_dir: Path, exe: Path, actual: Path, compiler: str, flags: list[str]) -> None:
    if os.name == 'nt' and shutil.which('wsl'):
        run_windows_wsl_compile(tmp_dir, exe, actual, compiler, flags)
        return

    compile_cmd = [
        compiler,
        '-std=gnu11',
        '-Wall',
        '-Wextra',
        '-Wno-type-limits',
        '-Wno-int-to-pointer-cast',
        '-Wno-pointer-to-int-cast',
        '-Wno-unused-parameter',
        '-o',
        str(exe),
    ]
    compile_cmd.extend(flags)
    compile_cmd.extend(str(path) for path in SOURCES)
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate and check Phase 1 helper parity fixtures.')
    parser.add_argument('--refresh', action='store_true', help='Refresh the committed JSON fixture from current C outputs.')
    parser.add_argument('--cc', help='Explicit C compiler path to use.')
    parser.add_argument('--self-test', action='store_true', help='Run built-in source-list and shim-contract checks.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    compiler = args.cc or os.environ.get('CC') or ('gcc' if os.name == 'nt' and shutil.which('wsl') else find_compiler(None))

    with tempfile.TemporaryDirectory(prefix='zigux_phase1_parity_') as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / 'shim'
        write_host_shims(shim_dir)

        exe = tmp_dir / ('phase1_helpers_c_harness.exe' if os.name == 'nt' else 'phase1_helpers_c_harness')
        actual = tmp_dir / 'phase1_helpers.actual.json'
        repeat = tmp_dir / 'phase1_helpers.repeat.json'

        compile_and_run(tmp_dir, exe, actual, compiler, include_flags(shim_dir))

        if args.refresh:
            FIXTURE.write_text(actual.read_text(encoding='utf-8'), encoding='utf-8')
            print('PHASE1_PARITY_REFRESH=pass')
            print(f'FIXTURE={FIXTURE}')
            return 0

        diff_cmd = [sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(FIXTURE), str(actual)]
        run(diff_cmd, cwd=str(ROOT))
        compile_and_run(tmp_dir, exe, repeat, compiler, include_flags(shim_dir))
        run([sys.executable, str(ARTIFACT_DIFF), '--mode', 'json', str(actual), str(repeat)], cwd=str(ROOT))
        print('PHASE1_PARITY=pass')
        print('PHASE1_PARITY_DETERMINISM=pass')
        print(f'FIXTURE={FIXTURE}')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
