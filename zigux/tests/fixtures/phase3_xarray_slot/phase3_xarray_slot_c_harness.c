#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#define MAX_ERRNO ((uintptr_t)4095)
#define VALUE_TAG_MASK ((uintptr_t)0x1)

static uintptr_t err_floor(void) {
    return (uintptr_t)(intptr_t)-(intptr_t)MAX_ERRNO;
}

static bool is_err_value(uintptr_t raw) {
    return raw >= err_floor();
}

static bool is_value(uintptr_t raw) {
    return (raw & VALUE_TAG_MASK) == VALUE_TAG_MASK && !is_err_value(raw);
}

static uintptr_t safe_inline_limit(void) {
    return (err_floor() >> 1) - 1;
}

static uintptr_t make_value(uintptr_t value) {
    return (value << 1) | VALUE_TAG_MASK;
}

static const char *kind_name(uintptr_t raw) {
    if (raw == 0) {
        return "null";
    }
    if (is_value(raw)) {
        return "xa_value";
    }
    if (is_err_value(raw)) {
        return "err_ptr";
    }
    return "pointer_like";
}

static void write_optional_signed(intptr_t value, bool present) {
    if (present) {
        printf("%" PRIdPTR, value);
        return;
    }
    printf("null");
}

static void write_optional_unsigned(uintptr_t value, bool present) {
    if (present) {
        printf("%" PRIuPTR, value);
        return;
    }
    printf("null");
}

static void write_case(const char *name, uintptr_t raw, int trailing_comma) {
    const bool is_null = raw == 0;
    const bool value = is_value(raw);
    const bool err = is_err_value(raw);
    const bool pointer = !is_null && !value && !err;

    printf(
        "    {\n"
        "      \"name\": \"%s\",\n"
        "      \"kind\": \"%s\",\n"
        "      \"raw_hex\": \"0x%" PRIxPTR "\",\n"
        "      \"raw_decimal\": \"%" PRIuPTR "\",\n"
        "      \"is_null\": %s,\n"
        "      \"is_value\": %s,\n"
        "      \"is_err\": %s,\n"
        "      \"is_pointer\": %s,\n"
        "      \"is_tagged_internal\": %s,\n"
        "      \"decoded_error\": ",
        name,
        kind_name(raw),
        raw,
        raw,
        is_null ? "true" : "false",
        value ? "true" : "false",
        err ? "true" : "false",
        pointer ? "true" : "false",
        (value || err) ? "true" : "false");
    write_optional_signed((intptr_t)raw, err);
    printf(",\n      \"decoded_value\": ");
    write_optional_unsigned(raw >> 1, value);
    printf(",\n      \"pointer_raw\": ");
    write_optional_unsigned(raw, pointer);
    printf("\n    }");
    if (trailing_comma) {
        printf(",");
    }
    printf("\n");
}

int main(void) {
    const uintptr_t inline_limit = safe_inline_limit();
    const uintptr_t inline_limit_raw = make_value(inline_limit);

    printf(
        "{\n"
        "  \"word_bits\": %zu,\n"
        "  \"safe_inline_limit\": %" PRIuPTR ",\n"
        "  \"safe_inline_limit_raw_hex\": \"0x%" PRIxPTR "\",\n"
        "  \"cases\": [\n",
        sizeof(uintptr_t) * 8,
        inline_limit,
        inline_limit_raw);

    write_case("null", 0, 1);
    write_case("pointer_like", 64, 1);
    write_case("inline_small", make_value(29), 1);
    write_case("inline_limit", inline_limit_raw, 1);
    write_case("gap_before_err_floor", err_floor() - 1, 1);
    write_case("err_enomem", (uintptr_t)(intptr_t)-12, 1);
    write_case("err_max", (uintptr_t)(intptr_t)-4095, 0);

    printf("  ]\n}\n");
    return 0;
}
