#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path(".")
RAW_GITHUB_COVERAGE_PATH = Path("Documentation/zigux/phase12-raw-github-coverage-survey.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")

REQUIRED_FILES = (
    RAW_GITHUB_COVERAGE_PATH,
    WORKFLOW_PATH,
    MAKEFILE_PATH,
)

RAW_GITHUB_COVERAGE_MARKERS = (
    "`PHASE12_STATUS=active`",
    "current contents-bridge shared support bundle during degraded contents reads:",
    "scripts/zigux/check-phase12-cross-compile-smoke.py",
    "scripts/zigux/check-phase12-libbpf-lane-marker.py",
    "direct container-side `curl`, `wget`, `urllib`, and `git clone https://github.com/adybag14-cyber/Zigux.git` still fail in this runtime through the proxy tunnel with HTTP `403`",
    "same-runtime fallback verification remains contents-bridge-driven here.",
    "the directly readable workflow blob",
    "still rebuilds that repo-local fallback by trying the pinned `third_party` archive first, then the Zig community-mirror list, and finally `ziglang.org` before rerunning `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`",
    "first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`",
    "make -C zigux phase12-smoke ZIG=<attached-zig-path>",
    "make -C zigux phase12-test ZIG=<attached-zig-path>",
    "make -C zigux phase12 ZIG=<attached-zig-path>",
    "This note must keep the repo-local `.zig-toolchain` fallback explicit as the first shipped degraded rerun path when `ZIG` is unset",
)

WORKFLOW_MARKERS = (
    "repo_archive_path=\"third_party/$ZIGUX_ZIG_FILENAME\"",
    "repo_archive_parts_dir=\"${repo_archive_path}.parts\"",
    "python3 scripts/zigux/stage-pinned-zig-archive.py",
    "if try_local_archive; then",
    "https://ziglang.org/download/community-mirrors.txt",
    "if try_download \"$ZIGUX_ZIG_URL\"; then",
    "failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org",
    "run: make -C zigux phase12-smoke",
    "run: make -C zigux phase12-test",
    "run: make -C zigux phase12",
)

MAKEFILE_MARKERS = (
    "ZIG_PINNED_EXECUTABLE :=",
    "ZIG_LOCAL_TOOLCHAIN :=",
    "ZIG_PINNED_TOOLCHAIN :=",
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    "phase12-validate:",
    "phase12-smoke:",
    "phase12-test:",
    "phase12: phase12-validate phase12-smoke phase12-test",
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase12: phase12-smoke phase12-test",
)


class CheckError(RuntimeError):
    pass


def require_file(root: Path, rel: Path) -> Path:
    path = root / rel
    if not path.is_file():
        raise CheckError(f"missing required file: {rel.as_posix()}")
    return path


def require_markers(path: Path, markers: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise CheckError(f"{path.as_posix()}: missing marker {marker!r}")


def run_check(root: Path) -> None:
    for rel in REQUIRED_FILES:
        require_file(root, rel)

    require_markers(root / RAW_GITHUB_COVERAGE_PATH, RAW_GITHUB_COVERAGE_MARKERS)
    require_markers(root / WORKFLOW_PATH, WORKFLOW_MARKERS)
    makefile_path = root / MAKEFILE_PATH
    require_markers(makefile_path, MAKEFILE_MARKERS)
    makefile_text = makefile_path.read_text(encoding="utf-8")
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile_text:
            raise CheckError(f"{MAKEFILE_PATH.as_posix()}: forbidden marker {marker!r}")


def write_fixture(root: Path) -> None:
    payloads = {
        RAW_GITHUB_COVERAGE_PATH: "# Phase 12 Raw GitHub Coverage Survey\n\n"
        + "\n".join(f"- {marker}" for marker in RAW_GITHUB_COVERAGE_MARKERS)
        + "\n",
        WORKFLOW_PATH: "\n".join(WORKFLOW_MARKERS) + "\n",
        MAKEFILE_PATH: "\n".join(MAKEFILE_MARKERS) + "\n",
    }
    for rel, text in payloads.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase12-runtime-shell-fallback-") as tmp:
        root = Path(tmp)
        write_fixture(root)
        run_check(root)
        case_count += 1

        for rel in REQUIRED_FILES:
            write_fixture(root)
            (root / rel).unlink()
            try:
                run_check(root)
            except CheckError:
                pass
            else:
                raise AssertionError(f"expected missing-file failure for {rel.as_posix()}")
            case_count += 1

        write_fixture(root)
        broken = root / RAW_GITHUB_COVERAGE_PATH
        broken.write_text(broken.read_text(encoding="utf-8").replace("contents-bridge-driven here.", "broken"), encoding="utf-8")
        try:
            run_check(root)
        except CheckError:
            pass
        else:
            raise AssertionError("expected raw coverage marker failure")
        case_count += 1

        write_fixture(root)
        broken = root / WORKFLOW_PATH
        broken.write_text(broken.read_text(encoding="utf-8").replace("https://ziglang.org/download/community-mirrors.txt", "broken"), encoding="utf-8")
        try:
            run_check(root)
        except CheckError:
            pass
        else:
            raise AssertionError("expected workflow marker failure")
        case_count += 1

        write_fixture(root)
        broken = root / MAKEFILE_PATH
        broken.write_text(
            broken.read_text(encoding="utf-8") + "\nphase12: phase12-smoke phase12-test\n",
            encoding="utf-8",
        )
        try:
            run_check(root)
        except CheckError:
            pass
        else:
            raise AssertionError("expected forbidden makefile marker failure")
        case_count += 1

    print("PHASE12_RUNTIME_SHELL_FALLBACK_SELF_TEST=pass")
    print(f"PHASE12_RUNTIME_SHELL_FALLBACK_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed on the current Phase 12 degraded-runtime workflow story: "
            "contents-bridge fallback note, workflow toolchain fallback ladder, and Makefile route recovery."
        )
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(args.root.resolve())
    except CheckError as err:
        print("PHASE12_RUNTIME_SHELL_FALLBACK=fail")
        print(str(err))
        return 1

    print("PHASE12_RUNTIME_SHELL_FALLBACK=pass")
    print("PHASE12_RUNTIME_SHELL_FALLBACK_SCOPE=phase12_degraded_workflow_story")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
