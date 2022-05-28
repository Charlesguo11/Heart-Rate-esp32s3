#include "who_camera.h"
#include "who_human_face_detection.hpp"
#include "app_wifi.h"
#include "app_httpd.hpp"
#include "app_mdns.h"
#include "sys/socket.h"

static QueueHandle_t xQueueAIFrame = NULL;
static QueueHandle_t xQueueHttpFrame = NULL;

extern "C" void app_main()
{
    app_wifi_main();
    app_mdns_main();

    xQueueAIFrame = xQueueCreate(2, sizeof(camera_fb_t *));

    register_camera(PIXFORMAT_RGB565, FRAMESIZE_QVGA, 2, xQueueAIFrame);
    register_httpd(xQueueAIFrame, NULL, true);
}