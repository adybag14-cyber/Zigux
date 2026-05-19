#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zipfile


INDEX_URL = 'https://ziglang.org/download/index.json'
VERSION_KEY_RE = re.compile(r'^\d+\.\d+\.\d+(?:-dev\.\d+(?:\+[0-9A-Za-z.-]+)?)?$')
ARCHIVE_SHA256_RE = re.compile(r'^[0-9a-f]{64}$')
RETRYABLE_HTTP_STATUS_CODES = {500, 502, 503, 504}
DOWNLOAD_RETRIES = 4
DOWNLOAD_TIMEOUT = 120.0
DOWNLOAD_CHUNK_SIZE = 1024 * 1024
ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
TOOLCHAIN_POLICY = ROOT / 'scripts' / 'zigux' / 'zig-toolchain-policy.json'
FALLBACK_CHANNEL = 'master'


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


def is_explicit_version(channel: str) -> bool:
    return VERSION_KEY_RE.fullmatch(channel) is not None


def load_policy(policy_path: Path = TOOLCHAIN_POLICY) -> dict[str, object] | None:
    if not policy_path.exists():
        return None
    try:
        payload = json.loads(policy_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise SystemExit(f'invalid toolchain policy JSON in {policy_path}: {exc.msg}') from exc
    if not isinstance(payload, dict):
        raise SystemExit(f'invalid toolchain policy payload in {policy_path}: expected object')
    return payload


def load_policy_channel(policy_path: Path = TOOLCHAIN_POLICY, fallback: str = FALLBACK_CHANNEL) -> str:
    payload = load_policy(policy_path)
    if payload is None:
        return fallback
    channel = payload.get('channel')
    if not isinstance(channel, str) or not channel.strip():
        raise SystemExit(f'invalid channel in {policy_path}')
    return channel.strip()


def load_policy_archive_sha256(policy_path: Path, target_key: str) -> str | None:
    payload = load_policy(policy_path)
    if payload is None:
        return None
    archive_sha256 = payload.get('archive_sha256')
    if archive_sha256 is None:
        return None
    if not isinstance(archive_sha256, dict):
        raise SystemExit(f'invalid archive_sha256 in {policy_path}')
    digest = archive_sha256.get(target_key)
    if digest is None:
        return None
    if not isinstance(digest, str) or not ARCHIVE_SHA256_RE.fullmatch(digest.lower()):
        raise SystemExit(f'invalid archive sha256 for {target_key} in {policy_path}')
    return digest.lower()


def calculate_sha256(path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(path, 'rb') as fh:
        while True:
            chunk = fh.read(DOWNLOAD_CHUNK_SIZE)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_archive_sha256(path: Path, expected_sha256: str) -> str:
    actual_sha256 = calculate_sha256(path)
    if actual_sha256.lower() != expected_sha256.lower():
        raise SystemExit(
            f'zig archive sha256 mismatch for {path.name}: expected {expected_sha256.lower()}, got {actual_sha256.lower()}'
        )
    return actual_sha256.lower()


def open_url(url: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return urllib.request.urlopen(url, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code not in RETRYABLE_HTTP_STATUS_CODES or attempt == retries:
                raise
            last_error = exc
        except urllib.error.URLError as exc:
            if attempt == retries:
                raise
            last_error = exc
        time.sleep(min(0.5 * attempt, 2.0))
    if last_error is not None:
        raise last_error
    raise RuntimeError(f'failed to open URL after retries: {url}')


def response_status(response) -> int | None:
    status = getattr(response, 'status', None)
    if status is not None:
        return status
    if hasattr(response, 'getcode'):
        return response.getcode()
    return None


def build_download_request(url: str, start_offset: int) -> urllib.request.Request | str:
    if start_offset <= 0:
        return url
    return urllib.request.Request(url, headers={'Range': f'bytes={start_offset}-'})


def copy_response_chunks(response, destination: Path, *, append: bool) -> None:
    mode = 'ab' if append else 'wb'
    with open(destination, mode) as out:
        while True:
            try:
                chunk = response.read(DOWNLOAD_CHUNK_SIZE)
            except http.client.IncompleteRead as exc:
                if exc.partial:
                    out.write(exc.partial)
                raise
            if not chunk:
                return
            out.write(chunk)


def copy_url_to_file_with_curl(
    url: str,
    destination: Path,
    *,
    retries: int = DOWNLOAD_RETRIES,
    timeout: float = DOWNLOAD_TIMEOUT,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        'curl',
        '--fail',
        '--location',
        '--silent',
        '--show-error',
        '--retry',
        str(retries),
        '--retry-all-errors',
        '--retry-delay',
        '2',
        '--connect-timeout',
        str(max(5, int(timeout // 4))),
        '--speed-limit',
        '1',
        '--speed-time',
        str(max(30, int(timeout))),
        '--continue-at',
        '-',
        '--output',
        str(destination),
        url,
    ]
    subprocess.run(cmd, check=True)


def copy_url_to_file(
    url: str,
    destination: Path,
    *,
    retries: int = DOWNLOAD_RETRIES,
    timeout: float = DOWNLOAD_TIMEOUT,
) -> None:
    last_error: Exception | None = None
    if shutil.which('curl') is not None:
        try:
            copy_url_to_file_with_curl(url, destination, retries=retries, timeout=timeout)
            return
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            last_error = exc
            if destination.exists() and destination.stat().st_size == 0:
                destination.unlink()
    for attempt in range(1, retries + 1):
        resume_offset = destination.stat().st_size if destination.exists() else 0
        request = build_download_request(url, resume_offset)
        try:
            with open_url(request, retries=1, timeout=timeout) as response:
                status = response_status(response)
                append = resume_offset > 0 and status == 206
                if not append and destination.exists():
                    destination.unlink()
                copy_response_chunks(response, destination, append=append)
            return
        except TimeoutError as exc:
            last_error = exc
        except http.client.IncompleteRead as exc:
            last_error = exc
        except ConnectionResetError as exc:
            last_error = exc
        except urllib.error.URLError as exc:
            last_error = exc
        if attempt == retries:
            break
        time.sleep(min(1.5 * attempt, 5.0))
    if last_error is not None:
        raise last_error
    raise RuntimeError(f'failed to download URL after retries: {url}')


def read_index() -> dict:
    with open_url(INDEX_URL) as response:
        return json.load(response)


def infer_tarball_url(channel: str, target_key: str, system_key: str) -> str:
    suffix = '.zip' if system_key == 'windows' else '.tar.xz'
    if '-dev.' in channel:
        return f'https://ziglang.org/builds/zig-{target_key}-{channel}{suffix}'
    return f'https://ziglang.org/download/{channel}/zig-{target_key}-{channel}{suffix}'


def resolve_target(index: dict, channel: str, arch_key: str, system_key: str) -> tuple[str, str, str]:
    target_key = f'{arch_key}-{system_key}'
    entry = index.get(channel)
    if entry is None and VERSION_KEY_RE.fullmatch(channel):
        for candidate in index.values():
            if isinstance(candidate, dict) and candidate.get('version') == channel:
                entry = candidate
                break
        if entry is None:
            return target_key, channel, infer_tarball_url(channel, target_key, system_key)
    if entry is None:
        raise SystemExit(f'unknown Zig channel/version key: {channel}')
    if target_key not in entry:
        raise SystemExit(f'Zig download index has no target {target_key} under {channel}')

    target = entry[target_key]
    tarball_url = target['tarball']
    version = entry['version']
    return target_key, version, tarball_url


def load_index(channel: str) -> dict:
    try:
        return read_index()
    except (TimeoutError, urllib.error.URLError):
        if not is_explicit_version(channel):
            raise
        return {}


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


def resolve_bin_dir(final_root: Path) -> Path:
    if (final_root / 'zig').exists() or (final_root / 'zig.exe').exists():
        return final_root
    if (final_root / 'bin' / 'zig').exists() or (final_root / 'bin' / 'zig.exe').exists():
        return final_root / 'bin'
    raise SystemExit(f'could not locate zig binary in {final_root}')


def append_github_path(path: Path) -> None:
    github_path = os.environ.get('GITHUB_PATH')
    if not github_path:
        return
    with open(github_path, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(str(path.resolve()) + '\n')


def run_self_test() -> int:
    assert normalize_os('Linux') == 'linux'
    assert normalize_os('Darwin') == 'macos'
    assert normalize_os('Windows') == 'windows'

    assert normalize_arch('amd64') == 'x86_64'
    assert normalize_arch('aarch64') == 'aarch64'
    assert normalize_arch('i686') == 'x86'
    sample_index = {
        'master': {
            'version': '0.17.0-dev.87+9b177a7d2',
            'x86_64-linux': {
                'tarball': 'https://example.invalid/zig-linux.tar.xz',
            },
            'aarch64-macos': {
                'tarball': 'https://example.invalid/zig-macos.tar.xz',
            },
        },
        '0.16.0': {
            'version': '0.16.0',
            'x86_64-linux': {
                'tarball': 'https://example.invalid/zig-0.16.0.tar.xz',
            },
        },
    }

    assert resolve_target(sample_index, 'master', 'x86_64', 'linux') == (
        'x86_64-linux',
        '0.17.0-dev.87+9b177a7d2',
        'https://example.invalid/zig-linux.tar.xz',
    )
    assert resolve_target(sample_index, 'master', 'aarch64', 'macos') == (
        'aarch64-macos',
        '0.17.0-dev.87+9b177a7d2',
        'https://example.invalid/zig-macos.tar.xz',
    )
    assert resolve_target(sample_index, '0.17.0-dev.87+9b177a7d2', 'x86_64', 'linux') == (
        'x86_64-linux',
        '0.17.0-dev.87+9b177a7d2',
        'https://example.invalid/zig-linux.tar.xz',
    )
    assert resolve_target(
        {'0.16.0': sample_index['0.16.0']},
        '0.17.0-dev.87+9b177a7d2',
        'x86_64',
        'linux',
    ) == (
        'x86_64-linux',
        '0.17.0-dev.87+9b177a7d2',
        'https://ziglang.org/builds/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz',
    )

    original_read_index = globals()['read_index']
    try:
        globals()['read_index'] = lambda: (_ for _ in ()).throw(TimeoutError('timed out'))
        assert load_index('0.17.0-dev.87+9b177a7d2') == {}
        try:
            load_index('master')
        except TimeoutError:
            pass
        else:
            raise AssertionError('expected non-explicit channel timeout to fail')
    finally:
        globals()['read_index'] = original_read_index

    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_policy_') as tmp_dir:
        policy_path = Path(tmp_dir) / 'zig-toolchain-policy.json'
        assert load_policy_channel(policy_path, '0.15.0') == '0.15.0'
        assert load_policy_archive_sha256(policy_path, 'x86_64-linux') is None
        policy_path.write_text(
            '{"channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77"}}\n',
            encoding='utf-8',
        )
        assert load_policy_channel(policy_path, '0.15.0') == '0.17.0-dev.87+9b177a7d2'
        assert load_policy_archive_sha256(policy_path, 'x86_64-linux') == '313b231e76f3cc9b718044602dbc3c42b531693507203a6baf2fa892c9533e77'
        assert load_policy_archive_sha256(policy_path, 'aarch64-linux') is None
        policy_path.write_text('{"channel":7}\n', encoding='utf-8')
        try:
            load_policy_channel(policy_path, '0.15.0')
        except SystemExit as exc:
            assert 'invalid channel' in str(exc)
        else:
            raise AssertionError('expected invalid channel to fail')
        policy_path.write_text('{"channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":7}\n', encoding='utf-8')
        try:
            load_policy_archive_sha256(policy_path, 'x86_64-linux')
        except SystemExit as exc:
            assert 'invalid archive_sha256' in str(exc)
        else:
            raise AssertionError('expected invalid archive_sha256 to fail')
        policy_path.write_text('{"channel":"0.17.0-dev.87+9b177a7d2","archive_sha256":{"x86_64-linux":"short"}}\n', encoding='utf-8')
        try:
            load_policy_archive_sha256(policy_path, 'x86_64-linux')
        except SystemExit as exc:
            assert 'invalid archive sha256' in str(exc)
        else:
            raise AssertionError('expected invalid archive sha256 to fail')
        policy_path.write_text('{not-json}\n', encoding='utf-8')
        try:
            load_policy_channel(policy_path, '0.15.0')
        except SystemExit as exc:
            assert 'invalid toolchain policy JSON' in str(exc)
        else:
            raise AssertionError('expected invalid JSON policy to fail')

    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_sha_') as tmp_dir:
        archive_path = Path(tmp_dir) / 'archive.tar.xz'
        archive_path.write_bytes(b'zigux-archive')
        expected_sha256 = hashlib.sha256(b'zigux-archive').hexdigest()
        assert calculate_sha256(archive_path) == expected_sha256
        assert verify_archive_sha256(archive_path, expected_sha256) == expected_sha256
        try:
            verify_archive_sha256(archive_path, '0' * 64)
        except SystemExit as exc:
            assert 'zig archive sha256 mismatch' in str(exc)
        else:
            raise AssertionError('expected sha mismatch to fail')

    class FakeResponse:
        def __init__(self, events: list[bytes | BaseException], *, status: int):
            self._events = list(events)
            self.status = status

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def getcode(self) -> int:
            return self.status

        def read(self, size: int = -1) -> bytes:
            del size
            if not self._events:
                return b''
            event = self._events.pop(0)
            if isinstance(event, BaseException):
                raise event
            return event

    resume_headers: list[str | None] = []

    def resumable_open_url(target: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):
        del retries, timeout
        if isinstance(target, urllib.request.Request):
            range_header = target.headers.get('Range')
        else:
            range_header = None
        resume_headers.append(range_header)
        if range_header is None:
            return FakeResponse([b'zig-', TimeoutError('timed out')], status=200)
        assert range_header == 'bytes=4-'
        return FakeResponse([b'data'], status=206)

    temp_path = Path(tempfile.mkdtemp(prefix='zigux_install_zig_selftest_')) / 'archive.tar.xz'
    original_open_url = globals()['open_url']
    original_which = shutil.which
    try:
        shutil.which = lambda name: None if name == 'curl' else original_which(name)
        globals()['open_url'] = resumable_open_url
        copy_url_to_file('https://example.invalid/archive.tar.xz', temp_path, retries=2, timeout=1.0)
        assert temp_path.read_bytes() == b'zig-data'
        assert resume_headers == [None, 'bytes=4-']
    finally:
        shutil.which = original_which
        globals()['open_url'] = original_open_url
        if temp_path.exists():
            temp_path.unlink()
        temp_path.parent.rmdir()

    incomplete_headers: list[str | None] = []

    def incomplete_read_open_url(target: str | urllib.request.Request, *, retries: int = 3, timeout: float = 30.0):
        del retries, timeout
        if isinstance(target, urllib.request.Request):
            range_header = target.headers.get('Range')
        else:
            range_header = None
        incomplete_headers.append(range_header)
        if range_header is None:
            return FakeResponse([b'zig-', http.client.IncompleteRead(b'd', 4)], status=200)
        assert range_header == 'bytes=5-'
        return FakeResponse([b'ata'], status=206)

    temp_path = Path(tempfile.mkdtemp(prefix='zigux_install_zig_incomplete_')) / 'archive.tar.xz'
    try:
        shutil.which = lambda name: None if name == 'curl' else original_which(name)
        globals()['open_url'] = incomplete_read_open_url
        copy_url_to_file('https://example.invalid/archive.tar.xz', temp_path, retries=2, timeout=1.0)
        assert temp_path.read_bytes() == b'zig-data'
        assert incomplete_headers == [None, 'bytes=5-']
    finally:
        shutil.which = original_which
        globals()['open_url'] = original_open_url
        if temp_path.exists():
            temp_path.unlink()
        temp_path.parent.rmdir()

    curl_commands: list[list[str]] = []

    def fake_run(cmd: list[str], *, check: bool) -> None:
        assert check is True
        curl_commands.append(cmd)

    original_run = subprocess.run
    try:
        subprocess.run = fake_run
        copy_url_to_file_with_curl(
            'https://example.invalid/archive.tar.xz',
            Path('/tmp/zigux-install-zig-curl-test/archive.tar.xz'),
            retries=5,
            timeout=90.0,
        )
        assert len(curl_commands) == 1
        assert curl_commands[0][0] == 'curl'
        assert '--continue-at' in curl_commands[0]
        assert '--retry-all-errors' in curl_commands[0]
        assert curl_commands[0][-1] == 'https://example.invalid/archive.tar.xz'
    finally:
        subprocess.run = original_run

    curl_copy_calls: list[tuple[str, Path, int, float]] = []

    def fake_curl_copy(url: str, destination: Path, *, retries: int = DOWNLOAD_RETRIES, timeout: float = DOWNLOAD_TIMEOUT) -> None:
        curl_copy_calls.append((url, destination, retries, timeout))

    original_curl_copy = globals()['copy_url_to_file_with_curl']
    try:
        shutil.which = lambda name: '/usr/bin/curl' if name == 'curl' else original_which(name)
        globals()['copy_url_to_file_with_curl'] = fake_curl_copy
        copy_url_to_file(
            'https://example.invalid/archive.tar.xz',
            Path('/tmp/zigux-install-zig-curl-preferred/archive.tar.xz'),
            retries=7,
            timeout=9.0,
        )
        assert curl_copy_calls == [
            (
                'https://example.invalid/archive.tar.xz',
                Path('/tmp/zigux-install-zig-curl-preferred/archive.tar.xz'),
                7,
                9.0,
            )
        ]
    finally:
        shutil.which = original_which
        globals()['copy_url_to_file_with_curl'] = original_curl_copy

    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_layout_') as tmp_dir:
        root_layout = Path(tmp_dir) / 'root-layout'
        root_layout.mkdir(parents=True)
        (root_layout / 'zig').write_text('', encoding='utf-8')
        assert resolve_bin_dir(root_layout) == root_layout

        bin_layout = Path(tmp_dir) / 'bin-layout'
        (bin_layout / 'bin').mkdir(parents=True)
        (bin_layout / 'bin' / 'zig').write_text('', encoding='utf-8')
        assert resolve_bin_dir(bin_layout) == bin_layout / 'bin'

        try:
            resolve_bin_dir(Path(tmp_dir) / 'missing-layout')
        except SystemExit as exc:
            assert 'could not locate zig binary' in str(exc)
        else:
            raise AssertionError('expected missing zig binary layout to fail')

    try:
        normalize_os('plan9')
    except SystemExit:
        pass
    else:
        raise AssertionError('expected normalize_os to reject unsupported OS')

    try:
        normalize_arch('sparc')
    except SystemExit:
        pass
    else:
        raise AssertionError('expected normalize_arch to reject unsupported architecture')

    try:
        resolve_target(sample_index, 'stable', 'x86_64', 'linux')
    except SystemExit:
        pass
    else:
        raise AssertionError('expected resolve_target to reject unknown channel')

    try:
        resolve_target(sample_index, 'master', 'loongarch64', 'linux')
    except SystemExit:
        pass
    else:
        raise AssertionError('expected resolve_target to reject unknown target')

    print('ZIG_INSTALL_SELF_TEST=pass')
    print('ZIG_INSTALL_SELF_TEST_CASE_COUNT=33')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description='Install Zig from the official Zig download index or a direct version archive URL.')
    parser.add_argument('--channel', default=None, help='Channel or version key from ziglang.org/download/index.json, or an explicit Zig version string. Defaults to scripts/zigux/zig-toolchain-policy.json when available, otherwise master.')
    parser.add_argument('--dest', default='.zig-toolchain', help='Install root directory')
    parser.add_argument('--system', help='Override detected OS key (linux, macos, windows)')
    parser.add_argument('--arch', help='Override detected architecture key (x86_64, aarch64, x86)')
    parser.add_argument('--resolve-only', action='store_true', help='Resolve and print the chosen archive without downloading')
    parser.add_argument('--self-test', action='store_true', help='Run built-in target-resolution coverage without downloading')
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    policy_channel = load_policy_channel()
    channel = args.channel or policy_channel
    system_key = args.system or normalize_os(platform.system())
    arch_key = args.arch or normalize_arch(platform.machine())

    index = load_index(channel)
    target_key, version, tarball_url = resolve_target(index, channel, arch_key, system_key)
    expected_archive_sha256 = None
    if channel == policy_channel:
        expected_archive_sha256 = load_policy_archive_sha256(TOOLCHAIN_POLICY, target_key)

    print(f'ZIG_INSTALL_CHANNEL={channel}')
    print(f'ZIG_INSTALL_VERSION={version}')
    print(f'ZIG_INSTALL_TARGET={target_key}')
    print(f'ZIG_INSTALL_URL={tarball_url}')
    if expected_archive_sha256 is not None:
        print(f'ZIG_INSTALL_EXPECTED_ARCHIVE_SHA256={expected_archive_sha256}')
    if args.resolve_only:
        print('ZIG_INSTALL_STATUS=resolved')
        return 0

    install_root = Path(args.dest)
    install_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='zigux_install_zig_') as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        archive_name = tarball_url.rsplit('/', 1)[-1]
        archive_path = tmpdir / archive_name
        copy_url_to_file(tarball_url, archive_path)
        if expected_archive_sha256 is not None:
            actual_archive_sha256 = verify_archive_sha256(archive_path, expected_archive_sha256)
            print(f'ZIG_INSTALL_ARCHIVE_SHA256={actual_archive_sha256}')
            print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=verified')
        else:
            print('ZIG_INSTALL_ARCHIVE_SHA256_STATUS=unverified')

        extracted_root = extract_archive(archive_path, tmpdir / 'extract')
        final_root = install_root / extracted_root.name
        if final_root.exists():
            shutil.rmtree(final_root)
        shutil.copytree(extracted_root, final_root)

    bin_dir = resolve_bin_dir(final_root)
    append_github_path(bin_dir)
    print(f'ZIG_INSTALL_PATH={bin_dir.resolve()}')
    print('ZIG_INSTALL_STATUS=pass')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
