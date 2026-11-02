/*
 * profile.h — zone instrumentation with two backends and no mandatory dependency.
 *
 *   default            the macros compile to nothing at all
 *   -DOVERSTEER_PROFILE   built-in accumulating timers; a summary is printed at shutdown
 *   -DOVERSTEER_TRACY     zones are forwarded to Tracy (third_party/tracy must be present)
 *
 * Usage is a matched pair, which is what lets the same call sites serve both backends:
 *
 *     OVERSTEER_ZONE_BEGIN(update, "FixedUpdate");
 *     ...
 *     OVERSTEER_ZONE_END(update);
 *
 * `make profile` picks the backend for you: Tracy when it is vendored, the built-in timers
 * otherwise. Neither is ever part of a release build.
 *
 * Zone names must be string literals with static lifetime — both backends key on the
 * pointer, not on the characters.
 */
#ifndef OVERSTEER_PROFILE_H
#define OVERSTEER_PROFILE_H

#include <stdint.h>
#include <stdio.h>

#if defined(OVERSTEER_TRACY)

#include "tracy/TracyC.h"

#define OVERSTEER_ZONE_BEGIN(handle, name) TracyCZoneN(handle, name, 1)
#define OVERSTEER_ZONE_END(handle) TracyCZoneEnd(handle)
#define OVERSTEER_FRAME_MARK() TracyCFrameMark
#define OVERSTEER_PROFILE_REPORT(out) ((void)(out))

#elif defined(OVERSTEER_PROFILE)

/* Monotonic nanoseconds since an arbitrary origin. */
uint64_t profile_now_ns(void);
void profile_zone_end(const char *name, uint64_t startedNs);
void profile_frame_mark(void);
void profile_report(FILE *out);

#define OVERSTEER_ZONE_BEGIN(handle, name) \
    const char *handle##_name = (name); \
    const uint64_t handle##_started = profile_now_ns()

#define OVERSTEER_ZONE_END(handle) profile_zone_end(handle##_name, handle##_started)
#define OVERSTEER_FRAME_MARK() profile_frame_mark()
#define OVERSTEER_PROFILE_REPORT(out) profile_report(out)

#else

#define OVERSTEER_ZONE_BEGIN(handle, name) ((void)0)
#define OVERSTEER_ZONE_END(handle) ((void)0)
#define OVERSTEER_FRAME_MARK() ((void)0)
#define OVERSTEER_PROFILE_REPORT(out) ((void)(out))

#endif

#endif /* OVERSTEER_PROFILE_H */
