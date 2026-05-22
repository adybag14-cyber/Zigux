#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")
TOOLCHAIN_NOTES_PATH = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
CLOSURE_PATH = Path("Documentation/zigux/phase2-closure.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")
THIRD_PARTY_README_PATH = Path("third_party/README.md")


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required packet file: {path}") from exc


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_policy(root: Path) -> tuple[str, str, str, str]:
    policy_path = root / POLICY_PATH
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing toolchain policy: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid toolchain policy JSON in {policy_path}: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"invalid toolchain policy payload in {policy_path}: expected object")

    channel = payload.get("channel")
    archive_sha256 = payload.get("archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(channel, str) or not channel.strip():
        raise ValueError(f"invalid channel in {policy_path}")
    if not isinstance(archive_sha256, dict) or not archive_sha256:
        raise ValueError(f"invalid archive_sha256 in {policy_path}")
    if not isinstance(upgrade_policy, dict):
        raise ValueError(f"invalid upgrade_policy in {policy_path}")

    archive_targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(archive_targets, list) or len(archive_targets) != 1:
        raise ValueError(f"expected exactly one archive_target_scope entry in {policy_path}")
    target = archive_targets[0]
    if not isinstance(target, str) or not target.strip():
        raise ValueError(f"invalid archive target in {policy_path}")
    digest = archive_sha256.get(target)
    if not isinstance(digest, str) or not digest.strip():
        raise ValueError(f"missing archive digest for {target} in {policy_path}")

    filename = f"zig-{target}-{channel.strip()}.tar.xz"
    archive_path = f"third_party/{filename}"
    return channel.strip(), target.strip(), digest.strip(), archive_path


def require_markers(text: str, markers: tuple[str, ...], label: str) -> list[str]:
    return [f"{label}: {marker}" for marker in markers if marker not in text]


def validate_packet(root: Path) -> tuple[str, str]:
    channel, target, digest, archive_path = load_policy(root)
    archive_validate_cmd = (
        "python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "
        f"{archive_path} --archive-target {target}"
    )

    toolchain_notes = read_text(root, TOOLCHAIN_NOTES_PATH)
    closure = read_text(root, CLOSURE_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    third_party_readme = read_text(root, THIRD_PARTY_README_PATH)

    missing: list[str] = []

    missing.extend(
        require_markers(
            toolchain_notes,
            (
                f"channel `{channel}`",
                "`third_party/README.md`",
                f"`{archive_validate_cmd}`",
                "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
                "`scripts/zigux/check-lane05-local-archive-readme.py`",
                "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
                "community-mirrors.txt",
            ),
            "toolchain notes missing marker",
        )
    )
    missing.extend(
        require_markers(
            closure,
            (
                "`third_party/README.md`",
                "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
                "`scripts/zigux/check-lane05-local-archive-readme.py`",
                "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
                "`make -C zigux phase2-toolchain`",
            ),
            "phase2 closure missing marker",
        )
    )
    missing.extend(
        require_markers(
            scripts_readme,
            (
                "`scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
                "`scripts/zigux/install-zig.py`",
                "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
                "`scripts/zigux/check-lane05-local-archive-readme.py`",
                "`third_party`",
            ),
            "scripts readme missing marker",
        )
    )
    missing.extend(
        require_markers(
            tests_readme,
            (
                f"`{archive_path}`",
                f"`{archive_validate_cmd}`",
                "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
                "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
                "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
            ),
            "tests readme missing marker",
        )
    )
    missing.extend(
        require_markers(
            workflow,
            (
                "- 'third_party/**'",
                'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
                'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
                'run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing',
                'run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test',
                'run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test',
            ),
            "workflow missing marker",
        )
    )
    missing.extend(
        require_markers(
            makefile,
            (
                "phase2-toolchain:",
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
                "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
            ),
            "makefile missing marker",
        )
    )
    missing.extend(
        require_markers(
            third_party_readme,
            (
                f"`{archive_path}`",
                f"`{digest}`",
                f"`{archive_validate_cmd}`",
                "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
                "`scripts/zigux/check-lane05-local-archive-readme.py`",
            ),
            "third_party readme missing marker",
        )
    )

    if missing:
        raise ValueError("\n".join(missing))

    return target, archive_path


def build_sample_root(root: Path) -> None:
    policy = """{
  \"phase\": \"Phase 2\",
  \"channel\": \"0.17.0-dev.87+9b177a7d2\",
  \"minimum_version\": \"0.17.0-dev.87+9b177a7d2\",
  \"archive_sha256\": {
    \"x86_64-linux\": \"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77\"
  },
  \"upgrade_policy\": {
    \"channel_minimum_lockstep\": true,
    \"archive_target_scope\": [
      \"x86_64-linux\"
    ],
    \"required_make_routes\": [
      \"phase2-toolchain\",
      \"phase2-validate\",
      \"phase2-cross\"
    ]
  }
}
"""
    write_text(root, POLICY_PATH, policy)
    write_text(
        root,
        TOOLCHAIN_NOTES_PATH,
        "\n".join(
            (
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "- `scripts/zigux/zig-toolchain-policy.json` currently pins Phase 2 to channel `0.17.0-dev.87+9b177a7d2`.",
                "- `third_party/README.md` keeps `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux` explicit beside the policy-driven toolchain packet.",
                "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the current shipped archive guards.",
                "- `.github/workflows/zigux-bootstrap.yml` derives the archive packet from policy, keeps `community-mirrors.txt` before the direct download URL, and reruns `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        CLOSURE_PATH,
        "\n".join(
            (
                "# Phase 2 Closure",
                "",
                "- `third_party/README.md`",
                "- `scripts/zigux/check-lane05-local-first-archive-workflow.py`",
                "- `scripts/zigux/check-lane05-local-archive-readme.py`",
                "- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
                "- `make -C zigux phase2-toolchain`",
            )
        )
        + "\n",
    )
    write_text(
        root,
        SCRIPTS_README_PATH,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "## Phase 2",
                "",
                "- `scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`, `scripts/zigux/install-zig.py`, `scripts/zigux/check-lane05-local-first-archive-workflow.py`, and `scripts/zigux/check-lane05-local-archive-readme.py` keep the returned `third_party` archive packet explicit.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        TESTS_README_PATH,
        "\n".join(
            (
                "# zigux/tests",
                "",
                "## Phase 2 review packet",
                "",
                "keep the repo-local pinned archive packet explicit through `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`, `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`, and `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`.",
                "keep the local-first archive workflow replay surface explicit through `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test` and `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`.",
            )
        )
        + "\n",
    )
    write_text(
        root,
        WORKFLOW_PATH,
        "\n".join(
            (
                "name: zigux-bootstrap",
                "on:",
                "  pull_request:",
                "    paths:",
                "      - 'third_party/**'",
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Setup pinned Zig toolchain",
                "        run: |",
                '          repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
                '          if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
                '            :',
                '          elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
                '            :',
                "      - name: Check current pinned Zig archive packet",
                "        run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
                "      - name: Self-test current Lane 05 local-first archive checker",
                "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
                "      - name: Self-test current Lane 05 local archive README checker",
                "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
            )
        )
        + "\n",
    )
    write_text(
        root,
        MAKEFILE_PATH,
        "\n".join(
            (
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "phase2-toolchain:",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
            )
        )
        + "\n",
    )
    write_text(
        root,
        THIRD_PARTY_README_PATH,
        "\n".join(
            (
                "# Zigux third-party archives",
                "",
                "- file: `third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz`",
                "- sha256: `313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77`",
                "- validation: `python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz --archive-target x86_64-linux`",
                "- `scripts/zigux/check-lane05-local-first-archive-workflow.py` and `scripts/zigux/check-lane05-local-archive-readme.py` are the shipped reminder guards.",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    checks = 0

    with tempfile.TemporaryDirectory(prefix="phase2_pinned_archive_packet_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        assert validate_packet(root) == ("x86_64-linux", "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")
        checks += 1

        build_sample_root(root)
        write_text(
            root,
            TOOLCHAIN_NOTES_PATH,
            read_text(root, TOOLCHAIN_NOTES_PATH).replace("`third_party/README.md`", "`third_party/OTHER.md`", 1),
        )
        try:
            validate_packet(root)
        except ValueError as exc:
            assert "toolchain notes missing marker" in str(exc)
            checks += 1
        else:
            raise AssertionError("expected missing toolchain note marker failure")

        build_sample_root(root)
        write_text(
            root,
            TESTS_README_PATH,
            read_text(root, TESTS_README_PATH).replace("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz", "third_party/other.tar.xz", 1),
        )
        try:
            validate_packet(root)
        except ValueError as exc:
            assert "tests readme missing marker" in str(exc)
            checks += 1
        else:
            raise AssertionError("expected missing tests readme marker failure")

        build_sample_root(root)
        write_text(
            root,
            WORKFLOW_PATH,
            read_text(root, WORKFLOW_PATH).replace("- 'third_party/**'\n", "", 1),
        )
        try:
            validate_packet(root)
        except ValueError as exc:
            assert "workflow missing marker" in str(exc)
            checks += 1
        else:
            raise AssertionError("expected missing workflow marker failure")

        build_sample_root(root)
        write_text(
            root,
            MAKEFILE_PATH,
            read_text(root, MAKEFILE_PATH).replace(
                "\t$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing\n",
                "",
                1,
            ),
        )
        try:
            validate_packet(root)
        except ValueError as exc:
            assert "makefile missing marker" in str(exc)
            checks += 1
        else:
            raise AssertionError("expected missing makefile marker failure")

    print("PHASE2_PINNED_ARCHIVE_PACKET_SELF_TEST=pass")
    print(f"PHASE2_PINNED_ARCHIVE_PACKET_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 2 pinned-archive reminder packet stays aligned across current bootstrap surfaces."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repo root to inspect.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage.")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal current-like packet to the target directory and exit.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_PINNED_ARCHIVE_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    try:
        target, archive_path = validate_packet(args.root.resolve())
    except ValueError as exc:
        print("PHASE2_PINNED_ARCHIVE_PACKET=fail")
        print(f"PHASE2_PINNED_ARCHIVE_PACKET_ROOT={args.root.resolve()}")
        print(f"PHASE2_PINNED_ARCHIVE_PACKET_NOTE={exc}")
        return 1

    print("PHASE2_PINNED_ARCHIVE_PACKET=pass")
    print(f"PHASE2_PINNED_ARCHIVE_PACKET_ROOT={args.root.resolve()}")
    print(f"PHASE2_PINNED_ARCHIVE_PACKET_TARGET={target}")
    print(f"PHASE2_PINNED_ARCHIVE_PACKET_PATH={archive_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
