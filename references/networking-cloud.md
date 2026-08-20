# Wi-Fi, networking, and cloud

## Evidence routes

- Wi-Fi API and events: `hi_wifi_api.h`, `hi_net_api.h`, PZ `bsp_wifi.c`, `22_wifi_ap`, and `23_wifi_sta`.
- TCP/UDP/socket behavior: PZ `24_wifi_udp`, `25_wifi_tcp`, Pegasus client/server examples, and the bundled lwIP headers/source.
- MQTT: PZ `bsp_mqtt.c` and `26_wifi_mqtt`; also inspect bundled Paho examples and their exact library wiring.
- Huawei IoTDA: PZ `27_wifi_huawei_iotda` and its BUILD dependencies.
- HTTP, SNTP, CoAP, cJSON: query the example/document indexes and verify the selected component is enabled and linked.
- TLS/DTLS: use the bundled mbedTLS version, SDK security configuration, certificate storage, entropy/time prerequisites, and SDK documentation. Do not paste APIs from a newer mbedTLS release.

## Integration order

Initialize the board/network stack, register callbacks, start or join Wi-Fi, wait for a usable link/IP event, then create sockets or protocol clients. Bound reconnect loops, close resources on failure, and avoid blocking networking inside callbacks. Credentials and cloud secrets belong in user-controlled configuration, not generated source unless explicitly requested.
