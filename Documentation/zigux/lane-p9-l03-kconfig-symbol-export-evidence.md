# Lane P9-L03 Kconfig Symbol Export Evidence

This note records bounded verification evidence for the current Kconfig symbol/config behavior used by the `P9-L03` symbol export parity lane.

It is not a phase-closure document. It only captures the exact current behavior visible in the repo on 2026-05-21.

## Repo Anchors

- `scripts/zigux/kconfig/confdata_bridge.zig`
- `zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names.config`
- `zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names_expected.json`
- `zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment.config`
- `zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment_expected.json`

## Current Symbol/Config Behavior

### Empty `CONFIG_` names are ignored

The current parser only accepts names that start with `CONFIG_` and contain at least one additional alphanumeric or underscore character.

Relevant source behavior in `confdata_bridge.zig`:
- `isConfigSymbol` returns `false` when `name.len <= config_prefix.len`
- `parseConfig` skips assignments whose left-hand side fails `isConfigSymbol`
- `parseUnsetSymbol` also rejects `# CONFIG_ is not set` because the empty suffix is not a valid symbol name

Fixture input:

```text
CONFIG_=y
# CONFIG_ is not set
CONFIG_VALID=m
```

Observed runtime output from a local compile of the fetched `confdata_bridge.zig` slice with Zig `0.17.0-dev.87+9b177a7d2`:

```json
{"counts":{"set":1,"unset":0},"entries":[{"name":"CONFIG_VALID","kind":"tristate","value":"m"}]}
```

This matches `zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names_expected.json` exactly.

### Malformed quoted duplicate assignments do not overwrite the last good state

The current parser detects malformed quoted values with:
- `raw_value[0] == '"' and closing_quote_index == null`
- `if (malformed_quoted_value) continue;`

That means a later malformed quoted duplicate is ignored and the most recent valid value remains in place.

Fixture input:

```text
CONFIG_ALPHA="stable"
CONFIG_ALPHA="unterminated
# CONFIG_DEBUG is not set
CONFIG_DEBUG="broken
CONFIG_SUFFIX="zigux"tail
CONFIG_GAMMA="still-broken
CONFIG_BETA=y
```

Observed runtime output from the same local compile:

```json
{"counts":{"set":3,"unset":1},"entries":[{"name":"CONFIG_ALPHA","kind":"string","value":"stable"},{"name":"CONFIG_DEBUG","kind":"unset","value":"n"},{"name":"CONFIG_SUFFIX","kind":"string","value":"zigux"},{"name":"CONFIG_BETA","kind":"tristate","value":"y"}]}
```

This matches `zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment_expected.json` exactly.

## Validation Performed

- compiled the fetched `scripts/zigux/kconfig/confdata_bridge.zig` source with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2`
- ran the compiled binary against the two fixture inputs above
- checked that the emitted JSON matched the repo's current expected JSON byte-for-byte
- confirmed the parser slice is at least compile-valid in isolation

## Limits

A full in-tree checkout was not available in the workspace, so this run verified the exact fetched parser slice and fixture inputs locally rather than running the full repo harness.

## Next Bounded Step

Extend this evidence from current config parsing behavior to any future export-facing symbol packet or ABI surface once the lane gains a direct symbol-export artifact beyond the existing Kconfig bridge fixtures.
