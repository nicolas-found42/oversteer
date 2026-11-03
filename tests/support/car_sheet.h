/* Headless inspection of the same source-mesh sprite atlas used by the game. */
#ifndef OVERSTEER_CAR_SHEET_H
#define OVERSTEER_CAR_SHEET_H

#include <stdbool.h>
#include "physics/vehicle.h"
#include "render/car_model.h"

bool car_sheet_write(const char *outDir);
bool car_sheet_write_cards(const char *outDir);
bool car_sheet_write_spec(const VehicleSpec *spec, const CarModel *model, const char *prefix);

#endif
