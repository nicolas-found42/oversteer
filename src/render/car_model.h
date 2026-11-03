/* Source-mesh sprite catalog and CPU image loading, shared by gameplay and tests.
 * No geometry or paint is generated from physics parameters. */
#ifndef OVERSTEER_CAR_MODEL_H
#define OVERSTEER_CAR_MODEL_H

#include <stdbool.h>
#include <stddef.h>

#include "physics/vehicle.h"
#include "render/car_appearance.h"

typedef struct {
    const char *code;
    const char *name;
    const char *path;
    float sourceLength;
    float orthoSpan;
    float physicalLengthM;
    int frameSize;
    int columns;
    int frameCount;
    int firstAngleDeg;
    int angleStepDeg;
    int mipLevels;
} CarModel;

typedef struct {
    int width;
    int height;
    unsigned char *rgba;
} CarModelImage;

typedef struct {
    int frame;
    float imageWidthM;
    float imageHeightM;
    Vector2 originPx;
} CarModelLayout;

int car_model_count(void);
const CarModel *car_model_at(int index);
int car_model_find(const char *code);
const CarModel *car_model_default(void);
bool car_model_select(CarAppearanceSpec *appearance, const char *code);
const CarModel *car_model_selected(const CarAppearanceSpec *appearance);
/* Optional presentation metadata in tuning profiles. A missing tag keeps a legacy
 * profile's appearance unchanged; an invalid/excluded tag rejects the load. */
bool car_model_read_profile(const char *path, const CarModel **out);
bool car_model_append_profile(const char *path, const CarAppearanceSpec *appearance);

/* Read the catalog's baked premultiplied RGBA PNG. Gameplay and tests consume the
 * same bytes. Draw with premultiplied alpha blending; do not blend these as straight RGBA. */
bool car_model_load(const CarModel *model, CarModelImage *out);
void car_model_image_free(CarModelImage *image);
bool car_model_layout(const CarModel *model, const VehicleSpec *spec, float steerRad,
                      CarModelLayout *out);

#endif
