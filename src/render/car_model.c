#include "render/car_model.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/math_utils.h"

/* One decoder implementation, with the same pixel path in game and headless tests. */
#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#pragma GCC diagnostic ignored "-Wmissing-prototypes"
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wshadow"
#endif
#define STB_IMAGE_IMPLEMENTATION
#define STB_IMAGE_STATIC
#define STBI_ONLY_PNG
#define STBI_NO_LINEAR
#define STBI_NO_HDR
#include "stb/stb_image.h"
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

static const CarModel kModels[] = {
#include "render/car_model_catalog.inc"
};

int car_model_count(void)
{
    return (int)(sizeof(kModels) / sizeof(kModels[0]));
}

const CarModel *car_model_at(int index)
{
    return index >= 0 && index < car_model_count() ? &kModels[index] : NULL;
}

int car_model_find(const char *code)
{
    if (code == NULL) return -1;
    int low = 0, high = car_model_count();
    while (low < high) {
        const int middle = low + (high - low) / 2;
        const int comparison = strcmp(code, kModels[middle].code);
        if (comparison == 0) return middle;
        if (comparison < 0)
            high = middle;
        else
            low = middle + 1;
    }
    return -1;
}

const CarModel *car_model_default(void)
{
    return car_model_at(car_model_find("FOCUS_SVT"));
}

bool car_model_select(CarAppearanceSpec *appearance, const char *code)
{
    if (appearance == NULL || car_model_find(code) < 0) return false;
    snprintf(appearance->modelCode, sizeof(appearance->modelCode), "%s", code);
    return true;
}

const CarModel *car_model_selected(const CarAppearanceSpec *appearance)
{
    if (appearance == NULL || appearance->modelCode[0] == '\0') return car_model_default();
    return car_model_at(car_model_find(appearance->modelCode));
}

bool car_model_load(const CarModel *model, CarModelImage *out)
{
    if (model == NULL || out == NULL) return false;
    memset(out, 0, sizeof(*out));
    int width = 0, height = 0, channels = 0;
    unsigned char *rgba = stbi_load(model->path, &width, &height, &channels, 4);
    if (rgba == NULL) return false;
    int mipSpan = 0;
    for (int level = 0, size = model->frameSize; level < model->mipLevels && size > 0;
         level++, size /= 2)
        mipSpan += size;
    const bool valid =
        channels == 4 && model->frameSize > 0 && model->columns > 0 && model->mipLevels == 9 &&
        width == model->frameSize * model->columns &&
        height == mipSpan * ((model->frameCount + model->columns - 1) / model->columns);
    if (!valid) {
        stbi_image_free(rgba);
        return false;
    }
    out->width = width;
    out->height = height;
    out->rgba = rgba;
    return true;
}

bool car_model_read_profile(const char *path, const CarModel **out)
{
    if (path == NULL || out == NULL) return false;
    *out = NULL;
    FILE *file = fopen(path, "rb");
    if (file == NULL) return false;
    const char *prefix = "# carmodels.model = ";
    char line[1024];
    bool ok = true;
    while (fgets(line, sizeof(line), file) != NULL) {
        if (strncmp(line, prefix, strlen(prefix)) != 0) continue;
        char code[64], extra;
        if (*out != NULL || sscanf(line + strlen(prefix), "%63s %c", code, &extra) != 1) {
            ok = false;
            break;
        }
        *out = car_model_at(car_model_find(code));
        if (*out == NULL) {
            ok = false;
            break;
        }
    }
    ok = ok && !ferror(file);
    return fclose(file) == 0 && ok;
}

bool car_model_append_profile(const char *path, const CarAppearanceSpec *appearance)
{
    const CarModel *model = car_model_selected(appearance);
    if (path == NULL || model == NULL) return false;
    FILE *file = fopen(path, "ab");
    if (file == NULL) return false;
    const bool ok = fprintf(file, "# carmodels.model = %s\n", model->code) > 0;
    return fclose(file) == 0 && ok;
}

void car_model_image_free(CarModelImage *image)
{
    if (image == NULL) return;
    stbi_image_free(image->rgba);
    memset(image, 0, sizeof(*image));
}

bool car_model_layout(const CarModel *model, const VehicleSpec *spec, float steerRad,
                      CarModelLayout *out)
{
    if (model == NULL || spec == NULL || out == NULL || !isfinite(steerRad) ||
        model->sourceLength <= 0.0f || model->orthoSpan <= 0.0f || model->frameSize <= 0 ||
        model->frameCount < 1 || model->angleStepDeg <= 0 || !vehicle_spec_is_valid(spec))
        return false;
    memset(out, 0, sizeof(*out));
    const float angle = steerRad * OVERSTEER_RAD2DEG;
    out->frame =
        (int)clampf(roundf((angle - (float)model->firstAngleDeg) / (float)model->angleStepDeg),
                    0.0f, (float)(model->frameCount - 1));
    /* Uniform scaling retains the mesh proportions. Length follows the researched spec;
     * the source can include mirrors outside the physical body's width convention. */
    out->imageWidthM = model->orthoSpan / model->sourceLength * spec->lengthOverallM;
    out->imageHeightM = out->imageWidthM;
    const float metresPerPixel = out->imageHeightM / (float)model->frameSize;
    const float centreXM =
        (spec->cgToFrontM + spec->frontOverhangM - spec->cgToRearM - spec->rearOverhangM) *
        0.5f;
    out->originPx = (Vector2){ (float)model->frameSize * 0.5f,
                               (float)model->frameSize * 0.5f + centreXM / metresPerPixel };
    return true;
}
