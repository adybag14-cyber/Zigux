# comment only
# still no targets
# rustc tail keeps going \
still comment with include/generated/autoconf.h sample2.so shared\#config.h \
and shared\:config.h sample.rlib sample.rmeta stay invisible too \
plus escaped\ space-config.h sample_dependency_continuation_dep.so shared\#config.h \
and include/generated/autoconf.h sample_comment_continuation_dep.so still stay invisible \
while shared\:config.h escaped\ space-config.h sample_comment_continuation_dep.so sample.rlib remain comment-only too \
before sample_missing_dep.h include/generated/autoconf.h shared\#config.h still vanish inside the continued comment \
while sample2.so sample.rmeta sample.rlib escaped\ space-config.h shared\:config.h \
and include/generated/autoconf.h sample_dependency_continuation_dep.so shared\#config.h still remain invisible
