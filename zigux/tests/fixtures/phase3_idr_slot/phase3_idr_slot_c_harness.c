// SPDX-License-Identifier: GPL-2.0-only
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define MAX_ERRNO ((uintptr_t)4095)
#define VALUE_TAG_MASK ((uintptr_t)0x1)
#define ERR_FLOOR ((uintptr_t)(intptr_t)-((intptr_t)MAX_ERRNO))

static uintptr_t safe_inline_limit(void) {
    return (ERR_FLOOR >> 1) - 1;
}

static uintptr_t make_value(uintptr_t value) {
    return (value << 1) | VALUE_TAG_MASK;
}

static bool is_err_value(uintptr_t raw) {
    return raw >= ERR_FLOOR;
}

static bool is_value(uintptr_t raw) {
    return (raw & VALUE_TAG_MASK) == VALUE_TAG_MASK && !is_err_value(raw);
}

static const char *kind_name(uintptr_t raw) {
    if (raw == 0) {
        return "empty";
    }
    if (is_err_value(raw)) {
        return "err_ptr";
    }
    if (is_value(raw)) {
        return "internal_value";
    }
    return "pointer_like";
}

static void write_optional_signed(intptr_t value, bool present) {
    if (!present) {
        fputs("null", stdout);
        return;
    }
    printf("%" PRIdPTR, value);
}

static void write_optional_uintptr(uintptr_t value, bool present) {
    if (!present) {
        fputs("null", stdout);
        return;
    }
    printf("%" PRIuPTR, value);
}

static void write_case(const char *name, uintptr_t raw, int trailing_comma) {
    const bool tagged_internal = is_err_value(raw) || is_value(raw);
    const bool internal_value = is_value(raw);
    const bool err_value = is_err_value(raw) && raw != 0;
    const bool pointer_like = !internal_value && !err_value && raw != 0;

    printf(
        "    {\n"
        "      \"name\": \"%s\",\n"
        "      \"kind\": \"%s\",\n"
        "      \"raw_hex\": \"0x%" PRIxPTR "\",\n"
        "      \"raw_decimal\": \"%" PRIuPTR "\",\n"
        "      \"is_tagged_internal\": %s,\n"
        "      \"decoded_internal_value\": ",
        name,
        kind_name(raw),
        raw,
        raw,
        tagged_internal ? "true" : "false");
    write_optional_uintptr(raw >> 1, internal_value);
    fputs(",\n      \"decoded_error\": ", stdout);
    write_optional_signed((intptr_t)raw, err_value);
    fputs(",\n      \"pointer_raw\": ", stdout);
    write_optional_uintptr(raw, pointer_like);
    fputs("\n    }", stdout);
    if (trailing_comma) {
        fputs(",", stdout);
    }
    fputc('\n', stdout);
}

int main(void) {
    const uintptr_t inline_limit_raw = make_value(safe_inline_limit());

    printf(
        "{\n"
        "  \"word_bits\": %zu,\n"
        "  \"safe_inline_limit\": %" PRIuPTR ",\n"
        "  \"safe_inline_limit_raw_hex\": \"0x%" PRIxPTR "\",\n"
        "  \"cases\": [\n",
        sizeof(uintptr_t) * 8u,
        safe_inline_limit(),
        inline_limit_raw);

    write_case("null", 0, 1);
    write_case("pointer_like", 64, 1);
    write_case("internal_zero", make_value(0), 1);
    write_case("internal_small", make_value(29), 1);
    write_case("internal_limit", inline_limit_raw, 1);
    write_case("gap_before_err_floor", ERR_FLOOR - 1, 1);
    write_case("err_enomem", (uintptr_t)(intptr_t)-12, 1);
    write_case("err_max", (uintptr_t)(intptr_t)-4095, 0);

    fputs("  ]\n}\n", stdout);
    return 0;
}
