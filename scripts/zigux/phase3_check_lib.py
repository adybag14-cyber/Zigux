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

from phase3_catalog import build_step_for_slug, description_for_slug


ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIFF = ROOT / "scripts" / "zigux" / "artifact_diff.py"
SCRIPT_PREFIX = "check-phase3-"
PHASE3_PREFLIGHT_SCRIPTS = {
    "abi": (
        "scripts/zigux/validate-phase3-abi-bindings-syntax.py",
        "scripts/zigux/survey-phase3-abi-constant-parity.py",
    ),
}

WRAPPER_STUB = """#!/usr/bin/env python3
from __future__ import annotations

from phase3_check_lib import run_from_wrapper


if __name__ == \"__main__\":
    raise SystemExit(run_from_wrapper(__file__))
"""


def render_wrapper_stub() -> str:
    return WRAPPER_STUB


def slug_from_wrapper_path(path: str | Path) -> str:
    name = Path(path).name
    if not name.startswith(SCRIPT_PREFIX) or not name.endswith(".py"):
        raise SystemExit(f"unsupported Phase 3 wrapper path: {path}")
    return name[len(SCRIPT_PREFIX) : -3]


def fixture_key_for_slug(slug: str) -> str:
    return f"phase3_{slug.replace('-', '_')}"


def status_name_for_slug(slug: str) -> str:
    return f"PHASE3_{slug.replace('-', '_').upper()}_DIFF"


def shared_runner_gate_for_slug(slug: str) -> str:
    return f"PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug {slug}"


def legacy_wrapper_gate_for_slug(slug: str) -> str:
    return f"PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-{slug}.py"


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, **kwargs)


def parse_phase3_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--cc", help="Explicit C compiler path")
    parser.add_argument("--zig", help="Explicit zig executable path")
    return parser.parse_args(argv)


def find_compiler(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in ("gcc", "cc", "clang"):
        path = shutil.which(candidate)
        if path:
            return path
    raise SystemExit("no C compiler found; pass --cc or add gcc/cc/clang to PATH")


def find_zig(explicit: str | None) -> str:
    if explicit:
        return explicit
    path = shutil.which("zig")
    if path:
        return path
    fallback = ROOT.parent / "toolchains" / "zig-master" / "current" / "zig.exe"
    if fallback.exists():
        return str(fallback)
    raise SystemExit("zig not found; pass --zig or add zig to PATH")


def preflight_scripts_for_slug(slug: str) -> tuple[Path, ...]:
    return tuple(ROOT / rel for rel in PHASE3_PREFLIGHT_SCRIPTS.get(slug, ()))


def run_slug_preflights(slug: str) -> None:
    for script in preflight_scripts_for_slug(slug):
        run([sys.executable, str(script)], cwd=str(ROOT))


def windows_to_wsl(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":").lower()
    tail = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive}{tail}"


def compile_and_run_c(tmp_dir: Path, compiler: str, harness: Path, actual: Path, fixture_key: str) -> None:
    exe = tmp_dir / (f"{fixture_key}_c_harness.exe" if os.name == "nt" else f"{fixture_key}_c_harness")
    flags = ["-I", str(ROOT / "include")]

    if os.name == "nt" and shutil.which("wsl"):
        script_path = tmp_dir / f"run_{fixture_key}_c.sh"
        quoted = [shlex.quote(compiler), "-std=gnu11", "-Wall", "-Wextra", "-o", shlex.quote(windows_to_wsl(exe))]
        index = 0
        while index < len(flags):
            item = flags[index]
            quoted.append(shlex.quote(item))
            if item == "-I":
                index += 1
                quoted.append(shlex.quote(windows_to_wsl(Path(flags[index]))))
            index += 1
        quoted.append(shlex.quote(windows_to_wsl(harness)))
        script = "\n".join(
            [
                "#!/usr/bin/env bash",
                "set -euo pipefail",
                " ".join(quoted),
                f"{shlex.quote(windows_to_wsl(exe))} > {shlex.quote(windows_to_wsl(actual))}",
                "",
            ]
        )
        script_path.write_text(script, encoding="utf-8", newline="\n")
        run(["wsl", "bash", windows_to_wsl(script_path)], cwd=str(ROOT))
        return

    compile_cmd = [compiler, "-std=gnu11", "-Wall", "-Wextra", "-o", str(exe)]
    compile_cmd.extend(flags)
    compile_cmd.append(str(harness))
    run(compile_cmd, cwd=str(ROOT))
    result = run([str(exe)], cwd=str(ROOT), capture_output=True)
    actual.write_text(result.stdout, encoding="utf-8", newline="\n")


def compile_and_run_zig(zig: str, build_step: str, actual: Path) -> None:
    env = os.environ.copy()
    env["ZIG"] = zig
    result = run(
        [zig, "build", build_step, "--build-file", str(ROOT / "zigux" / "tests" / "build.zig")],
        cwd=str(ROOT),
        capture_output=True,
        env=env,
    )
    actual.write_text(result.stdout, encoding="utf-8", newline="\n")


def run_phase3_check(
    slug: str,
    description: str | None = None,
    build_step: str | None = None,
    argv: list[str] | None = None,
) -> int:
    args = parse_phase3_args(argv)

    if args.cc:
        compiler = args.cc
    elif os.name == "nt" and shutil.which("wsl"):
        compiler = "gcc"
    else:
        compiler = find_compiler(None)
    zig = find_zig(args.zig)
    run_slug_preflights(slug)

    fixture_key = fixture_key_for_slug(slug)
    fixture_dir = ROOT / "zigux" / "tests" / "fixtures" / fixture_key
    expected = fixture_dir / "expected.json"
    harness = fixture_dir / f"{fixture_key}_c_harness.c"
    temp_prefix = f"zigux_{fixture_key}_"

    with tempfile.TemporaryDirectory(prefix=temp_prefix) as tmp_dir_str:
        tmp_dir = Path(tmp_dir_str)
        c_actual = tmp_dir / f"{fixture_key}_c.actual.json"
        zig_actual = tmp_dir / f"{fixture_key}_zig.actual.json"

        compile_and_run_c(tmp_dir, compiler, harness, c_actual, fixture_key)
        compile_and_run_zig(zig, build_step or build_step_for_slug(slug), zig_actual)

        run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(c_actual)], cwd=str(ROOT))
        run([sys.executable, str(ARTIFACT_DIFF), "--mode", "json", str(expected), str(zig_actual)], cwd=str(ROOT))

    print(f"{status_name_for_slug(slug)}=pass")
    print(f"FIXTURE={expected}")
    return 0


def run_from_wrapper(path: str | Path) -> int:
    slug = slug_from_wrapper_path(path)
    return run_phase3_check(slug)


def run_self_test() -> int:
    expected_wrapper = "\n".join(
        [
            "#!/usr/bin/env python3",
            "from __future__ import annotations",
            "",
            "from phase3_check_lib import run_from_wrapper",
            "",
            "",
            'if __name__ == "__main__":',
            '    raise SystemExit(run_from_wrapper(__file__))',
            "",
        ]
    )
    assert render_wrapper_stub() == expected_wrapper

    assert slug_from_wrapper_path("/tmp/check-phase3-alpha-beta.py") == "alpha-beta"
    try:
        slug_from_wrapper_path("/tmp/phase3-alpha-beta.py")
    except SystemExit as exc:
        assert str(exc) == "unsupported Phase 3 wrapper path: /tmp/phase3-alpha-beta.py"
    else:
        raise AssertionError("expected invalid wrapper path to fail")

    assert fixture_key_for_slug("alpha-beta") == "phase3_alpha_beta"
    assert build_step_for_slug("alpha-beta") == "phase3-alpha-beta-dump"
    assert build_step_for_slug("abi") == "phase3-dump"
    assert description_for_slug("bitmap-cpumask") == "bitmap/cpumask"
    assert description_for_slug("alpha-beta") == "alpha beta"
    assert status_name_for_slug("alpha-beta") == "PHASE3_ALPHA_BETA_DIFF"
    assert shared_runner_gate_for_slug("alpha-beta") == "PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug alpha-beta"
    assert legacy_wrapper_gate_for_slug("alpha-beta") == "PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-alpha-beta.py"
    parsed = parse_phase3_args(["--cc", "/tmp/cc", "--zig", "/tmp/zig"])
    assert parsed.cc == "/tmp/cc"
    assert parsed.zig == "/tmp/zig"
    assert [path.as_posix() for path in preflight_scripts_for_slug("abi")] == [
        (ROOT / "scripts/zigux/validate-phase3-abi-bindings-syntax.py").as_posix(),
        (ROOT / "scripts/zigux/survey-phase3-abi-constant-parity.py").as_posix(),
    ]
    assert preflight_scripts_for_slug("bitmap-cpumask") == ()

    print("PHASE3_CHECK_LIB_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared Phase 3 parity helper library.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated helper checks without launching parity builds.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    raise SystemExit("phase3_check_lib.py is a shared library; pass --self-test to run helper coverage")


if __name__ == "__main__":
    raise SystemExit(main())
