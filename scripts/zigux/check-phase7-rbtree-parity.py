#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree.json"
HARNESS = ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree_c_harness.c"
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
SOURCE = ROOT / "lib" / "rbtree.c"
SELF_TEST_PAYLOAD_ENV = "PHASE7_RBTREE_PARITY_SELFTEST_PAYLOAD"


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ("gcc", "cc", "clang"):
        path = shutil.which(candidate)
        if path:
            return path
    raise FileNotFoundError("no C compiler found on PATH")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def write_host_shims(root: Path) -> None:
    asm_dir = root / "asm"
    asm_dir.mkdir(parents=True, exist_ok=True)
    (asm_dir / "types.h").write_text(
        "\n".join(
            [
                "#ifndef __ZIGUX_HOST_ASM_TYPES_H__",
                "#define __ZIGUX_HOST_ASM_TYPES_H__",
                "typedef signed char __s8;",
                "typedef unsigned char __u8;",
                "typedef signed short __s16;",
                "typedef unsigned short __u16;",
                "typedef signed int __s32;",
                "typedef unsigned int __u32;",
                "typedef signed long long __s64;",
                "typedef unsigned long long __u64;",
                "#endif",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (asm_dir / "posix_types.h").write_text(
        '#include <asm-generic/posix_types.h>\n', encoding="utf-8"
    )
    (asm_dir / "bitsperlong.h").write_text(
        '#define __BITS_PER_LONG (__CHAR_BIT__ * __SIZEOF_LONG__)\n',
        encoding="utf-8",
    )


def include_flags(shim_dir: Path) -> list[str]:
    return [
        "-I",
        str(shim_dir),
        "-I",
        str(ROOT / "tools" / "include"),
        "-I",
        str(ROOT / "tools" / "include" / "uapi"),
    ]


def validate_required_path(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"missing {label}: {path}")


def validate_required_paths(
    *,
    fixture: Path = FIXTURE,
    harness: Path = HARNESS,
    artifact_diff: Path = ARTIFACT_DIFF,
    source: Path = SOURCE,
) -> None:
    validate_required_path(fixture, "fixture")
    validate_required_path(harness, "harness")
    validate_required_path(artifact_diff, "artifact diff tool")
    validate_required_path(source, "source")


def compile_and_run(
    exe: Path,
    actual: Path,
    compiler: str,
    flags: list[str],
    *,
    harness: Path = HARNESS,
    source: Path = SOURCE,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
) -> None:
    compile_cmd = [
        compiler,
        "-std=gnu11",
        "-Wall",
        "-Wextra",
        "-Wno-type-limits",
        "-Wno-int-to-pointer-cast",
        "-Wno-pointer-to-int-cast",
        "-o",
        str(exe),
    ]
    compile_cmd.extend(flags)
    compile_cmd.extend([str(harness), str(source)])
    run(compile_cmd, cwd=str(cwd), env=env)
    result = run([str(exe)], cwd=str(cwd), capture_output=True, env=env)
    actual.write_text(result.stdout, encoding="utf-8")


def write_fake_compiler(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import os\n"
        "import sys\n"
        "out = Path(sys.argv[sys.argv.index('-o') + 1])\n"
        f"payload = os.environ[{SELF_TEST_PAYLOAD_ENV!r}]\n"
        "out.write_text(\n"
        "    '#!/usr/bin/env python3\\n'\n"
        "    'import sys\\n'\n"
        "    'sys.stdout.write(' + repr(payload) + ')\\n',\n"
        "    encoding='utf-8',\n"
        ")\n"
        "out.chmod(0o755)\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def write_fake_artifact_diff(path: Path) -> None:
    path.write_text(
        "#!/usr/bin/env python3\n"
        "from pathlib import Path\n"
        "import sys\n"
        "lhs = Path(sys.argv[-2]).read_text(encoding='utf-8')\n"
        "rhs = Path(sys.argv[-1]).read_text(encoding='utf-8')\n"
        "raise SystemExit(0 if lhs == rhs else 1)\n",
        encoding="utf-8",
    )
    path.chmod(0o755)


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_selftest_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        fixture = tmp_dir / "expected.json"
        harness = tmp_dir / "fixture.c"
        source = tmp_dir / "source.c"
        fake_compiler = tmp_dir / "fake-cc"
        fake_artifact_diff = tmp_dir / "artifact_diff.py"
        payload = '{"selftest":{"ordered":true}}\n'
        fixture.write_text(payload, encoding="utf-8")
        harness.write_text("/* self-test fixture */\n", encoding="utf-8")
        source.write_text("/* self-test source */\n", encoding="utf-8")
        write_fake_compiler(fake_compiler)
        write_fake_artifact_diff(fake_artifact_diff)

        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)
        env = os.environ.copy()
        env[SELF_TEST_PAYLOAD_ENV] = payload

        validate_required_paths(
            fixture=fixture,
            harness=harness,
            artifact_diff=fake_artifact_diff,
            source=source,
        )

        exe = tmp_dir / "phase7_rbtree_selftest"
        actual = tmp_dir / "actual.json"
        compile_and_run(
            exe,
            actual,
            str(fake_compiler),
            include_flags(shim_dir),
            harness=harness,
            source=source,
            cwd=tmp_dir,
            env=env,
        )
        run(
            [sys.executable, str(fake_artifact_diff), "--mode", "json", str(fixture), str(actual)],
            cwd=str(tmp_dir),
            env=env,
        )

        drift_exe = tmp_dir / "phase7_rbtree_selftest_drift"
        drift_actual = tmp_dir / "drift.json"
        env[SELF_TEST_PAYLOAD_ENV] = '{"selftest":{"ordered":false}}\n'
        compile_and_run(
            drift_exe,
            drift_actual,
            str(fake_compiler),
            include_flags(shim_dir),
            harness=harness,
            source=source,
            cwd=tmp_dir,
            env=env,
        )
        drift_result = subprocess.run(
            [sys.executable, str(fake_artifact_diff), "--mode", "json", str(fixture), str(drift_actual)],
            cwd=str(tmp_dir),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        if drift_result.returncode == 0:
            raise SystemExit("phase7-rbtree-parity-self-test:drift_not_detected")

        fixture.unlink()
        try:
            validate_required_paths(
                fixture=fixture,
                harness=harness,
                artifact_diff=fake_artifact_diff,
                source=source,
            )
        except FileNotFoundError as exc:
            if str(exc) != f"missing fixture: {fixture}":
                raise SystemExit(
                    "phase7-rbtree-parity-self-test:missing_fixture_guard_shape"
                ) from exc
        else:
            raise SystemExit(
                "phase7-rbtree-parity-self-test:missing_fixture_guard_not_detected"
            )

        fixture.write_text(payload, encoding="utf-8")
        fake_artifact_diff.unlink()
        try:
            validate_required_paths(
                fixture=fixture,
                harness=harness,
                artifact_diff=fake_artifact_diff,
                source=source,
            )
        except FileNotFoundError as exc:
            if str(exc) != f"missing artifact diff tool: {fake_artifact_diff}":
                raise SystemExit(
                    "phase7-rbtree-parity-self-test:missing_artifact_diff_guard_shape"
                ) from exc
        else:
            raise SystemExit(
                "phase7-rbtree-parity-self-test:missing_artifact_diff_guard_not_detected"
            )

    print("PHASE7_RBTREE_PARITY_SELF_TEST=pass")
    print("PHASE7_RBTREE_PARITY_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate and check the Phase 7 rbtree parity fixture."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh the committed JSON fixture from the C harness.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Exercise the checker with a synthetic no-compiler fixture.",
    )
    parser.add_argument("--cc", help="Explicit C compiler path to use.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        validate_required_paths()
    except FileNotFoundError as exc:
        print("PHASE7_RBTREE_PARITY=fail")
        print(str(exc))
        return 1

    compiler = find_compiler(args.cc)

    with tempfile.TemporaryDirectory(prefix="zigux_phase7_rbtree_parity_") as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        shim_dir = tmp_dir / "shim"
        write_host_shims(shim_dir)

        exe = tmp_dir / "phase7_rbtree_c_harness"
        actual = tmp_dir / "phase7_rbtree.actual.json"

        compile_and_run(exe, actual, compiler, include_flags(shim_dir))

        if args.refresh:
            FIXTURE.write_text(actual.read_text(encoding="utf-8"), encoding="utf-8")
            print("PHASE7_RBTREE_PARITY_REFRESH=pass")
            print(f"FIXTURE={FIXTURE}")
            return 0

        diff_cmd = [
            sys.executable,
            str(ARTIFACT_DIFF),
            "--mode",
            "json",
            str(FIXTURE),
            str(actual),
        ]
        run(diff_cmd, cwd=str(ROOT))
        print("PHASE7_RBTREE_PARITY=pass")
        print(f"FIXTURE={FIXTURE}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
