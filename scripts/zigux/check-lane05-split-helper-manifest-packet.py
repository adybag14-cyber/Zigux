#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
SPLIT_HELPER_PATH = Path("scripts/zigux/split-pinned-zig-archive.py")
TOOLCHAIN_POLICY_PATH = Path("scripts/zigux/zig-toolchain-policy.json")

MANIFEST_MARKERS = (
    'manifest = {',
    '    "filename": filename,',
    '    "encoding": "base64",',
    '    "sha256": sha256,',
    '    "size": size,',
    '    "chunk_bytes": chunk_bytes,',
    '    "part_count": part_count,',
    '    "parts_glob": "part-*.b64",',
    'manifest_path = output_dir / "manifest.json"',
    'manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")',
)

HELPER_MARKERS = (
    'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
    "DEFAULT_CHUNK_BYTES = 786_432",
    "EXPECTED_ARCHIVE_SIZES = {",
    '    "x86_64-linux": 58_159_088,',
    '(output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
    'raise ValueError(f"expected archive data for part {index}, got EOF")',
    'raise ValueError("source archive had unexpected trailing bytes after part split")',
    'encoded = path.read_text(encoding="utf-8").strip()',
    "chunks.append(base64.b64decode(encoded, validate=True))",
    'raise ValueError(f"missing expected shard: {path.name}")',
    'payload = (b"lane05-archive-payload-" * 64)[:4097]',
    'reconstructed = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")',
    'print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
    'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
)

ORDERED_MARKERS = (
    ('    "filename": filename,', '    "encoding": "base64",'),
    ('    "encoding": "base64",', '    "sha256": sha256,'),
    ('    "sha256": sha256,', '    "size": size,'),
    ('    "size": size,', '    "chunk_bytes": chunk_bytes,'),
    ('    "chunk_bytes": chunk_bytes,', '    "part_count": part_count,'),
    ('    "part_count": part_count,', '    "parts_glob": "part-*.b64",'),
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"missing required file: {path}") from exc


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise ValueError(f"lane05 split-helper manifest checker missing {label}: {marker}")


def require_exact_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = text.count(marker)
    if actual != expected:
        raise ValueError(
            f"lane05 split-helper manifest checker expected exactly {expected} {label} entries for "
            f"`{marker}`, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise ValueError(f"lane05 split-helper manifest checker missing ordered markers for {label}")
    if earlier_index >= later_index:
        raise ValueError(
            f"lane05 split-helper manifest checker expected {label} `{earlier}` before `{later}`"
        )


def check_helper(root: Path) -> int:
    helper_text = read_text(root / SPLIT_HELPER_PATH)
    policy_text = read_text(root / TOOLCHAIN_POLICY_PATH)
    try:
        policy = json.loads(policy_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"lane05 split-helper manifest checker invalid policy JSON: {exc.msg}") from exc

    if '"channel": "0.17.0-dev.87+9b177a7d2"' not in policy_text:
        raise ValueError("lane05 split-helper manifest checker missing pinned channel marker")
    try:
        archive_target_scope = policy["upgrade_policy"]["archive_target_scope"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "lane05 split-helper manifest checker missing archive target scope marker"
        ) from exc
    if archive_target_scope != ["x86_64-linux"]:
        raise ValueError(
            "lane05 split-helper manifest checker expected archive target scope ['x86_64-linux']"
        )

    for marker in HELPER_MARKERS:
        require_marker(helper_text, marker, "helper marker")
    for marker in MANIFEST_MARKERS:
        require_marker(helper_text, marker, "manifest marker")

    require_exact_count(helper_text, 'manifest = {', 1, "manifest start")
    require_exact_count(helper_text, '    "encoding": "base64",', 1, "manifest encoding")
    require_exact_count(helper_text, '    "parts_glob": "part-*.b64",', 1, "manifest parts_glob")
    require_exact_count(
        helper_text,
        '(output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
        1,
        "shard write marker",
    )

    for earlier, later in ORDERED_MARKERS:
        require_order(helper_text, earlier, later, "manifest key order")
    require_order(
        helper_text,
        'manifest_path = output_dir / "manifest.json"',
        'manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")',
        "manifest write order",
    )
    require_order(
        helper_text,
        "part_count, manifest_path = split_archive(",
        'reconstructed = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")',
        "self-test replay order",
    )
    require_order(
        helper_text,
        'reconstructed = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")',
        'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
        "self-test output order",
    )

    return len(HELPER_MARKERS) + len(MANIFEST_MARKERS)


def write_sample_root(root: Path) -> None:
    (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
    (root / TOOLCHAIN_POLICY_PATH).write_text(
        json.dumps(
            {
                "phase": "Phase 2",
                "channel": "0.17.0-dev.87+9b177a7d2",
                "minimum_version": "0.17.0-dev.87+9b177a7d2",
                "archive_sha256": {
                    "x86_64-linux": "313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77",
                },
                "upgrade_policy": {
                    "channel_minimum_lockstep": True,
                    "archive_target_scope": ["x86_64-linux"],
                    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (root / SPLIT_HELPER_PATH).write_text(
        "\n".join(
            (
                '#!/usr/bin/env python3',
                'TOOLCHAIN_POLICY = Path("scripts/zigux/zig-toolchain-policy.json")',
                "DEFAULT_CHUNK_BYTES = 786_432",
                "EXPECTED_ARCHIVE_SIZES = {",
                '    "x86_64-linux": 58_159_088,',
                "}",
                "def write_manifest(output_dir, *, filename, sha256, size, chunk_bytes, part_count):",
                "    manifest = {",
                '    "filename": filename,',
                '    "encoding": "base64",',
                '    "sha256": sha256,',
                '    "size": size,',
                '    "chunk_bytes": chunk_bytes,',
                '    "part_count": part_count,',
                '    "parts_glob": "part-*.b64",',
                "    }",
                '    manifest_path = output_dir / "manifest.json"',
                '    manifest_path.write_text(json.dumps(manifest, indent=2) + "\\n", encoding="utf-8")',
                "    return manifest_path",
                "",
                "def split_archive(source, output_dir, *, expected_size, expected_sha, filename, chunk_bytes):",
                '    raise ValueError(f"expected archive data for part {index}, got EOF")',
                '    (output_dir / f"part-{index:03d}.b64").write_text(encoded + "\\n", encoding="utf-8")',
                '    raise ValueError("source archive had unexpected trailing bytes after part split")',
                "",
                "def reconstruct_archive(parts_dir, destination):",
                '    encoded = path.read_text(encoding="utf-8").strip()',
                "    chunks.append(base64.b64decode(encoded, validate=True))",
                '    raise ValueError(f"missing expected shard: {path.name}")',
                "",
                "def run_self_test():",
                '    payload = (b"lane05-archive-payload-" * 64)[:4097]',
                "    part_count, manifest_path = split_archive(",
                "        source,",
                "        output_dir,",
                "        expected_size=1,",
                '        expected_sha="sha",',
                '        filename="zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",',
                "        chunk_bytes=1024,",
                "    )",
                '    reconstructed = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")',
                '    print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")',
                '    print("SPLIT_PINNED_ZIG_ARCHIVE_SELF_TEST=pass")',
            )
        )
        + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="lane05_split_helper_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        write_sample_root(root)
        assert check_helper(root) == len(HELPER_MARKERS) + len(MANIFEST_MARKERS)
        case_count += 1

    def expect_failure(mutator, expected_substring: str) -> None:
        nonlocal case_count
        with tempfile.TemporaryDirectory(prefix="lane05_split_helper_manifest_fail_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            mutator(root)
            try:
                check_helper(root)
            except ValueError as exc:
                assert expected_substring in str(exc), str(exc)
                case_count += 1
                return
            raise AssertionError("expected checker to fail")

    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text("missing\n", encoding="utf-8"),
        "missing helper marker",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                '    "encoding": "base64",\n    "sha256": sha256,\n',
                '    "sha256": sha256,\n    "encoding": "base64",\n',
                1,
            ),
            encoding="utf-8",
        ),
        "manifest key order",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                '    "parts_glob": "part-*.b64",\n',
                "",
                1,
            ),
            encoding="utf-8",
        ),
        "manifest marker",
    )
    expect_failure(
        lambda root: (root / TOOLCHAIN_POLICY_PATH).write_text(
            (root / TOOLCHAIN_POLICY_PATH).read_text(encoding="utf-8").replace(
                '"archive_target_scope": [\n      "x86_64-linux"\n    ],',
                '"archive_target_scope": [\n      "aarch64-linux"\n    ],',
                1,
            ),
            encoding="utf-8",
        ),
        "archive target scope",
    )
    expect_failure(
        lambda root: (root / SPLIT_HELPER_PATH).write_text(
            (root / SPLIT_HELPER_PATH).read_text(encoding="utf-8").replace(
                'reconstructed = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")\n'
                '    print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")\n',
                'print("RECONSTRUCT_PINNED_ZIG_ARCHIVE=pass")\n'
                '    reconstructed = reconstruct_archive(output_dir, root / "rebuilt.tar.xz")\n',
                1,
            ),
            encoding="utf-8",
        ),
        "self-test output order",
    )

    print("LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST=pass")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 split helper keeps its shard-manifest packet explicit."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker coverage")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a compact sample root that should satisfy this checker and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root.resolve())
        return 0

    try:
        root = args.root.resolve()
        marker_count = check_helper(root)
    except ValueError as exc:
        print("LANE05_SPLIT_HELPER_MANIFEST_PACKET=fail")
        print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_ROOT={args.root.resolve()}")
        print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_NOTE={exc}")
        return 1

    print("LANE05_SPLIT_HELPER_MANIFEST_PACKET=pass")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_ROOT={root}")
    print(f"LANE05_SPLIT_HELPER_MANIFEST_PACKET_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
