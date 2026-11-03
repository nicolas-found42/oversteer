/*
 * car_appearance.h — stable, presentation-only identity for source-model sprites.
 *
 * Model identity lives outside VehicleSpec and never changes solver behavior or checksums.
 * An empty code selects the catalog's default source model for legacy tuning profiles.
 */
#ifndef OVERSTEER_CAR_APPEARANCE_H
#define OVERSTEER_CAR_APPEARANCE_H

typedef struct {
    char modelCode[64]; /* Presentation identity; never read by the physics solver. */
} CarAppearanceSpec;

#endif /* OVERSTEER_CAR_APPEARANCE_H */
