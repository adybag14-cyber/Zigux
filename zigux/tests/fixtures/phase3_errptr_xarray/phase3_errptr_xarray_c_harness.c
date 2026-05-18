#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

#define MAX_ERRNO ((uintptr_t)4095)
#define VALUE_TAG_MASK ((uintptr_t)0x1)

static uintptr_t err_floor(void) {
    return (uintptr_t)(-(intptr_t)MAX_ERRNO);
}

static uintptr_t safe_inline_limit(void) {
    return (err_floor() >> 1) - 1;
}

static uintptr_t make_value(uintptr_t value) {
    return (value << 1) | VALUE_TAG_MASK;
}

static int is_err_value(uintptr_t raw) {
    return raw >= err_floor();
}

static int is_value(uintptr_t raw) {
    return (raw & VALUE_TAG_MASK) == VALUE_TAG_MASK && !is_err_value(raw);
}

static intptr_t to_error_code(uintptr_t raw) {
    return (intptr_t)raw;
}

static uintptr_t to_value(uintptr_t raw) {
    return raw >> 1;
}

static const char *kind_for(uintptr_t raw) {
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

static void write_case(const char *name, uintptr_t raw, int trailing_comma) {
    char raw_hex[2 + sizeof(uintptr_t) * 2 + 1];
    char raw_decimal[32];
    const int err = is_err_value(raw);
    const int value = is_value(raw);

    snprintf(raw_hex, sizeof(raw_hex), "0x%" PRIxPTR, raw);
    snprintf(raw_decimal, sizeof(raw_decimal), "%" PRIuPTR, raw);

    printf("    {\n");
    printf("      \"name\": \"%s\",\n", name);
    printf("      \"kind\": \"%s\",\n", kind_for(raw));
    printf("      \"raw_hex\": \"%s\",\n", raw_hex);
    printf("      \"raw_decimal\": \"%s\",\n", raw_decimal);
    printf("      \"is_err\": %s,\n", err ? "true" : "false");
    printf("      \"is_value\": %s,\n", value ? "true" : "false");
    printf("      \"decoded_error\": ");
    if (err) {
        printf("%jd", (intmax_t)to_error_code(raw));
    } else {
        printf("null");
    }
    printf(",\n");
    printf("      \"decoded_value\": ");
    if (value) {
        printf("%" PRIuPTR, to_value(raw));
    } else {
        printf("null");
    }
    printf("\n");
    printf("    }");
    if (trailing_comma) {
        printf(",");
    }
    printf("\n");
}

int main(void) {
    const uintptr_t inline_limit_raw = make_value(safe_inline_limit());

    printf("{\n");
    printf("  \"word_bits\": %zu,\n", sizeof(uintptr_t) * 8U);
    printf("  \"safe_inline_limit\": %" PRIuPTR ",\n", safe_inline_limit());
    printf("  \"safe_inline_limit_raw_hex\": \"0x%" PRIxPTR "\",\n", inline_limit_raw);
    printf("  \"cases\": [\n");

    write_case("null", 0, 1);
    write_case("pointer_like", 64, 1);
    write_case("inline_small", make_value(29), 1);
    write_case("inline_limit", inline_limit_raw, 1);
    write_case("gap_before_err_floor", err_floor() - 1, 1);
    write_case("err_top", (uintptr_t)(intptr_t)-1, 1);
    write_case("err_enomem", (uintptr_t)(intptr_t)-12, 1);
    write_case("err_max", (uintptr_t)(intptr_t)-4095, 0);

    printf("  ]\n");
    printf("}\n");
    return 0;
}
