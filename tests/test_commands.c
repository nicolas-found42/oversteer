/*
 * test_commands.c — the non-scenario modes: throughput, the failure-bundle verifier, and the
 * parameter/corpus generators.
 *
 * These write artifacts and measure things. Keeping them out of the scenario registry is what
 * lets the registry stay a list of assertions.
 */
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#if defined(_WIN32)
#include <direct.h>
#define OVERSTEER_RMDIR(path) _rmdir(path)
#else
#include <unistd.h>
#define OVERSTEER_RMDIR(path) rmdir(path)
#endif

#include "test_commands.h"
#include "test_scenarios.h"
#include "support/car_sheet.h"
#include "support/simulation_fixture.h"
#include "support/test_harness.h"

#include "dev/car_corpus.h"
#include "game/car_roster.h"
#include "render/car_model.h"
#include "core/config.h"
#include "dev/dev_params.h"
#include "dev/dev_replay.h"
#include "dev/dev_scenario.h"
#include "dev/dev_state.h"
#include "physics/drivetrain.h"
#include "physics/auto_transmission.h"
#include "dev/failure_bundle.h"
#include "physics/surface.h"
#include "game/game.h"
#include "game/input.h"
#include "core/math_utils.h"
#include "game/particle.h"
#include "physics/physics.h"
#include "render/render.h"
#include "game/replay.h"
#include "game/telemetry.h"
#include "platform/timestep.h"
#include "physics/tire.h"
#include "core/units.h"

/* Simulation throughput, for the performance workflow. Prints one machine-readable line. */
int test_run_benchmark(int ticks)
{
    if (ticks <= 0) ticks = 240000;

    Game *game = alloc_game();
    game_init(game);
    game->dev.scenario = dev_scenario_find("power-oversteer");
    game->dev.scenarioRunning = (game->dev.scenario > 0);
    game->dev.scenarioStartTick = 0;

    const clock_t started = clock();
    for (int i = 0; i < ticks; i++) {
        /* Restart the script rather than letting it finish, so every tick does real work. */
        if (!game->dev.scenarioRunning && game->dev.scenario > 0) {
            game->dev.scenarioRunning = true;
            game->dev.scenarioStartTick = game->sim.tick;
        }
        game_fixed_update(game, FIXED_DT_S);
    }
    const clock_t finished = clock();

    const double seconds = (double)(finished - started) / (double)CLOCKS_PER_SEC;
    const double ticksPerSecond = (seconds > 0.0) ? (double)ticks / seconds : 0.0;
    const double realtimeFactor = ticksPerSecond / (double)FIXED_HZ;

    printf("BENCHMARK ticks=%d seconds=%.4f ticks_per_second=%.0f realtime_factor=%.1f "
           "checksum=%08x\n",
           ticks, seconds, ticksPerSecond, realtimeFactor, game->stateChecksum);

    free(game);
    return 0;
}

static bool file_contains_text(const char *path, const char *needle)
{
    FILE *file = fopen(path, "rb");
    if (file == NULL) return false;
    char buffer[4096];
    const size_t read = fread(buffer, 1, sizeof(buffer) - 1u, file);
    fclose(file);
    buffer[read] = '\0';
    return strstr(buffer, needle) != NULL;
}

/*
 * Exercise the real bundle writer with a controlled Phase 3 invariant failure. This is an
 * explicit validation mode rather than a normal scenario: the ordinary suite must stay
 * green, while release validation still gets a reproducible way to prove that all six
 * diagnostic files and the Phase 3 context are present. The fixture cleans up after itself.
 */
int test_verify_failure_bundle(const char *rootDir)
{
    const char *root = (rootDir != NULL) ? rootDir : "artifacts/bundle-verification";
    const char *telemetryPath = TELEMETRY_DIR "/_bundle_verification.csv";
    const char *failure =
        "controlled Phase 3 invariant failure: dynamic front load below minimum";
    const char *profile = "Phase3 Candidate";

    Game *game = alloc_game();
    game_init(game);
    const int scenario = dev_scenario_find("accel-load");
    game->dev.scenario = scenario;
    game->dev.scenarioRunning = true;
    game->dev.scenarioStartTick = game->sim.tick;
    replay_begin_recording(&game->replay, game->sim.tick);

    /* --verify-failure-bundle can be the FIRST thing run against a clean checkout. */
    (void)telemetry_ensure_dir(TELEMETRY_DIR);

    TelemetryWriter writer;
    if (!telemetry_open(&writer, telemetryPath)) {
        free(game);
        return 1;
    }
    for (int i = 0; i < 180; i++) {
        game_fixed_update(game, FIXED_DT_S);
        const TelemetryRow row = test_telemetry_row_from_game(game, 1);
        if (!telemetry_write_row(&writer, &row)) {
            telemetry_close(&writer);
            free(game);
            return 1;
        }
    }
    if (!telemetry_close(&writer)) {
        free(game);
        return 1;
    }

    FailureBundle bundle;
    memset(&bundle, 0, sizeof(bundle));
    bundle.scenario = "phase3-controlled";
    bundle.failureText = failure;
    bundle.telemetryPath = telemetryPath;
    bundle.replay = &game->replay;
    bundle.spec = &game->spec;
    bundle.activeProfile = profile;
    bundle.failingTick = game->sim.tick;
    bundle.checksum = game->stateChecksum;
    bundle.seed = 1010u;
    bundle.checksRun = 1;
    bundle.checksFailed = 1;

    char directory[512];
    bool ok = failure_bundle_write(root, &bundle, directory, sizeof(directory));
    static const char *const required[] = { "replay.bin",   "telemetry.csv",
                                            "summary.json", "config_snapshot.txt",
                                            "git_info.txt", "failure.txt" };
    char path[640];
    for (size_t i = 0; ok && i < sizeof(required) / sizeof(required[0]); i++) {
        snprintf(path, sizeof(path), "%s/%s", directory, required[i]);
        FILE *file = fopen(path, "rb");
        ok = (file != NULL);
        if (file != NULL) fclose(file);
    }
    snprintf(path, sizeof(path), "%s/summary.json", directory);
    ok = ok && file_contains_text(path, failure) && file_contains_text(path, profile);
    snprintf(path, sizeof(path), "%s/config_snapshot.txt", directory);
    ok = ok && file_contains_text(path, "active_profile=Phase3 Candidate");

    for (size_t i = 0; i < sizeof(required) / sizeof(required[0]); i++) {
        snprintf(path, sizeof(path), "%s/%s", directory, required[i]);
        remove(path);
    }
    OVERSTEER_RMDIR(directory);
    remove(telemetryPath);
    OVERSTEER_RMDIR(root);
    free(game);

    printf("FAILURE_BUNDLE_VERIFY files=6 failure_text=yes active_profile=yes cleanup=yes "
           "result=%s\n",
           ok ? "PASS" : "FAIL");
    return ok ? 0 : 1;
}

int test_dump_params(const char *path)
{
    if (path == NULL) {
        dev_params_write_markdown(stdout);
        return 0;
    }

    FILE *file = fopen(path, "wb");
    if (file == NULL) {
        fprintf(stderr, "error: could not write '%s'\n", path);
        return 1;
    }
    dev_params_write_markdown(file);
    if (fclose(file) != 0) {
        fprintf(stderr, "error: could not close '%s'\n", path);
        return 1;
    }
    printf("wrote %s (%d parameters)\n", path, dev_params_count());
    return 0;
}

/* Export every corpus vehicle as a tuning profile, grouped into subdirectories. The files are
 * a human-readable mirror of car_corpus.c, not a second source of truth: the `corpus` scenario
 * asserts each one round-trips back to the spec the code generates. */
int test_generate_corpus(const char *dir)
{
    if (dir == NULL) dir = "data/vehicles/corpus";
    if (!telemetry_ensure_dir(dir)) return 1;

    int written = 0;
    for (int i = 0; i < car_corpus_count(); i++) {
        VehicleSpec spec;
        char id[128], sub[512], path[768];

        if (!car_corpus_spec(i, &spec)) {
            fprintf(stderr, "error: corpus entry %d could not be built\n", i);
            return 1;
        }
        car_corpus_id(i, id, sizeof(id));

        snprintf(sub, sizeof(sub), "%s/%s", dir, car_corpus_group_name(car_corpus_group(i)));
        if (!telemetry_ensure_dir(sub)) return 1;

        snprintf(path, sizeof(path), "%s/%s.txt", sub, id);
        if (!dev_params_save(&spec, path)) {
            fprintf(stderr, "error: could not write '%s'\n", path);
            return 1;
        }
        written++;
    }

    printf("wrote %d vehicle profiles to %s\n", written, dir);
    return 0;
}

/* Print the roster: one id per line, so the suite can enumerate cars from the binary. */
int test_list_cars(void)
{
    for (int i = 0; i < car_roster_count(); i++) {
        char id[128];
        car_roster_id(i, id, sizeof(id));
        printf("%s\n", id);
    }
    return 0;
}

/* Export every roster car as a tuning profile, exactly as --generate-corpus does for the
 * appearance fleet. The `roster` scenario asserts each one round-trips back to the spec
 * the code generates, so the files cannot silently rot away from the code. */
int test_generate_roster(const char *dir)
{
    if (dir == NULL) dir = "data/vehicles/roster";
    if (!telemetry_ensure_dir(dir)) return 1;

    int written = 0;
    for (int i = 0; i < car_roster_count(); i++) {
        VehicleSpec spec;
        char id[128], path[768];

        if (!car_roster_spec(i, &spec)) {
            fprintf(stderr, "error: roster entry %d could not be built\n", i);
            return 1;
        }
        car_roster_id(i, id, sizeof(id));

        snprintf(path, sizeof(path), "%s/%s.txt", dir, id);
        if (!dev_params_save(&spec, path)) {
            fprintf(stderr, "error: could not write '%s'\n", path);
            return 1;
        }
        written++;
    }

    printf("wrote %d roster profiles to %s\n", written, dir);
    return 0;
}

/* The corpus table, in the same generated-Markdown style as --dump-params. */
int test_dump_corpus_index(const char *path)
{
    FILE *out = stdout;
    if (path != NULL) {
        out = fopen(path, "wb");
        if (out == NULL) {
            fprintf(stderr, "error: could not write '%s'\n", path);
            return 1;
        }
    }

    fprintf(out, "<!-- Generated by `build/tests/oversteer_tests.exe --dump-corpus-index`."
                 " Do not edit by hand. -->\n");
    fprintf(out, "# Vehicle corpus\n\n");
    fprintf(out, "Every entry is a pure function of its index in `src/dev/car_corpus.c`."
                 " These are deterministic physics fixtures; source artwork is selected "
                 "independently.\n\n");
    fprintf(out, "| # | Group | Id | What defines it |\n|---:|---|---|---|\n");

    for (int i = 0; i < car_corpus_count(); i++) {
        char id[128], note[192];
        car_corpus_id(i, id, sizeof(id));
        car_corpus_describe(i, note, sizeof(note));
        fprintf(out, "| %d | %s | `%s` | %s |\n", i, car_corpus_group_name(car_corpus_group(i)),
                id, note);
    }

    if (path != NULL) {
        if (fclose(out) != 0) {
            fprintf(stderr, "error: could not close '%s'\n", path);
            return 1;
        }
        printf("wrote %s (%d vehicles)\n", path, car_corpus_count());
    }
    return 0;
}

int test_dump_corpus_cards(const char *dir)
{
    return car_sheet_write_cards(dir) ? 0 : 1;
}

int test_dump_corpus_sheet(const char *dir)
{
    return car_sheet_write(dir) ? 0 : 1;
}

int test_measure_vehicle(const char *profile, const char *prefix, bool benchmark, bool card)
{
    VehicleSpec spec;
    vehicle_spec_set_default(&spec);
    int unknown = 0;
    int rejected = 0;
    if (!dev_params_load(&spec, profile, NULL, &unknown, &rejected) || unknown || rejected) {
        fprintf(stderr, "vehicle measurement: invalid profile %s (%d unknown, %d rejected)\n",
                profile, unknown, rejected);
        return 1;
    }
    if (card) {
        const CarModel *model = NULL;
        if (!car_model_read_profile(profile, &model) || model == NULL) {
            fprintf(stderr, "vehicle card: profile needs a valid # carmodels.model = CODE\n");
            return 1;
        }
        if (!car_sheet_write_spec(&spec, model, prefix)) return 1;
    }
    if (!benchmark) return 0;

    VehicleState state;
    VehicleDerived derived;
    VehicleRenderState history;
    vehicle_state_reset(&spec, &state, &derived, &history);
    AutoTransmission automatic = { true, true, AUTO_DRIVE, 0.0f };
    Input input;
    input_zero(&input);
    input.throttle = 1.0f;
    float zeroToHundredS = -1.0f;
    float maxSpeedMps = 0.0f;
    for (int tick = 0; tick < FIXED_HZ * 120; tick++) {
        auto_transmission_update(&automatic, &state, &spec, &derived, &input, FIXED_DT_S);
        physics_fixed_update(&spec, &state, &derived, &history, &input, FIXED_DT_S);
        if (!physics_state_is_valid(&spec, &state, &derived)) return 1;
        if (state.velocityLongitudinalMps > maxSpeedMps)
            maxSpeedMps = state.velocityLongitudinalMps;
        if (zeroToHundredS < 0.0f && state.velocityLongitudinalMps >= 100.0f / 3.6f)
            zeroToHundredS = (float)(tick + 1) * FIXED_DT_S;
    }

    vehicle_state_reset(&spec, &state, &derived, &history);
    state.selectedGear = 0;
    state.velocityLongitudinalMps = 100.0f / 3.6f;
    for (int i = 0; i < WHEEL_COUNT; i++) {
        if (!vehicle_wheel_is_active(&spec, i)) continue;
        const float radius = vehicle_wheel_radius_m(&spec, i);
        state.wheels[i].angularVelocityRadS = state.velocityLongitudinalMps / radius;
    }
    input_zero(&input);
    input.brake = 1.0f;
    int stopTick = 0;
    for (; stopTick < FIXED_HZ * 30; stopTick++) {
        physics_fixed_update(&spec, &state, &derived, &history, &input, FIXED_DT_S);
        if (!physics_state_is_valid(&spec, &state, &derived)) return 1;
        if (fabsf(state.velocityLongitudinalMps) < 0.1f) break;
    }
    char path[1024];
    snprintf(path, sizeof(path), "%s_physics.json", prefix);
    FILE *out = fopen(path, "wb");
    if (out == NULL) return 1;
    fprintf(out, "{\"protocol\":\"level asphalt; production automatic; 120s full throttle; "
                 "100kmh neutral full brake\",\"zero_to_100_s\":");
    if (zeroToHundredS >= 0.0f)
        fprintf(out, "%.6g", (double)zeroToHundredS);
    else
        fprintf(out, "null");
    fprintf(out,
            ",\"max_120s_kmh\":%.6g,\"brake_100_to_stop_m\":%.6g,"
            "\"brake_stopped\":%s}\n",
            (double)(maxSpeedMps * 3.6f), (double)state.positionM.x,
            stopTick < FIXED_HZ * 30 ? "true" : "false");
    return fclose(out) == 0 ? 0 : 1;
}
