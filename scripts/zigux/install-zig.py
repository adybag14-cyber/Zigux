#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'
INDEX_URL = 'https://ziglang.org/download/index.json'
VERSION_KEY_RE = re.compile(
    r'^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
    r'(?:-dev\.(?P<dev>\d+)(?:\+[0-9A-Za-z.-]+)?)?$'
)
ARCHIVE_SHA256_RE = re.compile(r'^[0-9a-f]{64}$')


def normalize_os(name: str) -> str:
    lowered = name.lower()
    if lowered.startswith('linux'):
        return 'linux'
    if lowered.startswith('darwin') or lowered.startswith('mac'):
        return 'macos'
    if lowered.startswith('windows'):
        return 'windows'
    raise SystemExit(f'unsupported OS for Zig installer: {name}')


def normalize_arch(name: str) -> str:
    lowered = name.lower()
    if lowered in {'amd64', 'x86_64', 'x64'}:
        return 'x86_64'
    if lowered in {'arm64', 'aarch64'}:
        return 'aarch64'
    if lowered in {'x86', 'i386', 'i686'}:
        return 'x86'
    raise SystemExit(f'unsupported architecture for Zig installer: {name}')


def parse_archive_sha256(raw: object) -> dict[str, str]:
    if raw is None:
        return {}
    if not isinstance(raw, dict) or not raw:
        raise ValueError('toolchain policy archive_sha256 must be a non-empty object when present')

    normalized: dict[str, str] = {}
    for target_key, digest in raw.items():
        if not isinstance(target_key, str) or not target_key:
            raise ValueError('toolchain policy archive_sha256 keys must be non-empty target strings')
        if not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower()):
            raise ValueError(
                f'toolchain policy archive_sha256 entry for {target_key!r} must be a 64-character hex string'
            )
        normalized[target_key] = digest.lower()
    return normalized


def parse_policy_data(raw: object) -> tuple[str, str, dict[str, str]]:
    if not isinstance(raw, dict):
        raise ValueError('toolchain policy must be a JSON object')

    channel = raw.get('channel')
    minimum_version = raw.get('minimum_version')
    if not isinstance(channel, str) or not channel:
        raise ValueError('toolchain policy must define a non-empty string channel')
    if not isinstance(minimum_version, str) or not minimum_version:
        raise ValueError('toolchain policy must define a non-empty string minimum_version')
    return channel, minimum_version, parse_archive_sha256(raw.get('archive_sha256'))


def load_policy(path: Path) -> tuple[str, str, dict[str, str]]:
    return parse_policy_data(json.loads(path.read_text(encoding='utf-8')))


def read_index() -> dict:
    with urllib.request.urlopen(INDEX_URL) as response:
        return json.load(response)


def extract_archive(archive_path: Path, dest: Path) -> Path:
    if archive_path.suffix == '.zip':
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(dest)
    else:
        with tarfile.open(archive_path, 'r:*') as tf:
            tf.extractall(dest)

    children = [child for child in dest.iterdir() if child.is_dir()]
    if len(children) != 1:
        raise SystemExit(f'unexpected extracted layout in {dest}')
    return children[0]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def append_github_path(path: Path) -> None:
    github_path = os.environ.get('GITHUB_PATH')
    if not github_path:
        return
    with open(github_path, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(str(path.resolve()) + '\n')


def is_version_key(value: str) -> bool:
    return VERSION_KEY_RE.fullmatch(value.strip()) is not None


def direct_download_url(version: str, target_key: str) -> str:
    base = 'https://ziglang.org/builds' if '-dev.' in version else f'https://ziglang.org/download/{version}'
    if target_key.endswith('-windows'):
        filename = f'zig-{target_key}-{version}.zip'
    else:
        filename = f'zig-{target_key}-{version}.tar.xz'
    return f'{base}/{filename}'


def resolve_entry(index: dict, channel: str, target_key: str) -> tuple[dict, str]:
    if channel in index:
        return index[channel], 'channel-key'

    for key, entry in index.items():
        if isinstance(entry, dict) and entry.get('version') == channel:
            return entry, f'version-match:{key}'

    if is_version_key(channel):
        return {
            'version': channel,
            target_key: {
                'tarball': direct_download_url(channel, target_key),
            },
        }, 'direct-url-fallback'

    raise SystemExit(f'unknown Zig channel/version key: {channel}')


def run_self_test() -> int:
    assert normalize_os('Linux') == 'linux'
    assert normalize_os('Darwin') == 'macos'
    assert normalize_os('Windows_NT') == 'windows'
    assert normalize_arch('x86_64') == 'x86_64'
    assert normalize_arch('amd64') == 'x86_64'
    assert normalize_arch('aarch64') == 'aarch64'
    assert normalize_arch('i686') == 'x86'
    assert parse_policy_data(
        {
            'channel': '0.17.0-dev.87+9b177a7d2',
            'minimum_version': '0.17.0-dev.87+9b177a7d2',
            'archive_sha256': {
                'x86_64-linux': '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77',
            },
        }
    ) == (
        '0.17.0-dev.87+9b177a7d2',
        '0.17.0-dev.87+9b177a7d2',
        {'x86_64-linux': '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77'},
    )
    assert is_version_key('0.17.0-dev.87+9b177a7d2')
    assert not is_version_key('master')
    assert direct_download_url('0.17.0-dev.87+9b177a7d2', 'x86_64-linux') == (
        'https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz'
    )
    assert direct_download_url('0.16.0', 'x86_64-windows') == (
        'https://ziglang.org/download/0.16.0/zig-x86_64-windows-0.16.0.zip'
    )
    entry, resolution = resolve_entry(
        {
            'master': {
                'version': '0.17.0-dev.90+abcdef',
                'x86_64-linux': {'tarball': 'https://example.invalid/master.tar.xz'},
            },
            'stable': {
                'version': '0.16.0',
                'x86_64-linux': {'tarball': 'https://example.invalid/stable.tar.xz'},
            },
        },
        '0.16.0',
        'x86_64-linux',
    )
    assert resolution == 'version-match:stable'
    assert entry['version'] == '0.16.0'
    entry, resolution = resolve_entry({}, '0.17.0-dev.87+9b177a7d2', 'x86_64-linux')
    assert resolution == 'direct-url-fallback'
    assert entry['x86_64-linux']['tarball'] == (
        'https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz'
    )
    sample = Path('/tmp/zigux-toolchain-check') / 'sample.bin'
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_bytes(b'zigux-toolchain')
    assert sha256_file(sample) == '187643e96a97359df9f137c811446d257d418f500e30ac264db38e19edd466cf'
    try:
        parse_policy_data({'channel': '', 'minimum_version': '0.17.0-dev.87+9b177a7d2'})
    except ValueError:
        pass
    else:
        raise AssertionError('expected invalid toolchain policy to fail')
    try:
        parse_policy_data(
            {
                'channel': '0.17.0-dev.87+9b177a7d2',
                'minimum_version': '0.17.0-dev.87+9b177a7d2',
                'archive_sha256': {'x86_64-linux': 'not-a-digest'},
            }
        )
    except ValueError:
        pass
    else:
        raise AssertionError('expected invalid archive sha256 policy entry to fail')
    print('ZIG_INSTALL_SELF_TEST=pass')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Install Zig from the official Zig download index.')
    parser.add_argument('--channel', help='Channel or version key from ziglang.org/download/index.json')
    parser.add_argument('--policy', help='Toolchain policy JSON path. Defaults to scripts/zigux/zig-toolchain-policy.json.')
    parser.add_argument('--dest', default='.zig-toolchain', help='Install root directory')
    parser.add_argument('--system', help='Override detected OS key (linux, macos, windows)')
    parser.add_argument('--arch', help='Override detected architecture key (x86_64, aarch64, x86)')
    parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')
    parser.add_argument('--self-test', action='store_true', help='Run built-in policy and platform parser checks.')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    policy_path = Path(args.policy) if args.policy else DEFAULT_POLICY
    policy_channel = None
    policy_minimum_version = None
    policy_archive_sha256: dict[str, str] = {}
    if policy_path.exists():
        try:
            policy_channel, policy_minimum_version, policy_archive_sha256 = load_policy(policy_path)
        except ValueError as exc:
            raise SystemExit(f'invalid toolchain policy {policy_path}: {exc}')
    elif args.policy:
        raise SystemExit(f'toolchain policy not found: {policy_path}')

    channel = args.channel or policy_channel or 'master'
    system_key = args.system or normalize_os(platform.system())
    arch_key = args.arch or normalize_arch(platform.machine())
    target_key = f'{arch_key}-{system_key}'

    index = read_index()
    entry, resolution = resolve_entry(index, channel, target_key)
    if target_key not in entry:
        raise SystemExit(f'Zig download index has no target {target_key} under {channel}')

    target = entry[target_key]
    tarball_url = target['tarball']
    version = entry['version']
    if policy_minimum_version is not None and version != policy_minimum_version:
        raise SystemExit(
            f'policy version drift for {channel}: index resolved {version}, '
            f'expected {policy_minimum_version}'
        )
    expected_sha256 = policy_archive_sha256.get(target_key)

    print(f'ZIG_INSTALL_CHANNEL={channel}')
    print(f'ZIG_INSTALL_VERSION={version}')
    print(f'ZIG_INSTALL_TARGET={target_key}')
    print(f'ZIG_INSTALL_URL={tarball_url}')
    print(f'ZIG_INSTALL_RESOLUTION={resolution}')
    if policy_channel is not None:
        print(f'ZIG_INSTALL_POLICY={policy_path}')
    if expected_sha256 is not None:
        print(f'ZIG_INSTALL_EXPECTED_SHA256={expected_sha256}')

    if args.resolve_only:
        print('ZIG_INSTALL_STATUS=resolved')
        return 0

    install_root = Path(args.dest)
    install_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        archive_name = tarball_url.rsplit('/', 1)[-1]
        archive_path = tmpdir / archive_name
        with urllib.request.urlopen(tarball_url) as response, open(archive_path, 'wb') as out:
            shutil.copyfileobj(response, out)

        archive_sha256 = sha256_file(archive_path)
        print(f'ZIG_INSTALL_ARCHIVE_SHA256={archive_sha256}')
        if expected_sha256 is not None and archive_sha256 != expected_sha256:
            raise SystemExit(
                f'archive sha256 mismatch for {target_key}: got {archive_sha256}, expected {expected_sha256}'
            )

        extracted_root = extract_archive(archive_path, tmpdir / 'extract')
        final_root = install_root / extracted_root.name
        if final_root.exists():
            shutil.rmtree(final_root)
        shutil.copytree(extracted_root, final_root)

    bin_dir = final_root
    if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():
        bin_dir = final_root
    elif (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():
        bin_dir = final_root / 'bin'
    else:
        raise SystemExit(f'could not locate zig binary in {final_root}')

    append_github_path(bin_dir)
    print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')
    print('ZIG_INSTALL_STATUS=pass')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())