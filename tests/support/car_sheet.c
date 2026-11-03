/* Source sprites and physics evidence, exported without a GPU or procedural artwork. */
#include "car_sheet.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "dev/dev_params.h"
#include "game/telemetry.h"

#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmissing-prototypes"
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wshadow"
#endif
#define STB_IMAGE_WRITE_IMPLEMENTATION
#define STBI_WRITE_NO_STDIO_DEPRECATION
#include "stb/stb_image_write.h"
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

static void json_string(FILE *out, const char *text)
{
    fputc('"', out);
    for (const unsigned char *p = (const unsigned char *)text; *p; p++) {
        if (*p == '"' || *p == '\\') fputc('\\', out);
        if (*p < 32)
            fprintf(out, "\\u%04x", *p);
        else
            fputc(*p, out);
    }
    fputc('"', out);
}

static void html_string(FILE *out, const char *text)
{
    for (const char *p = text; *p; p++) {
        switch (*p) {
            case '&': fputs("&amp;", out); break;
            case '<': fputs("&lt;", out); break;
            case '>': fputs("&gt;", out); break;
            case '"': fputs("&quot;", out); break;
            default: fputc(*p, out); break;
        }
    }
}

static bool write_card(FILE *out, const VehicleSpec *spec, const CarModel *model,
                       const char *imageName)
{
    fprintf(out, "{\"id\":");
    json_string(out, model->code);
    fprintf(out, ",\"name\":");
    json_string(out, model->name);
    fprintf(out, ",\"appearance_model\":");
    json_string(out, model->code);
    fprintf(out, ",\"image\":");
    if (imageName != NULL)
        json_string(out, imageName);
    else
        fprintf(out, "\"%s.png\"", model->code);
    fprintf(out,
            ",\"source_manifest\":\"data/carmodels/sprites.json\","
            "\"mass_kg\":%.7g,\"cg_height_m\":%.7g,\"yaw_inertia_kg_m2\":%.7g,"
            "\"length_m\":%.7g,\"width_m\":%.7g,\"wheelbase_m\":%.7g,"
            "\"frame_size\":%d,\"frame_count\":%d,\"image_span_m\":%.7g,\"parameters\":{",
            (double)spec->massKg, (double)spec->cgHeightM, (double)spec->yawInertiaKgM2,
            (double)spec->lengthOverallM, (double)spec->widthOverallM, (double)spec->wheelbaseM,
            model->frameSize, model->frameCount,
            (double)(model->orthoSpan / model->sourceLength * spec->lengthOverallM));
    for (int i = 0; i < dev_params_count(); i++) {
        const DevParameter *param = dev_param_at(i);
        fprintf(out, "%s\"%s\":%.9g", i ? "," : "", param->name,
                (double)dev_param_get(spec, param));
    }
    fprintf(out, "}}");
    return !ferror(out);
}

bool car_sheet_write_spec(const VehicleSpec *spec, const CarModel *model, const char *prefix)
{
    if (spec == NULL || model == NULL || prefix == NULL || !vehicle_spec_is_valid(spec))
        return false;
    CarModelImage image;
    if (!car_model_load(model, &image)) return false;
    const int size = model->frameSize;
    unsigned char *rgba = (unsigned char *)malloc((size_t)size * (size_t)size * 4u);
    if (rgba == NULL) {
        car_model_image_free(&image);
        return false;
    }
    const int frame = -model->firstAngleDeg / model->angleStepDeg;
    for (int y = 0; y < size; y++) {
        for (int x = 0; x < size; x++) {
            const unsigned char *src =
                image.rgba +
                ((size_t)(frame / model->columns * size + y) * (size_t)image.width +
                 (size_t)(frame % model->columns * size + x)) *
                    4u;
            unsigned char *dst = rgba + ((size_t)y * (size_t)size + (size_t)x) * 4u;
            dst[3] = src[3];
            /* Export normal straight-alpha PNG; GPU atlas stays premultiplied. */
            for (int c = 0; c < 3; c++)
                dst[c] =
                    src[3]
                        ? (unsigned char)(((unsigned int)src[c] * 255u + src[3] / 2u) / src[3])
                        : 0;
        }
    }
    char path[1024];
    snprintf(path, sizeof(path), "%s.png", prefix);
    bool ok = stbi_write_png(path, size, size, 4, rgba, size * 4) != 0;
    free(rgba);
    car_model_image_free(&image);
    if (!ok) return false;
    snprintf(path, sizeof(path), "%s.json", prefix);
    FILE *out = fopen(path, "wb");
    if (out == NULL) return false;
    const char *leaf = strrchr(prefix, '/');
    const char *backslash = strrchr(prefix, '\\');
    if (backslash != NULL && (leaf == NULL || backslash > leaf)) leaf = backslash;
    char imageName[1024];
    snprintf(imageName, sizeof(imageName), "%s.png", leaf == NULL ? prefix : leaf + 1);
    ok = write_card(out, spec, model, imageName);
    return fclose(out) == 0 && ok;
}

bool car_sheet_write_cards(const char *outDir)
{
    if (outDir == NULL || !telemetry_ensure_dir(outDir)) return false;
    char path[1024];
    snprintf(path, sizeof(path), "%s/cards.json", outDir);
    FILE *out = fopen(path, "wb");
    if (out == NULL) return false;
    fprintf(out, "{\"format\":\"source-mesh-sprites-v1\",\"cars\":[");
    bool ok = true;
    for (int n = 0; n < car_model_count() && ok; n++) {
        const CarModel *model = car_model_at(n);
        VehicleSpec spec;
        vehicle_spec_set_default(&spec);
        snprintf(path, sizeof(path), "data/carmodels/profiles/%s.txt", model->code);
        int unknown = 0, rejected = 0;
        ok = dev_params_load(&spec, path, NULL, &unknown, &rejected) && !unknown && !rejected;
        snprintf(path, sizeof(path), "%s/%s", outDir, model->code);
        if (ok) ok = car_sheet_write_spec(&spec, model, path);
        if (ok) {
            if (n) fputc(',', out);
            ok = write_card(out, &spec, model, NULL);
        }
    }
    fprintf(out, "]}\n");
    return fclose(out) == 0 && ok;
}

bool car_sheet_write(const char *outDir)
{
    if (!car_sheet_write_cards(outDir)) return false;
    char path[1024];
    snprintf(path, sizeof(path), "%s/index.html", outDir);
    FILE *out = fopen(path, "wb");
    if (out == NULL) return false;
    fprintf(out, "<!doctype html><meta charset=\"utf-8\"><title>Source vehicle sprites</title>"
                 "<style>body{background:#161c24;color:#eee;font:14px system-ui}"
                 "main{display:flex;flex-wrap:wrap;gap:16px}article{width:220px;background:#"
                 "222b38;padding:12px}"
                 "figure{height:220px;display:grid;place-items:center;margin:0}img{object-fit:"
                 "contain}</style>"
                 "<h1>Source vehicle sprites</h1><p>904 cars and trucks. Uniform 26.4 px/m "
                 "physical scale; "
                 "original source paint and geometry. Physics estimates are documented in "
                 "data/carmodels.</p><main>");
    for (int n = 0; n < car_model_count(); n++) {
        const CarModel *model = car_model_at(n);
        const float side =
            model->orthoSpan / model->sourceLength * model->physicalLengthM * 26.4f;
        fprintf(out,
                "<article><figure><img loading=\"lazy\" width=\"%.0f\" height=\"%.0f\" "
                "src=\"%s.png\" alt=\"",
                (double)side, (double)side, model->code);
        html_string(out, model->name);
        fprintf(out, "\"></figure><b>");
        html_string(out, model->name);
        fprintf(out, "</b><p>%s · reference length %.2f m</p></article>\n", model->code,
                (double)model->physicalLengthM);
    }
    fprintf(out, "</main>");
    return fclose(out) == 0;
}
