/* Source-mesh sprite upload, compositing and catalog browsing. */
#if !defined(OVERSTEER_HEADLESS)

#include "render/render_internal.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "core/math_utils.h"
#include "core/units.h"
#include "render/car_model.h"

#define MODEL_FRAMES_MAX 13
#define GALLERY_COLS 4
#define GALLERY_ROWS 4
#define GALLERY_PER_PAGE (GALLERY_COLS * GALLERY_ROWS)

typedef struct {
    const CarModel *model;
    Texture2D frames[MODEL_FRAMES_MAX];
    bool ready;
} ModelTextures;

static ModelTextures s_car;
static ModelTextures s_gallery[GALLERY_PER_PAGE];
static int s_galleryPage;

static void textures_unload(ModelTextures *textures)
{
    for (int i = 0; i < MODEL_FRAMES_MAX; i++)
        if (textures->frames[i].id != 0) UnloadTexture(textures->frames[i]);
    memset(textures, 0, sizeof(*textures));
}

static bool textures_load(ModelTextures *textures, const CarModel *model)
{
    if (textures->ready && textures->model == model) return true;
    textures_unload(textures);
    if (model == NULL || model->frameCount > MODEL_FRAMES_MAX) return false;
    CarModelImage atlas;
    if (!car_model_load(model, &atlas)) return false;
    size_t frameBytes = 0;
    for (int size = model->frameSize; size > 0; size /= 2)
        frameBytes += (size_t)size * (size_t)size * 4;
    unsigned char *frame = (unsigned char *)malloc(frameBytes);
    bool ok = frame != NULL;
    for (int i = 0; i < model->frameCount && ok; i++) {
        size_t offset = 0;
        int top = 0;
        const int rows = (model->frameCount + model->columns - 1) / model->columns;
        for (int level = 0, size = model->frameSize; level < model->mipLevels;
             level++, size /= 2) {
            const int x = i % model->columns * size;
            const int y = top + i / model->columns * size;
            const size_t stride = (size_t)size * 4;
            for (int row = 0; row < size; row++)
                memcpy(frame + offset + (size_t)row * stride,
                       atlas.rgba + ((size_t)(y + row) * (size_t)atlas.width + (size_t)x) * 4,
                       stride);
            offset += stride * (size_t)size;
            top += rows * size;
        }
        const Image image = { .data = frame,
                              .width = model->frameSize,
                              .height = model->frameSize,
                              .mipmaps = model->mipLevels,
                              .format = PIXELFORMAT_UNCOMPRESSED_R8G8B8A8 };
        textures->frames[i] = LoadTextureFromImage(image);
        ok = textures->frames[i].id != 0;
        if (ok) {
            /* Offline linear-light mip levels preserve fine detail. Each pose has
             * an isolated chain, so neighboring atlas tiles cannot bleed. */
            SetTextureFilter(textures->frames[i], TEXTURE_FILTER_TRILINEAR);
        }
    }
    free(frame);
    car_model_image_free(&atlas);
    if (!ok) {
        textures_unload(textures);
        return false;
    }
    textures->model = model;
    textures->ready = true;
    return true;
}

static void draw_model(const ModelTextures *textures, const CarModelLayout *layout,
                       Vector2 centrePx, float headingRad, float ppm)
{
    if (!textures->ready) return;
    const Texture2D frame = textures->frames[layout->frame];
    const Rectangle source = { 0, 0, (float)frame.width, (float)frame.height };
    const Rectangle destination = { centrePx.x, centrePx.y, layout->imageWidthM * ppm,
                                    layout->imageHeightM * ppm };
    const Vector2 origin = { layout->originPx.x * destination.width / (float)frame.width,
                             layout->originPx.y * destination.height / (float)frame.height };
    const float rotation = 90.0f + units_heading_to_rotation_deg(headingRad);
    BeginBlendMode(BLEND_ALPHA_PREMULTIPLY);
    Rectangle shadow = destination;
    shadow.x += 0.04f * ppm;
    shadow.y += 0.06f * ppm;
    DrawTexturePro(frame, source, shadow, origin, rotation, (Color){ 0, 0, 0, 65 });
    DrawTexturePro(frame, source, destination, origin, rotation, WHITE);
    EndBlendMode();
}

void render_vehicle_draw(const Game *game, const VehicleDrawState *draw)
{
    const CarModel *model = car_model_selected(&game->appearance);
    if (!textures_load(&s_car, model)) return;
    const float steer =
        game->spec.frontWheelCount == 1.0f
            ? draw->wheelAngleRad[WHEEL_FRONT_LEFT]
            : (draw->wheelAngleRad[WHEEL_FRONT_LEFT] + draw->wheelAngleRad[WHEEL_FRONT_RIGHT]) *
                  0.5f;
    CarModelLayout layout;
    if (!car_model_layout(model, &game->spec, steer, &layout)) return;
    draw_model(&s_car, &layout,
               units_world_to_render_px(draw->positionM, game->renderPixelsPerMeter),
               draw->headingRad, game->renderPixelsPerMeter);
}

void render_vehicle_resources_unload(void)
{
    textures_unload(&s_car);
    for (int i = 0; i < GALLERY_PER_PAGE; i++) textures_unload(&s_gallery[i]);
    s_galleryPage = 0;
}

void render_vehicle_resources_reset(void)
{
    render_vehicle_resources_unload();
}

int render_gallery_page_count(void)
{
    return (car_model_count() + GALLERY_PER_PAGE - 1) / GALLERY_PER_PAGE;
}

void render_draw_gallery(Game *game, int page)
{
    const int pages = render_gallery_page_count();
    if (IsKeyPressed(KEY_ESCAPE)) {
        game->dev.galleryPage = 0;
        return;
    }
    if (IsKeyPressed(KEY_RIGHT) || IsKeyPressed(KEY_PAGE_DOWN)) page++;
    if (IsKeyPressed(KEY_LEFT) || IsKeyPressed(KEY_PAGE_UP)) page--;
    page = (int)clampf((float)page, 1, (float)pages);
    game->dev.galleryPage = page;
    if (s_galleryPage != page) {
        for (int slot = 0; slot < GALLERY_PER_PAGE; slot++)
            textures_load(&s_gallery[slot], car_model_at((page - 1) * GALLERY_PER_PAGE + slot));
        s_galleryPage = page;
    }
    BeginDrawing();
    ClearBackground((Color){ 21, 24, 29, 255 });
    int selected = -1;
    const int cellW = SCREEN_W / GALLERY_COLS, cellH = SCREEN_H / GALLERY_ROWS;
    for (int slot = 0; slot < GALLERY_PER_PAGE; slot++) {
        const int index = (page - 1) * GALLERY_PER_PAGE + slot;
        const CarModel *model = car_model_at(index);
        if (model == NULL) break;
        const int x = slot % GALLERY_COLS * cellW, y = slot / GALLERY_COLS * cellH;
        const Rectangle cell = { (float)x + 3, (float)y + 24, (float)cellW - 6,
                                 (float)cellH - 28 };
        const bool hovered = CheckCollisionPointRec(GetMousePosition(), cell);
        DrawRectangleRec(cell,
                         hovered ? (Color){ 39, 49, 61, 255 } : (Color){ 29, 33, 40, 255 });
        if (hovered && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) selected = index;
        CarModelLayout layout = {
            .frame = (0 - model->firstAngleDeg) / model->angleStepDeg,
            .imageWidthM = model->orthoSpan / model->sourceLength * model->physicalLengthM,
            .imageHeightM = model->orthoSpan / model->sourceLength * model->physicalLengthM,
            .originPx = { (float)model->frameSize * 0.5f, (float)model->frameSize * 0.5f }
        };
        draw_model(&s_gallery[slot], &layout,
                   (Vector2){ (float)x + (float)cellW * 0.5f, (float)y + (float)cellH * 0.5f },
                   OVERSTEER_PI * 0.5f, 23.0f);
        DrawText(model->name, x + 8, y + cellH - 27, 11, COL_TEXT);
    }
    DrawText(
        TextFormat("Choose vehicle - %d / %d - arrows to browse - click to select - Esc back",
                   page, pages),
        12, 6, 14, COL_TEXT);
    EndDrawing();
    if (selected >= 0 && game_select_model(game, car_model_at(selected)->code)) {
        game->dev.galleryPage = 0;
        /* The frame has been submitted; page textures can now be released safely. */
        for (int i = 0; i < GALLERY_PER_PAGE; i++) textures_unload(&s_gallery[i]);
        s_galleryPage = 0;
    }
}

#endif
