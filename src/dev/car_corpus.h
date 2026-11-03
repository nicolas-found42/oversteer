/* Deterministic physics fixtures, independent of the source-model artwork catalog.
 * Authored archetypes and sweeps are built locally; sampled cases are frozen numeric
 * snapshots so changes to rendering never select different simulation fixtures. */
#ifndef OVERSTEER_CAR_CORPUS_H
#define OVERSTEER_CAR_CORPUS_H

#include <stdbool.h>
#include <stddef.h>

#include "physics/vehicle.h"

typedef enum {
    CAR_CORPUS_ARCHETYPE = 0,
    CAR_CORPUS_SWEEP,
    CAR_CORPUS_SAMPLED,
    CAR_CORPUS_GROUP_COUNT
} CarCorpusGroup;

/* Total vehicles. Stable for a given build. */
int car_corpus_count(void);

/* Write vehicle `index` into `out`. Pure: the same index always yields the same spec, and no
 * ordering of calls changes the result. Returns false for an out-of-range index or NULL out.
 * The result is not guaranteed valid by construction — the `corpus` scenario asserts
 * vehicle_spec_is_valid() over every entry, which is how a bad registry range gets caught. */
bool car_corpus_spec(int index, VehicleSpec *out);

CarCorpusGroup car_corpus_group(int index);
const char *car_corpus_group_name(CarCorpusGroup group);

/* A stable, filesystem-safe identifier, e.g. "sweep_wheel_radius_2". Formatted into the
 * caller's buffer rather than returned as a pointer so there is no shared static state. */
void car_corpus_id(int index, char *buf, size_t cap);

/* One human-readable line naming what makes this entry what it is, e.g.
 * "body.cg_to_rear = 1.200 (step 2/5)". Used in the contact sheet and in test failures. */
void car_corpus_describe(int index, char *buf, size_t cap);

/* The registry key a sweep entry varies, or NULL for non-sweep entries. Used to describe physics parameter coverage. */
const char *car_corpus_sweep_key(int index);

/* Build a physics sweep probe using the same exclusion window as the fixture row. */
int car_corpus_sweep_steps(void);
bool car_corpus_sweep_probe(const char *key, int step, VehicleSpec *out);

#endif /* OVERSTEER_CAR_CORPUS_H */
