---
title: "Wi-Fi, WebSocket, 실시간 UI와 데이터 저장"
date: 2026-06-05T20:36:00+09:00
draft: false
categories:
  - Embedded
tags:
  - ESP32
  - WebSocket
  - ESPAsyncWebServer
  - SPIFFS
  - WiFi
  - 재활자전거
summary: "ESPAsyncWebServer로 웹 서버를 올리고, WebSocket으로 센서 데이터를 실시간 전송하고, 측정이 끝나면 수백 KB의 바이너리 데이터를 브라우저로 내려받는 과정을 정리했다."
---

캘리브레이션까지 끝나면 센서 데이터가 실제 무게(kg)로 나온다. 이제 이 데이터를 어떻게 외부로 내보내느냐가 남는다. 유선 시리얼은 측정 중에 케이블이 걸리적거리고, Bluetooth는 지연이 있다. Wi-Fi + WebSocket을 선택했다.

## ESPAsyncWebServer를 쓴 이유

일반 `WebServer` 라이브러리도 있다. 차이는 블로킹 여부다.

일반 WebServer는 요청이 들어오면 처리가 끝날 때까지 루프가 멈춘다. 센서 샘플링을 40 SPS로 유지해야 하는 상황에서 루프가 블로킹되면 샘플이 빠진다.

`ESPAsyncWebServer`는 요청 처리를 별도 태스크로 넘긴다. 루프는 계속 돌고, 웹 요청은 백그라운드에서 처리된다. 실시간 샘플링과 웹 서버를 동시에 돌리려면 비동기가 필수였다.

```cpp
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");
```

## 웹 UI를 어디에 두는가 — IoT 장비의 일반적인 선택지

선택지는 세 가지다.

**클라우드 기반**: AWS IoT, Google Cloud IoT처럼 장비는 MQTT나 HTTP로 데이터만 올리고, UI는 외부 서버에서 제공한다. 상용 IoT 제품 대부분이 이 방식이다. 어디서든 접근 가능하고 데이터가 축적되지만, 인터넷 연결이 필수고 서버 운영 비용이 따른다.

**외부 대시보드 연동**: Node-RED, Grafana 같은 도구를 로컬 서버(PC나 라즈베리파이)에 설치하고 장비는 데이터만 보낸다. 산업용 IoT에서 많이 쓰는 방식이다. 별도 서버가 필요하지만 UI 구성이 자유롭다.

**장비 자체 호스팅**: 장비 안에 웹 서버를 올리고 UI까지 직접 서빙한다. 공유기만 있으면 브라우저로 바로 접근할 수 있고 외부 인프라가 필요 없다. ESP32 같은 마이크로컨트롤러 기반 프로젝트에서 자주 쓰는 방식이다.

## 이 프로젝트에서 SPIFFS를 선택한 이유

재활 측정 장비라는 특성상 클라우드나 외부 서버는 적합하지 않았다. 병원 네트워크 환경은 외부 접근이 제한되는 경우가 많고, 측정 데이터를 외부로 내보내는 것 자체가 민감할 수 있다. 장비 자체에서 모든 것이 해결되어야 했다.

장비 자체 호스팅을 선택했고, 그 안에서 웹 파일을 어디에 두느냐가 다시 선택지가 된다.

HTML을 C++ 문자열로 펌웨어에 하드코딩하면 추가 하드웨어 없이 가장 단순하게 구현할 수 있다. 하지만 CSS와 JavaScript까지 포함된 UI를 C++ 문자열로 관리하면 가독성이 떨어지고, 수정할 때마다 전체 펌웨어를 다시 컴파일하고 업로드해야 한다.

SPIFFS는 ESP32 플래시의 별도 파티션에 파일 시스템을 만든다. `index.html`, `script.js`, `style.css`를 독립적인 파일로 올려두면 UI를 수정할 때 펌웨어를 건드리지 않고 파일만 다시 업로드하면 된다. 펌웨어와 UI의 배포 단위가 분리되고, 웹 파일을 일반 텍스트 파일처럼 편집기에서 작업할 수 있다.

단점도 있다. SPIFFS 파티션 크기는 보드 설정에 따라 다르지만 수 MB 수준이라 복잡한 SPA(React, Vue 등)를 올리기에는 부족하다. 또한 SPIFFS는 현재 공식적으로 deprecated 상태로, ESP32 Arduino에서는 LittleFS로 이전이 권장된다. 이 프로젝트를 진행할 당시에는 SPIFFS가 더 보편적이었기 때문에 그대로 사용했다.

웹 UI(`index.html`, `script.js`, `style.css`)는 SPIFFS에 올려두고 서버가 그걸 읽어서 응답한다.

```cpp
server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(SPIFFS, "/index.html", "text/html", false, processor);
});

server.serveStatic("/", SPIFFS, "/");
```

`serveStatic`이 `/` 경로로 들어오는 정적 파일 요청을 SPIFFS에서 찾아 응답한다. `index.html`에서 로드하는 `script.js`, `style.css`도 자동으로 처리된다.

`processor`는 HTML 안의 플레이스홀더를 센서 초기값으로 치환하는 함수다:

```cpp
String processor(const String& var){
    if(var == "RIGHTARM")  return String((float)Sensors.DATA1 * LoadcellCalGain1, 3);
    if(var == "LEFTARM")   return String((float)Sensors.DATA2 * LoadcellCalGain2, 3);
    if(var == "RIGHTFOOT") return String((float)Sensors.DATA3 * LoadcellCalGain3, 3);
    if(var == "LEFTFOOT")  return String((float)Sensors.DATA4 * LoadcellCalGain4, 3);
    if(var == "ANGLE")     return String((float)Sensors.encoderAngle * AS5600_RAW_TO_DEGREES, 2);
    return String();
}
```

페이지를 처음 로드할 때 빈 칸 대신 현재 센서값이 바로 보인다.

## Wi-Fi 연결

EEPROM에 저장된 SSID와 비밀번호를 읽어 연결을 시도한다.

```cpp
WiFi.mode(WIFI_AP_STA);
WiFi.begin(ssid, password);
```

`WIFI_AP_STA`는 Station 모드(공유기에 연결)와 AP 모드(자체 핫스팟 생성)를 동시에 사용하는 모드다. 연결에 실패하면 시리얼로 주변 Wi-Fi 목록을 출력하고 번호를 입력받아 새로 연결한다:

```cpp
int n = WiFi.scanNetworks();
for (int i = 0; i < n; ++i) {
    Serial.print(i + 1);  Serial.print(") ");
    Serial.println(WiFi.SSID(i));
}
Serial.print("Select No. of SSIDs : ");
// 입력받아 EEPROM에 저장
EEPROM.writeString(EEPROM_SSID, WiFi.SSID(NoSSID));
EEPROM.writeString(EEPROM_PASS, passWordstr);
EEPROM.commit();
```

한 번 연결하면 EEPROM에 저장되니 다음 부팅부터는 자동으로 연결된다.

## WebSocket 이벤트 핸들러

WebSocket은 클라이언트(브라우저)와 서버(ESP32) 사이의 양방향 통신 채널이다. 연결, 해제, 데이터 수신을 하나의 핸들러에서 처리한다:

```cpp
void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
             AwsEventType type, void *arg, uint8_t *data, size_t len) {
    switch (type) {
    case WS_EVT_CONNECT:
        client->ping();
        break;

    case WS_EVT_DISCONNECT:
        break;

    case WS_EVT_DATA:
        if (strcmp((char*)data, "START") == 0) {
            workingPointer = packetPointer;  packetCounter = 0;
            quit = false;
        } else if (strcmp((char*)data, "STOP") == 0) {
            quit = true;
        } else if (strcmp((char*)data, "SAVE") == 0) {
            client_id = client->id();
            save = true;
        }
        break;
    }
}
```

클라이언트에서 텍스트 명령 세 가지로 상태를 제어한다:

| 명령 | 동작 |
|------|------|
| `START` | PSRAM 버퍼 초기화 후 측정 시작 |
| `STOP` | 측정 중단 |
| `SAVE` | 버퍼에 쌓인 데이터 전송 시작 |

![ELEPHANT WEB MONITOR UI](/images/esp32/rehab-web-ui.png)

## 센서 데이터 실시간 전송

루프에서 16 샘플(약 0.4초)마다 JSON을 모든 클라이언트에 브로드캐스트한다:

```cpp
if (!NoNetwork && (WebSampleIdx >= 16)) {
    WebSampleIdx = 0;
    sendSensorsWs(null);    // null = 전체 클라이언트
    ws.cleanupClients();
}
```

```cpp
void sendSensorsWs(AsyncWebSocketClient *client) {
    readings["s1"] = String((float)Sensors.DATA1 * LoadcellCalGain1, 3);
    readings["s2"] = String((float)Sensors.DATA2 * LoadcellCalGain2, 3);
    readings["s3"] = String((float)Sensors.DATA3 * LoadcellCalGain3, 3);
    readings["s4"] = String((float)Sensors.DATA4 * LoadcellCalGain4, 3);
    readings["s5"] = (Sensors.encoderAngle == 8192.0)
        ? "N.C."
        : String((float)Sensors.encoderAngle * AS5600_RAW_TO_DEGREES, 2);
    readings["s6"] = String(packetCounter);

    String buffer = JSON.stringify(readings);
    if (client) client->text(buffer);
    else        ws.textAll(buffer);
}
```

측정 중이 아닐 때(`quit = true`)는 각도 자리에 "STOPPED"가 전송된다. 브라우저에서 이 값을 보고 UI 상태를 표시한다.

## 바이너리 청크로 대용량 데이터 보내기

40 SPS로 최대 36분을 측정하면 PSRAM에 누적되는 구조체 배열이 약 86,400개다. 이걸 한 번에 WebSocket으로 보내면 TCP 버퍼를 초과한다.

5분 단위(12,000개)로 잘라서 보낸다:

```cpp
#define PACKET_LENGTH  (5*60*40)  // 5분치

int pn = packetCounter / PACKET_LENGTH;  // 5분 청크 개수
int pr = packetCounter % PACKET_LENGTH;  // 나머지

for (int p = 0; p < pn; p++) {
    ws.binary(client_id, (uint8_t*)workingPointer,
              PACKET_LENGTH * sizeof(struct sensors));
    workingPointer += PACKET_LENGTH;
    delay(500);
}
if (pr) {
    ws.binary(client_id, (uint8_t*)workingPointer,
              pr * sizeof(struct sensors));
    delay(100);
}
// 1바이트 종료 신호
ws.binary(client_id, (uint8_t*)workingPointer, 1);
```

`delay(500)`은 브라우저가 청크를 처리하는 시간을 확보하기 위한 것이다. 너무 빠르게 연속으로 보내면 클라이언트 측 버퍼가 넘친다.

마지막에 1바이트를 보내는 이유는 종료 신호다. 브라우저에서 "1바이트짜리 패킷이 오면 전송 완료"로 판단해 파일 저장 처리를 시작한다.

브라우저 쪽에서는 `ArrayBuffer` 조각을 받을 때마다 누적했다가 종료 신호가 오면 파일로 저장한다:

```javascript
ws.onmessage = (event) => {
    if (event.data instanceof ArrayBuffer) {
        if (event.data.byteLength === 1) {
            // 종료 신호 → 파일 저장
            saveToFile(chunks);
        } else {
            chunks.push(event.data);
        }
    }
};
```

## 단독 모드

부팅 중 버튼을 누른 채로 켜면 Wi-Fi 없이 동작한다:

```cpp
if (!digitalRead(ESP32_BUTTON)) {
    NoNetwork = true;
    isPsram = false;
}
```

이 경우 웹 서버도 WebSocket도 시작되지 않는다. 시리얼 모니터로만 데이터를 확인할 수 있다. 캘리브레이션 작업이나 센서 단순 확인 시 사용한다.
