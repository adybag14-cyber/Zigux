#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCRIPTS_README = Path("scripts/zigux/README.md")
THIRD_PARTY_README = Path("third_party/README.md")
SPLIT_HELPER = Path("scripts/zigux/split-pinned-zig-archive.py")
STAGE_HELPER = Path("scripts/zigux/stage-pinned-zig-archive.py")
TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def load_contract(root: Path) -> dict[str, str]:
    policy_path = root / TOOLCHAIN_POLICY
    try:
        payload = json.loads(policy_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {policy_path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {policy_path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {policy_path}")

    channel = payload.get("channel")
    if not isinstance(channel, str) or not channel.strip():
        raise SystemExit(f"invalid channel in required file: {policy_path}")

    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        raise SystemExit(f"invalid upgrade_policy in required file: {policy_path}")

    target_scope = upgrade_policy.get("archive_target_scope")
    if not isinstance(target_scope, list) or len(target_scope) != 1:
        raise SystemExit(f"expected exactly one archive target in required file: {policy_path}")
    target = target_scope[0]
    if not isinstance(target, str) or not target.strip():
        raise SystemExit(f"invalid archive target in required file: {policy_path}")

    filename = f"zig-{target}-{channel}.tar.xz"
    return {
        "channel": channel,
        "target": target,
        "filename": filename,
        "parts_dir": f"third_party/{filename}.parts",
        "manifest_path": f"third_party/{filename}.parts/manifest.json",
    }


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 split-helper readme checker missing {label}: {marker}")


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 split-helper readme checker missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            f"lane05 split-helper readme checker expected {label} `{earlier}` before `{later}`"
        )


def check_split_helper(root: Path) -> None:
    split_text = read_text(root / SPLIT_HELPER)
    for marker in (
        "DEFAULT_CHUNK_BYTES = 786_432",
        '"encoding": "base64"',
        '"parts_glob": "part-*.b64"',
        "manifest.json",
        'part-{index:03d}.b64',
        "def split_archive(",
        "def reconstruct_archive(",
        "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    ):
        require_marker(split_text, marker, "split helper marker")


def check_stage_helper(root: Path) -> None:
    stage_text = read_text(root / STAGE_HELPER)
    for marker in (
        "def load_shard_manifest(",
        "def reconstruct_archive_from_parts(",
        "parts_dir",
        "manifest.json",
        "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
    ):
        require_marker(stage_text, marker, "stage helper marker")


def check_scripts_readme(root: Path, contract: dict[str, str]) -> None:
    readme_text = read_text(root / SCRIPTS_README)
    markers = (
        "`scripts/zigux/split-pinned-zig-archive.py`",
        "`python3 scripts/zigux/split-pinned-zig-archive.py --self-test`",
        "`scripts/zigux/stage-pinned-zig-archive.py`",
        "`python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`",
        "`third_party/README.md`",
        "`.parts` shard-emitter",
        "`scripts/zigux/check-lane05-split-helper-readme-packet.py`",
        "`scripts/zigux/check-lane05-stage-helper-contract.py`",
        "`scripts/zigux/check-lane05-stage-helper-selftest.py`",
    )
    for marker in markers:
        require_marker(readme_text, marker, "scripts README marker")
    require_order(
        readme_text,
        "`scripts/zigux/split-pinned-zig-archive.py`",
        "`scripts/zigux/stage-pinned-zig-archive.py`",
        "scripts README helper order",
    )


def check_third_party_readme(root: Path, contract: dict[str, str]) -> None:
    readme_text = read_text(root / THIRD_PARTY_README)
    markers = (
        f"`{contract['parts_dir']}`",
        f"`{contract['manifest_path']}`",
        "`scripts/zigux/split-pinned-zig-archive.py`",
        "`manifest.json`",
        "`part-*.b64`",
        "matching shard emitter",
        "verified pinned archive",
    )
    for marker in markers:
        require_marker(readme_text, marker, "third_party README marker")
    require_order(
        readme_text,
        f"`{contract['parts_dir']}`",
        "`scripts/zigux/split-pinned-zig-archive.py`",
        "third_party README shard order",
    )


def build_sample_root(root: Path) -> None:
    contract = {
        "target": "x86_64-linux",
        "channel": "0.17.0-dev.87+9b177a7d2",
        "filename": "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
        "parts_dir": "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts",
        "manifest_path": (
            "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts/manifest.json"
        ),
    }

    write_text(
        root / TOOLCHAIN_POLICY,
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": contract["channel"],
                "minimum_version": contract["channel"],
                "archive_sha256": {
                    contract["target"]: "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": [contract["target"]],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate"],
                },
            },
            indent=2,
        )
        + "\n",
    )

    write_text(
        root / SPLIT_HELPER,
        "\n".join(
            (
                "DEFAULT_CHUNK_BYTES = 786_432",
                'manifest = {"encoding": "base64", "parts_glob": "part-*.b64"}',
                "manifest.json",
                "part-{index:03d}.b64",
                "def split_archive():",
                "    pass",
                "def reconstruct_archive():",
                "    pass",
                "SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
            )
        )
        + "\n",
    )

    write_text(
        root / STAGE_HELPER,
        "\n".join(
            (
                "def load_shard_manifest():",
                "    pass",
                "def reconstruct_archive_from_parts(parts_dir):",
                "    manifest_path = 'manifest.json'",
                "    return parts_dir",
                "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass",
            )
        )
        + "\n",
    )

    write_text(
        root / SCRIPTS_README,
        "\n".join(
            (
                "# scripts/zigux",
                "",
                "## Phase 2",
                "",
                "- `third_party/README.md`, `scripts/zigux/split-pinned-zig-archive.py`, `python3 scripts/zigux/split-pinned-zig-archive.py --self-test`, `scripts/zigux/stage-pinned-zig-archive.py`, `python3 scripts/zigux/stage-pinned-zig-archive.py --self-test`, `scripts/zigux/check-lane05-split-helper-readme-packet.py`, `scripts/zigux/check-lane05-stage-helper-contract.py`, and `scripts/zigux/check-lane05-stage-helper-selftest.py` keep the repo-local direct-archive, `.parts` shard-emitter, staged-recovery, README, contract, and self-test packet explicit from the scripts root beside that same shipped Lane 05 local-first archive path",
            )
        )
        + "\n",
    )

    write_text(
        root / THIRD_PARTY_README,
        "\n".join(
            (
                "# Zigux third-party archives",
                "",
                f"- If the exact archive file is absent but `{contract['parts_dir']}` is present, `.github/workflows/zigux-bootstrap.yml` stages the same pinned payload locally with `scripts/zigux/stage-pinned-zig-archive.py` before mirror or direct-download fallback.",
                f"- `scripts/zigux/split-pinned-zig-archive.py` is the matching shard emitter for `{contract['manifest_path']}`, writing `manifest.json` plus `part-*.b64` from a verified pinned archive before that staged recovery path is published.",
            )
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_readme_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        contract = load_contract(root)
        check_split_helper(root)
        check_stage_helper(root)
        check_scripts_readme(root, contract)
        check_third_party_readme(root, contract)
        case_count += 1

        write_text(
            root / SCRIPTS_README,
            read_text(root / SCRIPTS_README).replace(
                "`scripts/zigux/split-pinned-zig-archive.py`, ", "", 1
            ),
        )
        try:
            check_scripts_readme(root, contract)
        except SystemExit as exc:
            assert "`scripts/zigux/split-pinned-zig-archive.py`" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected scripts README marker failure")

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_readme_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        contract = load_contract(root)
        write_text(
            root / THIRD_PARTY_README,
            read_text(root / THIRD_PARTY_README).replace("`part-*.b64`", "`parts`", 1),
        )
        try:
            check_third_party_readme(root, contract)
        except SystemExit as exc:
            assert "`part-*.b64`" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected third_party README marker failure")

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_readme_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        contract = load_contract(root)
        write_text(root / SPLIT_HELPER, "missing\n")
        try:
            check_split_helper(root)
        except SystemExit as exc:
            assert "split helper marker" in str(exc), str(exc)
            case_count += 1
        else:
            raise AssertionError("expected split helper marker failure")

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_readme_") as tmp_dir:
        root = Path(tmp_dir)
        build_sample_root(root)
        contract = load_contract(root)
        write_text(
            root / SCRIPTS_README,
            read_text(root / SCRIPTS_README).replace(
                "`scripts/zigux/split-pinned-zig-archive.py`",
                "`scripts/zigux/stage-pinned-zig-archive.py`",
                1,
            ),
        )
        try:
            check_scripts_readme(root, contract)
        except SystemExit as exc:
            assert "exactly" not in str(exc)
            case_count += 1
        else:
            raise AssertionError("expected scripts README duplicate-order failure")

    print("LANE05_SPLIT_HELPER_README_PACKET_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_README_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that Lane 05 scripts-root reminders keep the split-helper shard packet explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a self-contained sample repository root for checker replay",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"LANE05_SPLIT_HELPER_README_PACKET_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    root = args.root.resolve()
    contract = load_contract(root)
    check_split_helper(root)
    check_stage_helper(root)
    check_scripts_readme(root, contract)
    check_third_party_readme(root, contract)
    print("LANE05_SPLIT_HELPER_README_PACKET=pass")
    print(f"LANE05_SPLIT_HELPER_README_PACKET_TARGET={contract['target']}")
    print(f"LANE05_SPLIT_HELPER_README_PACKET_MANIFEST={contract['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
