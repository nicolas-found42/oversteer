/* Source-mesh sprite, presentation-identity and physics-fixture checks. */
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "support/test_harness.h"
#include "test_scenarios.h"
#include "dev/car_corpus.h"
#include "dev/dev_params.h"
#include "game/game.h"
#include "physics/vehicle.h"
#include "render/car_model.h"
#include "render/vehicle_effects.h"

static void scenario_source_sprites(void)
{
    check(car_model_count() == 904, "source catalog includes every retained car and truck");
    const CarModel *focus = car_model_default();
    check(focus != NULL, "the default source-model sprite is in the catalog");
    if (focus == NULL) return;
    CarModelImage image;
    const bool loaded = car_model_load(focus, &image);
    check(loaded, "shared decoder loads the valid lossless source PNG atlas");
    if (!loaded) return;
    car_model_image_free(&image);
    int decoded = 0, frames = 0;
    bool premultiplied = true;
    for (int n = 0; n < car_model_count(); n++) {
        const CarModel *model = car_model_at(n);
        check(car_model_find(model->code) == n, "catalog lookup round-trips %s", model->code);
        check(strncmp(model->code, "REDLINE_", 8) != 0 &&
                  strncmp(model->code, "GT_SIMULATION_", 14) != 0 &&
                  strncmp(model->code, "MCLA_VA_", 8) != 0 &&
                  strncmp(model->code, "MC3_VA_", 7) != 0,
              "excluded source namespace absent: %s", model->code);
        const bool ok = car_model_load(model, &image);
        check(ok, "source atlas decodes: %s", model->code);
        if (!ok) continue;
        decoded++;
        for (int f = 0; f < model->frameCount; f++) {
            int top = 0;
            const int rows = (model->frameCount + model->columns - 1) / model->columns;
            for (int level = 0, size = model->frameSize; level < model->mipLevels;
                 level++, size /= 2) {
                bool visible = false;
                for (int y = 0; y < size; y++) {
                    for (int x = 0; x < size; x++) {
                        const int px = (f % model->columns) * size + x;
                        const int py = top + (f / model->columns) * size + y;
                        const unsigned char *p =
                            image.rgba + ((size_t)py * (size_t)image.width + (size_t)px) * 4;
                        visible |= p[3] > 0;
                        premultiplied &= p[0] <= p[3] && p[1] <= p[3] && p[2] <= p[3];
                    }
                }
                check(visible,
                      "source steering frame and mip contain geometry: %s frame%d level%d",
                      model->code, f, level);
                top += rows * size;
            }
            frames++;
        }
        car_model_image_free(&image);
    }
    check(decoded == 904 && frames == 11752,
          "all retained source models and steering frames load");
    check(premultiplied, "atlas pixels satisfy the premultiplied-alpha contract");
    CarAppearanceSpec appearance = { 0 };
    check(car_model_select(&appearance, focus->code), "explicit source appearance selects");
    const CarAppearanceSpec before = appearance;
    check(!car_model_select(&appearance, "MCLA_VA_350Z_04"), "ambient traffic cannot select");
    check(memcmp(&before, &appearance, sizeof(before)) == 0,
          "failed selection retains prior model");
    VehicleSpec spec;
    vehicle_spec_set_default(&spec);
    CarModelLayout a, b;
    check(car_model_layout(focus, &spec, 0.0f, &a), "source sprite physical layout is valid");
    spec.engineTorqueCurveNm[3] += 10;
    check(car_model_layout(focus, &spec, 0.0f, &b) && memcmp(&a, &b, sizeof(a)) == 0,
          "engine tuning does not invent a different body or palette");
    bool poses = true;
    for (int i = 0; i < 13; i++) {
        const float radians = (float)(-60 + i * 10) * 0.01745329252f;
        poses &= car_model_layout(focus, &spec, radians, &b) && b.frame == i;
    }
    check(poses, "source steering poses map to their physical steering angles");
    check(car_model_layout(focus, &spec, -2.0f, &a) && a.frame == 0 &&
              car_model_layout(focus, &spec, 2.0f, &b) && b.frame == 12,
          "steering outside the baked range clamps to the extreme source poses");
}

static void scenario_corpus(void)
{
    const int count = car_corpus_count();
    check(count >= 90 && count <= 110,
          "physics fixture corpus retains approximately100 entries");
    for (int i = 0; i < count; i++) {
        VehicleSpec first, again, scratch;
        char id[128], path[256];
        car_corpus_id(i, id, sizeof(id));
        check(car_corpus_spec(i, &first), "physics fixture builds: %s", id);
        (void)car_corpus_spec((i + 37) % count, &scratch);
        check(car_corpus_spec(i, &again) && memcmp(&first, &again, sizeof(first)) == 0,
              "physics fixture is order independent: %s", id);
        check(vehicle_spec_is_valid(&first), "physics fixture validates: %s", id);
        snprintf(path, sizeof(path), "data/vehicles/corpus/%s/%s.txt",
                 car_corpus_group_name(car_corpus_group(i)), id);
        vehicle_spec_set_default(&again);
        int unknown = 0, rejected = 0;
        const bool loaded = dev_params_load(&again, path, NULL, &unknown, &rejected);
        /* Archived fixtures contain the retired body.rolling_resistance key. */
        check(loaded && unknown == 1 && rejected == 0, "tracked physics fixture loads: %s", id);
        if (!loaded) continue;
        bool same = true;
        for (int k = 0; k < dev_params_count(); k++) {
            const DevParameter *parameter = dev_param_at(k);
            if (parameter->derived) continue;
            const float a = dev_param_get(&first, parameter),
                        b = dev_param_get(&again, parameter);
            if (fabsf(a - b) > fmaxf(2e-5f, fabsf(a) * 2e-5f)) same = false;
        }
        check(same, "tracked fixture matches the registry values: %s", id);
    }
}

static void scenario_source_identity(void)
{
    Game *game = (Game *)calloc(1, sizeof(*game));
    check(game != NULL, "source identity test allocates the persistent game");
    if (game == NULL) return;
    game_init(game);
    int loaded = 0;
    int tagged = 0;
    for (int i = 0; i < car_model_count(); i++) {
        const CarModel *entry = car_model_at(i);
        if (game_select_model(game, entry->code)) loaded++;
        char path[160];
        snprintf(path, sizeof(path), "data/carmodels/profiles/%s.txt", entry->code);
        const CarModel *saved = NULL;
        if (car_model_read_profile(path, &saved) && saved == entry) tagged++;
    }
    check(loaded == 904, "every source catalog vehicle loads its researched physics profile");
    check(tagged == 904, "every shipped profile carries its separate source identity");
    check(game_select_model(game, "MC3_VP_SC430_04"), "real SC430 catalog entry selects");
    check(game->spec.gearCount == 5, "SC430 keeps its researched five-speed reference");
    const VehicleSpec before = game->spec;
    const CarAppearanceSpec appearance = game->appearance;
    check(!game_select_model(game, "MCLA_VA_350Z_04"), "excluded traffic cannot become active");
    check(memcmp(&before, &game->spec, sizeof(before)) == 0 &&
              memcmp(&appearance, &game->appearance, sizeof(appearance)) == 0,
          "failed catalog selection retains spec and appearance atomically");
    const uint32_t checksum = game_state_checksum(game);
    check(car_model_select(&game->appearance, "F350"),
          "presentation-only source selection works");
    check(game_state_checksum(game) == checksum,
          "model appearance does not affect simulation checksum");
    const CarModel *model = car_model_selected(&game->appearance);
    VehicleSpec tuned = game->spec;
    tuned.engineTorqueCurveNm[3] += 10;
    game_apply_spec(game, &tuned);
    check(car_model_selected(&game->appearance) == model,
          "live tuning retains source identity");
    check(game_select_model(game, "GT4_BENZ0001") && game->spec.frontWheelCount == 1,
          "Benz source vehicle retains the three-wheel physics capability");
    const char *path = "artifacts/source-identity-profile-test.txt";
    const CarModel *saved = NULL;
    check(dev_params_save(&game->spec, path) &&
              car_model_append_profile(path, &game->appearance) &&
              car_model_read_profile(path, &saved) &&
              saved == car_model_selected(&game->appearance),
          "profile save/load preserves presentation without numeric registry fields");
    check(car_model_append_profile(path, &game->appearance) &&
              !car_model_read_profile(path, &saved),
          "duplicate model metadata is rejected");
    check(dev_params_save(&game->spec, path) && car_model_read_profile(path, &saved) &&
              saved == NULL,
          "legacy profiles have no assigned presentation override");
    FILE *file = fopen(path, "ab");
    if (file != NULL) {
        fputs("# carmodels.model = MCLA_VA_350Z_04\n", file);
        fclose(file);
    }
    check(file != NULL && !car_model_read_profile(path, &saved),
          "excluded model metadata is rejected before profile application");
    (void)remove(path);
    game_shutdown(game);
    free(game);
}

static void scenario_render_contracts(void)
{
    /* A NULL input returns a zeroed effect state — permanent, not placeholder behaviour. */
    {
        const VehicleVisualEffects zero = vehicle_visual_effects_derive(NULL);
        bool allZero = (zero.brakeLamp01 == 0.0f) && (zero.bodyRollRad == 0.0f) &&
                       (zero.shadowOffsetBodyM.x == 0.0f) && (zero.shadowOffsetBodyM.y == 0.0f);
        for (int i = 0; i < WHEEL_COUNT; i++) {
            if (zero.tireSmoke01[i] != 0.0f) allZero = false;
        }
        check(allZero, "vehicle_visual_effects_derive(NULL) is a zeroed effect state");
    }

    /* A populated input stays bounded and finite. The placeholder satisfies this trivially;
     * the real derivation must satisfy it too, so this check outlives the stub. */
    {
        VehicleEffectInputs in;
        memset(&in, 0, sizeof(in));
        in.brakeInput01 = 1.0f;
        in.filteredLateralAccelerationMps2 = 12.0f;
        for (int i = 0; i < WHEEL_COUNT; i++) {
            in.frictionUsage01[i] = 1.0f;
            in.slipAngleRad[i] = 0.6f;
            in.slipRatio[i] = 0.9f;
            in.surface[i] = SURFACE_ASPHALT;
        }

        const VehicleVisualEffects fx = vehicle_visual_effects_derive(&in);
        bool bounded = (fx.brakeLamp01 >= 0.0f && fx.brakeLamp01 <= 1.0f) &&
                       isfinite(fx.bodyRollRad) && isfinite(fx.shadowOffsetBodyM.x) &&
                       isfinite(fx.shadowOffsetBodyM.y);
        for (int i = 0; i < WHEEL_COUNT; i++) {
            if (!(fx.tireSmoke01[i] >= 0.0f && fx.tireSmoke01[i] <= 1.0f)) bounded = false;
        }
        check(bounded, "derived effects stay bounded and finite for a saturated input");
    }
}

static const TestScenario kAppearanceScenarios[] = {
    { "source-sprites", "mesh-baked atlas coverage, alpha and physical layout",
      scenario_source_sprites },
    { "source-identity", "catalog selection and simulation/appearance separation",
      scenario_source_identity },
    { "corpus", "physics fixture determinism and profile integrity", scenario_corpus },
    { "render-contracts", "presentation effects remain bounded", scenario_render_contracts },
};

TestScenarioGroup test_appearance_scenarios(void)
{
    TestScenarioGroup group;
    group.items = kAppearanceScenarios;
    group.count = sizeof(kAppearanceScenarios) / sizeof(kAppearanceScenarios[0]);
    return group;
}
