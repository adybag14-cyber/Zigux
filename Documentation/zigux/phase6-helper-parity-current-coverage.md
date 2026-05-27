# Phase 6 Helper Parity Current Coverage

This note records the exact current-master helper coverage snapshot for the existing Phase 6 helper parity catalog.

- surveyed head: `current-master-readback-2026-05-27`
- lane scope: exact helper coverage verification for the current Phase 6 parity packet
- parent parity catalog: `Documentation/zigux/phase6-helper-parity-catalog.md`
- machine-readable snapshot: `zigux/tests/phase6_helper_current_coverage_manifest.json`
- roadmap-backed helper anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`

## Coverage Verdict

All four roadmap-backed Phase 6 helper destinations are present on current `master`, and each landed Zig helper carries embedded test coverage in the helper body itself. Each helper also keeps a focused Phase 6 replay plus a dedicated parity, perf, or route-check companion inside the broader Phase 6 packet.

## Current Snapshot

| helper | roadmap anchor | Zig helper blob | embedded helper tests | focused replay | exact companion coverage |
| --- | --- | --- | ---: | --- | --- |
| `base64` | `lib/base64.c` | `lib/base64.zig` `844a091999aab9a1d78f90d7719450b4e590e962` | 20 | `zigux/tests/phase6_base64.zig` | `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts/zigux/check-phase6-base64-c-parity.py` |
| `bsearch` | `lib/bsearch.c` | `lib/bsearch.zig` `916a87eb91c0c3e620cf6e85c018180cdf772e58` | 11 | `zigux/tests/phase6_bsearch.zig` | `zigux/tests/phase6_bsearch_perf.zig`, `zigux/tests/phase6_bsearch_c_parity.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_c_harness.c`, `scripts/zigux/check-phase6-bsearch-c-parity.py` |
| `checksum` | `lib/checksum.c` | `lib/checksum.zig` `1cda59b1bd4e5d4e9989d2b9f4e84be62b8ccb7e` | 12 | `zigux/tests/phase6_checksum.zig` | `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, `scripts/zigux/check-phase6-checksum-c-parity.py` |
| `hexdump` | `lib/hexdump.c` | `lib/hexdump.zig` `0fc9534ddf7e020ab00f981d5762b1703430170c` | 17 | `zigux/tests/phase6_hexdump.zig` | `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_hexdump_perf_matrix.zig`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py` |

## Helper Evidence

### base64

- helper blob: `lib/base64.zig` at `844a091999aab9a1d78f90d7719450b4e590e962`
- embedded helper test count: `20`
- selected embedded tests:
  - `variant-pinned convenience helpers mirror the generic api`
  - `encode and decode sweep every one-byte and two-byte tail across variants and padding modes`
  - `decode reverse maps classify every byte across all variants`
- focused replay and exact companions:
  - `zigux/tests/phase6_base64.zig`
  - `zigux/tests/phase6_base64_perf.zig`
  - `zigux/tests/phase6_base64_c_parity.zig`
  - `zigux/tests/fixtures/phase6_base64_c_harness.c`
  - `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`
  - `zigux/tests/phase6_base64_c_casegen.zig`
  - `scripts/zigux/check-phase6-base64-c-parity.py`

### bsearch

- helper blob: `lib/bsearch.zig` at `916a87eb91c0c3e620cf6e85c018180cdf772e58`
- embedded helper test count: `11`
- selected embedded tests:
  - `typed and raw searches support duplicate spans and descending C ABI pointers`
  - `native std.math.Order comparator pointers keep duplicate spans and insertion points aligned`
  - `mutable wrappers keep write-through aliases with runtime-selected c abi comparator pointers`
- focused replay and exact companions:
  - `zigux/tests/phase6_bsearch.zig`
  - `zigux/tests/phase6_bsearch_perf.zig`
  - `zigux/tests/phase6_bsearch_c_parity.zig`
  - `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`
  - `zigux/tests/phase6_bsearch_c_abi_budget.zig`
  - `zigux/tests/fixtures/phase6_bsearch_c_harness.c`
  - `scripts/zigux/check-phase6-bsearch-c-parity.py`

### checksum

- helper blob: `lib/checksum.zig` at `1cda59b1bd4e5d4e9989d2b9f4e84be62b8ccb7e`
- embedded helper test count: `12`
- selected embedded tests:
  - `partial and compute match reference accumulation across seeded odd payloads`
  - `pseudo-header helpers match direct checksum recomputation over pseudo-header bytes and payload`
  - `ipFastCsum stays aligned with compute across aligned IPv4 headers`
- focused replay and exact companions:
  - `zigux/tests/phase6_checksum.zig`
  - `zigux/tests/phase6_checksum_perf.zig`
  - `zigux/tests/phase6_checksum_c_parity.zig`
  - `zigux/tests/fixtures/phase6_checksum_c_harness.c`
  - `scripts/zigux/check-phase6-checksum-c-parity.py`

### hexdump

- helper blob: `lib/hexdump.zig` at `0fc9534ddf7e020ab00f981d5762b1703430170c`
- embedded helper test count: `17`
- selected embedded tests:
  - `hexDumpToBuffer matches the kernel-style 16-byte line output`
  - `hexDumpToBuffer uses native-endian grouping for 2, 4, and 8 byte groups`
  - `hexDumpToBuffer follows kernel fixture normalization cases`
- focused replay and exact companions:
  - `zigux/tests/phase6_hexdump.zig`
  - `zigux/tests/phase6_hexdump_perf.zig`
  - `zigux/tests/phase6_hexdump_perf_matrix.zig`
  - `scripts/zigux/check-phase6-hexdump-packet.py`
  - `scripts/zigux/check-phase6-hexdump-route.py`

Reopen this exact-current-coverage note only when one of the four roadmap-backed helper blobs changes, the embedded helper test counts change, or the focused replay and parity companions drift on `master`.
