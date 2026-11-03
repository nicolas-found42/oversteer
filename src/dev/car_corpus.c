/* Historical physics fixtures: authored archetypes, parameter sweeps and frozen
 * samples. Independent of the source-model artwork catalog. */
#include "dev/car_corpus.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dev/dev_params.h"
#include "physics/vehicle.h"

#include "dev/car_corpus_internal.h"

/* ------------------------------------------------------------------------------ sweeps --
 *
 * Eight axes, five steps each = 40 vehicles. Each sweep varies EXACTLY ONE registry key;
 * all other parameters stay at stock. The varied key is documented beside each axis.
 */
#define SWEEP_AXES 8
#define SWEEP_STEPS 5

/* One sweep axis. A row is five cars that differ in this key and in nothing else. */
typedef struct {
    const char *key; /* the ONE registry key this row varies */
    // cppcheck-suppress unusedStructMember
    const char *note; /* the visual dimension the row demonstrates */
} SweepAxis;

/* WHY TIRE ASPECT RATIO IS NOT ONE OF THESE AXES.
 *
 * Tire aspect ratio is an obvious candidate for a sweep axis — it changes the drawn tire
 * diameter directly — and it is deliberately not here. That is a measured decision, not an
 * omission.
 *
 * Every PAIR of corpus vehicles has to clear three floors at once: >= 3% of union-silhouette
 * pixels differing, signature L2 >= 0.25, and signature L-infinity >= 0.08 m. Adjacent steps
 * of a five-step sweep are the tightest pairs in the whole fleet, so a sweep axis has to move
 * roughly a fifth of its range past all three floors, four times over.
 *
 * A tire's drawn diameter is rim + 2 * section * aspect, and aspect touches essentially
 * nothing else: it moves the tire diameter, the sidewall band inside it, and the arch drawn
 * around it — two of four wheels, on a shape seen from above. On the stock 225/45R17 the
 * registry's whole 25%..80% span moves the diameter by 2 * 0.225 * 0.55 = 0.2475 m, i.e.
 * 0.062 m per step: below the 0.08 m one-pixel floor before anything else is considered.
 * Widening the registry to close that would need ~80 points of aspect (25..105), which is not
 * a tire that exists.
 *
 * Building the row on a wide-tire, open-wheel base does clear L-infinity — a 355 mm section
 * gives 0.098 m per step — and was tried. It still fails the other two floors, and this is
 * arithmetic rather than a tuning problem: the pixel metric is a FRACTION of a shared
 * silhouette, and L2 is dominated by how MANY components move. Aspect ratio moves two. Even
 * with the body shrunk to the registry's minimum in every dimension, the measured figures
 * were 2.1% of pixels and L2 = 0.107 against floors of 3% and 0.25.
 *
 * So the axis is covered where it can be honest: `tire.aspect_front` and `tire.aspect_rear`
 * are both designated visual drivers in the `car-visual` sensitivity table, perturbed across
 * their full declared range — a 45% change in tire diameter, which clears the sensitivity
 * floors comfortably and is plainly visible on the contact sheet. What it cannot do is carry
 * five mutually distinct cars, and asserting otherwise would mean lowering a corpus-wide
 * threshold to accommodate one row.
 */
static const SweepAxis kSweepAxes[SWEEP_AXES] = {
    { "mass.engine_x", "engine station: CG, layout read, hood bulge" },
    { "body.wheelbase", "axle span and the body length that follows it" },
    { "body.width_overall", "silhouette width and fender flare" },
    { "body.track_rear", "rear stance: hub stations, arches, and wheel containment" },
    { "body.front_overhang", "nose length ahead of the front axle" },
    { "body.track_front", "front stance: track against body width" },
    { "body.shoulder_x", "station of maximum width: where the body is widest" },
    { "body.rear_overhang", "tail length behind the rear axle" },
};

/* WHY body.backlight_x LEFT THIS TABLE, AND WHY body.bed_length DID NOT REPLACE IT.
 *
 * Both are the tire-aspect story above, told twice more.
 *
 * backlight_x used to carry TWO visual jobs: the rear glass station, and — through the old
 * inference — the pickup bed. The second job was a bug (it grew beds on 74 non-trucks) and
 * body.bed_length replaced it. Stripped of the bed, the axis moves only cabin length, roof
 * panel and glass band, and the row stopped clearing the floors: sweep_body_backlight_x_3
 * measured L-infinity 0.0700 m and L2 0.1071 against sweep_mass_engine_x_0, versus floors of
 * 0.08 m and 0.25. The axis genuinely does less than it used to.
 *
 * bed_length was the obvious replacement and does not work either, for the opposite reason.
 * Its four upper steps are strongly distinct (measured bed areas 133 / 209 / 285 / 380 px),
 * but its default is 0 — most vehicles have no bed — so the generator's exclusion window puts
 * the FIRST step at 0.1875 m. At 13.2 px/m that is a 2.5 px lip that renders as nothing, so
 * step 0 came out byte-identical to the stock baseline: 0.00% of pixels differing. Widening
 * the range cannot help, because the exclusion window is half a grid step and scales with it.
 * A bed that short is not a configuration a real vehicle has.
 *
 * body.rear_overhang takes the slot instead: 0.2..2.5 m is 0.575 m per step, and it moves
 * length, both tail hull stations and the tail taper together, so it clears the pixel and L2
 * floors with room to spare.
 *
 * Both displaced keys stay covered where they can be honest — `body.backlight_x` and
 * `body.bed_length` are designated visual drivers in the `car-visual` sensitivity table,
 * perturbed across their whole declared registry range.
 */

/* WHY aero.lift_rear LEFT THIS TABLE IN PHASE B, AND WHY body.shoulder_x TOOK THE SLOT.
 *
 * The same story a third time, caused by a deliberate change rather than by a bug. Before
 * Phase B the tail taper read the SIGNED rear lift coefficient, so this axis moved both the
 * wing and the whole rear silhouette. Phase B made the silhouette endpoints explicit
 * ([identity] body.nose_width / body.tail_width) and retired the derived taper, which is what
 * closed the measured 3x tail-closure gap — and left aero.lift_rear moving only the wing
 * bolted to the deck. Measured with `oversteer_tests --measure-sweep aero.lift_rear` after that
 * change, its adjacent steps read:
 *
 *     pair 0-1  pixels 0.0313  L2 0.2447  Linf 0.2337 m   (L2 below the 0.25 floor)
 *     pair 1-2  pixels 0.0552  L2 0.2574  Linf 0.2338 m
 *     pair 2-3  pixels 0.0356  L2 0.2447  Linf 0.2337 m   (L2 below the floor)
 *     pair 3-4  pixels 0.0280  L2 1.2688  Linf 1.2538 m   (pixels below the 0.030 floor)
 *
 * Three of four adjacent pairs miss a floor. A wing is two rectangles over the deck: it cannot
 * carry five mutually distinct cars on its own, and Phase F is where wing span and chord become
 * explicit dimensions rather than a coefficient's shadow.
 *
 * body.shoulder_x takes the slot because it was measured to clear all three floors on every
 * adjacent pair:
 *
 *     pair 0-1  pixels 0.1068  L2 1.7659  Linf 1.7500 m
 *     pair 1-2  pixels 0.0710  L2 0.7686  Linf 0.7500 m
 *     pair 2-3  pixels 0.0573  L2 0.7693  Linf 0.7500 m
 *     pair 3-4  pixels 0.0363  L2 0.7604  Linf 0.7500 m
 *
 * It moves the maximum-width station along the body, so both hull sections change length at
 * once and several stations move together — the property a single appendage dimension lacks.
 *
 * THE OTHER TWO PHASE B CANDIDATES CANNOT BE SWEPT AT ALL, and the reason is the identity
 * itself rather than the fidelity budget. body.nose_width and body.tail_width are hull
 * endpoints, and vehicle_spec_is_valid() rejects an endpoint wider than widthOverallM: an
 * endpoint past the body's maximum width would falsify both the endpoint identity and the
 * shoulder's claim to be the widest station. The stock body is 1.70 m wide while the declared
 * registry ranges reach 2.2 m and 2.4 m, so the generated rows die on validity:
 *
 *     body.nose_width  step 3 = 1.90625 m  -> invalid spec
 *     body.tail_width  step 2 = 1.80000 m  -> invalid spec
 *
 * A sweep row varies exactly one key, so widening body.width_overall alongside is not
 * available, and narrowing the registry range to fit one base would misreport what the
 * parameter can express on a 2.4 m bus. Both keys are therefore designated visual drivers in
 * the `car-visual` sensitivity table instead, where they are perturbed across their whole
 * declared range from stock, and the archetypes exercise them as authored proportions.
 */

/* WHY body.height_overall LEFT THIS TABLE IN PHASE C, AND WHY body.track_rear TOOK THE SLOT.
 *
 * The aero.lift_rear story a fourth time, and again caused by a deliberate change rather than
 * by a bug. Before Phase C the roof plane was INFERRED from overall height: a taller body
 * grew a larger roof share of the plan area, so this axis moved the roof panel, the glass
 * band and the side-window run together. Phase C made those stations explicit
 * ([identity] body.roof_start_x / roof_end_x / roof_width, plus the two rakes), which is what
 * lets a bus and a coupe declare their greenhouses rather than deriving them from a single
 * scalar — and left body.height_overall moving only the `height_visual` signature component.
 * Measured with `oversteer_tests --measure-sweep body.height_overall` after that change:
 *
 *     pair 0-1  pixels 0.0521  L2 0.5806  Linf 0.4185 m
 *     pair 1-2  pixels 0.0295  L2 0.2582  Linf 0.1793 m   (pixels below the 0.030 floor)
 *     pair 2-3  pixels 0.0446  L2 0.2645  Linf 0.1793 m
 *     pair 3-4  pixels 0.0718  L2 0.2720  Linf 0.1793 m
 *
 * and step 0 measured 0.0226 of pixels against archetype_00_stock_baseline — the pair the
 * corpus scenario reported. One component moving cannot separate five cars from a fleet of a
 * hundred, however large that one component's excursion is: the pixel metric is a FRACTION of
 * a shared silhouette, and above the roof line a taller body adds no plan area at all.
 *
 * FOUR CANDIDATES WERE MEASURED FOR THE SLOT AND REJECTED BEFORE ONE PASSED.
 *
 * The three Phase C greenhouse keys are the obvious replacements, being the keys that took
 * height_overall's jobs, and none of them can carry a row:
 *
 *   - body.roof_start_x cannot even be generated. Its declared range is -4..4 m so the axis
 *     can express a roof on a bus, but step 0 puts the forward roof edge at -4 m, behind the
 *     tail of the stock car, and vehicle_spec_is_valid() rejects it. A sweep row varies
 *     exactly one key, so there is no way to grow the body to fit the station.
 *   - body.windscreen_rake moves one component, windscreen_length, and misses every floor on
 *     all four adjacent pairs: the widest is pair 3-4 at 0.0200 of pixels, L2 0.2676, and the
 *     largest excursion anywhere in the row is 0.0330 against stock. A plan projection of a
 *     raked screen is a band a few pixels deep; it cannot separate five cars.
 *   - body.cabin_rows has three legal states, 1..3. Five steps over three values duplicate:
 *     steps 0 and 1 measured 0.0000 of pixels apart, as did steps 3 and 4. An integer key
 *     with fewer states than the sweep has steps fails by construction, not by margin.
 *
 *   - body.cowl_x is the fourth, and its failure is the most instructive. It looked certain —
 *     it is the windscreen station, so cabin length, the rear glass station and the deck
 *     behind it move together. But the greenhouse band is the UNION of the declared glass
 *     stations and the occupant row window packaged rearward from mass.driver_x. Once the
 *     cowl falls behind the driver, the row window is the wider of the two and the union
 *     stops depending on the cowl at all. Step 2 lands at cowl_x = -0.5 m, behind the stock
 *     driver station, and came out geometrically identical to stock where it matters:
 *     L2 0.1527 against the 0.25 floor. Widening the range cannot help, because the masked
 *     region is the whole half of the axis behind the driver and it grows with the range.
 *
 * body.track_rear takes the slot. It clears all three floors on every adjacent pair:
 *
 *     pair 0-1  pixels 0.2449  L2 0.8533  Linf 0.7000 m   (worst component track_rear)
 *     pair 1-2  pixels 0.2734  L2 0.7990  Linf 0.6693 m   (open_wheel_weight)
 *     pair 2-3  pixels 0.1609  L2 0.3504  Linf 0.3000 m   (track_rear)
 *     pair 3-4  pixels 0.1525  L2 0.3511  Linf 0.3000 m   (track_rear)
 *
 * and its nearest neighbour anywhere in the fleet is 0.1544 of pixels with L2 0.3640. It is
 * rear stance: the hub stations, the rear arches and the flare that follows them all move,
 * and past a threshold the body stops containing the wheels and open_wheel_weight fires too.
 * body.track_front already holds a slot, and the two are not the same axis — a fleet where
 * every vehicle has parallel tracks is exactly the fleet that reads as one car. Note the two
 * upper pairs sit at 1.4x the L2 floor rather than the 3x the lower pairs enjoy: the axis is
 * accepted with that margin recorded, not assumed to be comfortable.
 *
 * mass.driver_x also clears every floor, by the widest margin of anything tried (worst
 * adjacent pair 0.3236 of pixels, L2 0.8553), and is NOT used. It is a longitudinal mass
 * station, and mass.engine_x already holds that slot; a second one buys margin by measuring
 * the same thing twice.
 *
 * body.height_overall and body.cowl_x both stay designated visual drivers in the `car-visual`
 * sensitivity table, perturbed across their whole declared ranges, and body.height_overall
 * remains a Halton dimension in the sampled block, so the fleet still spans it. What neither
 * can do is carry five mutually distinct cars, and asserting otherwise would mean lowering a
 * corpus-wide threshold to accommodate one row.
 */

/* ---- sweep value computation ----
 *
 * Even spacing over [min, max] is wrong when the stock default sits inside the interval: a
 * step landing on the default would reproduce the stock baseline exactly. Map steps through
 * the complement of an exclusion window around the default so every step is at least one
 * visible tick away from stock, the sequence stays monotonic, and neighbouring steps cannot
 * collapse onto the same value.
 */
static float sweep_compute_value(const DevParameter *param, int step, int totalSteps)
{
    DevParameter effective = *param;
    if (strcmp(param->name, "body.track_front") == 0) {
        /* This fixture has two front wheels. Zero track is reserved for a single front. */
        effective.minimum = fmaxf(param->minimum, 1.0f);
        param = &effective;
    }
    if (strcmp(param->name, "body.shoulder_x") == 0) {
        VehicleSpec stock;
        vehicle_spec_set_default(&stock);
        const float inset = 0.03f * stock.lengthOverallM;
        effective.minimum =
            fmaxf(param->minimum, -0.5f * stock.wheelbaseM - stock.rearOverhangM + inset);
        effective.maximum =
            fminf(param->maximum, 0.5f * stock.wheelbaseM + stock.frontOverhangM - inset);
        param = &effective;
    }
    const float span = param->maximum - param->minimum;
    const float stepSpan = (totalSteps > 1) ? (span / (float)(totalSteps - 1)) : span;
    /* Minimum exclusion around stock: half a grid step, but never less than 0.08 m for
     * metre-valued drivers (one screen pixel at ~13.2 px/m). For dimensionless keys like
     * aero coefficients, use at least 10% of the span. */
    const float metreExclude = fmaxf(0.5f * fabsf(stepSpan), 0.08f);
    const float dimExclude = fmaxf(0.5f * fabsf(stepSpan), 0.10f * span);
    const float exclude = fmaxf(metreExclude, dimExclude);

    const float leftHi = param->defaultValue - exclude;
    const float rightLo = param->defaultValue + exclude;
    const float leftLen = fmaxf(0.0f, leftHi - param->minimum);
    const float rightLen = fmaxf(0.0f, param->maximum - rightLo);
    const float usable = leftLen + rightLen;

    float value;
    if (!(usable > 0.0f)) {
        /* Degenerate registry range; fall back to plain endpoints. */
        const float t = (totalSteps > 1) ? ((float)step / (float)(totalSteps - 1)) : 0.0f;
        value = param->minimum + span * t;
    } else {
        const float t = (totalSteps > 1) ? ((float)step / (float)(totalSteps - 1)) : 0.0f;
        const float pos = t * usable;
        if (pos <= leftLen) {
            value = param->minimum + fminf(pos, leftLen);
        } else {
            value = rightLo + fminf(pos - leftLen, rightLen);
        }
    }
    return value;
}

/* Build the spec for one sweep slot: the stock car with a single key moved. */
static void sweep_build_spec(int axis, int step, VehicleSpec *out)
{
    vehicle_spec_set_default(out);
    if (axis < 0 || axis >= SWEEP_AXES) return;

    const DevParameter *param = dev_param_find(kSweepAxes[axis].key);
    if (param == NULL) return;
    (void)dev_param_set(out, param, sweep_compute_value(param, step, SWEEP_STEPS));
}

/* Build the spec a sweep row WOULD use for a key that is not on the axis table. Shares
 * sweep_compute_value with the real generator, so a measurement cannot flatter a candidate by
 * spacing its steps differently from the fleet that would ship. */
int car_corpus_sweep_steps(void)
{
    return SWEEP_STEPS;
}

bool car_corpus_sweep_probe(const char *key, int step, VehicleSpec *out)
{
    if (key == NULL || out == NULL) return false;
    if (step < 0 || step >= SWEEP_STEPS) return false;

    const DevParameter *param = dev_param_find(key);
    if (param == NULL) return false;

    vehicle_spec_set_default(out);
    return dev_param_set(out, param, sweep_compute_value(param, step, SWEEP_STEPS));
}

/* The original sampled physics cases are frozen independently of artwork. */
#define SAMPLED_COUNT 43
#include "car_corpus_sampled.inc"

/* -------------------------------------------------------------------- public API ---- */

static int archetype_count(void)
{
    return car_corpus_archetype_count();
}
static int sweep_count(void)
{
    return SWEEP_AXES * SWEEP_STEPS;
}
static int sampled_count(void)
{
    return SAMPLED_COUNT;
}

int car_corpus_count(void)
{
    return archetype_count() + sweep_count() + sampled_count();
}

CarCorpusGroup car_corpus_group(int index)
{
    if (index < archetype_count()) return CAR_CORPUS_ARCHETYPE;
    if (index < archetype_count() + sweep_count()) return CAR_CORPUS_SWEEP;
    return CAR_CORPUS_SAMPLED;
}

const char *car_corpus_group_name(CarCorpusGroup group)
{
    switch (group) {
        case CAR_CORPUS_ARCHETYPE: return "archetype";
        case CAR_CORPUS_SWEEP: return "sweep";
        case CAR_CORPUS_SAMPLED: return "sampled";
        default: return "?";
    }
}

/* Decompose a sweep index into axis and step. */
static bool sweep_slot(int index, int *axisOut, int *stepOut)
{
    const int base = archetype_count();
    const int end = base + sweep_count();
    if (index < base || index >= end) return false;
    const int offset = index - base;
    if (axisOut != NULL) *axisOut = offset / SWEEP_STEPS;
    if (stepOut != NULL) *stepOut = offset % SWEEP_STEPS;
    return true;
}

const char *car_corpus_sweep_key(int index)
{
    int axis = 0;
    if (!sweep_slot(index, &axis, NULL)) return NULL;
    if (axis < 0 || axis >= SWEEP_AXES) return NULL;
    return kSweepAxes[axis].key;
}

bool car_corpus_spec(int index, VehicleSpec *out)
{
    if (out == NULL || index < 0 || index >= car_corpus_count()) return false;

    vehicle_spec_set_default(out);

    /* Archetypes. */
    if (index < archetype_count()) {
        return car_corpus_archetype_build(index, out);
    }

    /* Sweeps. */
    int base = archetype_count();
    if (index < base + sweep_count()) {
        int axis = 0, step = 0;
        if (!sweep_slot(index, &axis, &step)) return false;
        sweep_build_spec(axis, step, out);
        return true;
    }

    const int sampledIdx = index - archetype_count() - sweep_count();
    if (sampledIdx < 0 || sampledIdx >= SAMPLED_COUNT) return false;
    int count = 0;
    while (kSampled[sampledIdx][count].key != NULL) count++;
    int unknown = 0, rejected = 0;
    (void)dev_params_apply_assignments(out, kSampled[sampledIdx], count, &unknown, &rejected);
    return unknown == 0 && rejected == 0 && vehicle_spec_is_valid(out);
}

/* Lower-case, replace anything awkward with '_'. */
static void slugify(const char *src, char *buf, size_t cap)
{
    if (buf == NULL || cap == 0) return;
    size_t n = 0;
    for (; src != NULL && *src != '\0' && n + 1 < cap; src++) {
        const char c = *src;
        if ((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9')) {
            buf[n++] = c;
        } else if (c >= 'A' && c <= 'Z') {
            buf[n++] = (char)(c - 'A' + 'a');
        } else if (n > 0 && buf[n - 1] != '_') {
            buf[n++] = '_';
        }
    }
    while (n > 0 && buf[n - 1] == '_') n--;
    buf[n] = '\0';
}

void car_corpus_id(int index, char *buf, size_t cap)
{
    if (buf == NULL || cap == 0) return;
    buf[0] = '\0';
    if (index < 0 || index >= car_corpus_count()) return;

    if (index < archetype_count()) {
        char slug[48];
        slugify(car_corpus_archetype_name(index), slug, sizeof(slug));
        snprintf(buf, cap, "archetype_%02d_%s", index, slug);
        return;
    }

    int base = archetype_count();
    if (index < base + sweep_count()) {
        int axis = 0, step = 0;
        (void)sweep_slot(index, &axis, &step);
        char slug[48];
        slugify(kSweepAxes[axis].key, slug, sizeof(slug));
        snprintf(buf, cap, "sweep_%s_%d", slug, step);
        return;
    }

    /* Sampled. */
    const int sampledIdx = index - base - sweep_count();
    snprintf(buf, cap, "sampled_%02d", sampledIdx);
}

void car_corpus_describe(int index, char *buf, size_t cap)
{
    if (buf == NULL || cap == 0) return;
    buf[0] = '\0';
    if (index < 0 || index >= car_corpus_count()) return;

    /* Archetypes. */
    if (index < archetype_count()) {
        snprintf(buf, cap, "%s - %s", car_corpus_archetype_name(index),
                 car_corpus_archetype_description(index));
        return;
    }

    int base = archetype_count();

    /* Sweeps. */
    if (index < base + sweep_count()) {
        int step = 0;
        const DevParameter *param = NULL;
        (void)sweep_slot(index, NULL, &step);

        VehicleSpec spec;
        if (!car_corpus_spec(index, &spec)) return;

        const char *key = car_corpus_sweep_key(index);
        param = (key != NULL) ? dev_param_find(key) : NULL;
        if (param == NULL) return;

        const float value = dev_param_get(&spec, param);
        snprintf(buf, cap, "%s = %.3f %s (step %d/%d)", param->name, (double)value,
                 (param->unit != NULL && param->unit[0] != '\0') ? param->unit : "", step + 1,
                 SWEEP_STEPS);
        return;
    }

    /* Sampled. */
    const int sampledIdx = index - base - sweep_count();
    snprintf(buf, cap, "sampled_%02d - Halton seed %d", sampledIdx, sampledIdx);
}
