#include <esp_now.h>
#include <WiFi.h>
#include <WebServer.h>
// these are the dependencies we need for the sender. esp_now for the radio, wifi to connect to the router, and webserver to handle http requests

// the hardcoded mac address of the reciever esp32 so the sender knows where to shoot the data
uint8_t receiverMacAddress[] = {}; // enter your reciever mac address here 


// router ssid and password so python can reach this board, enter your own
const char* ssid = "";
const char* password = "";


WebServer server(80); // define the port we use which is 80, as well as create the web server object


void handleData() {
    // extract the raw http request body as a string using plain
    String body = server.arg("plain");

    Serial.println();
    Serial.println("HTTP DATA RECEIVED:");
    Serial.println(body); // log the payload to serial so i can track whats coming in

  
    // beam that json body straight to the reciever using its mac address. 
    // cast the string to uint8_t* since the low level esp-now radio only accepts raw bytes. add 1 to include the null terminator
    esp_err_t result = esp_now_send(receiverMacAddress, (uint8_t*)body.c_str(), body.length() + 1);

    if (result == ESP_OK) {
        Serial.println("ESP-NOW send accepted");
    } else {
        Serial.println("ESP-NOW send failed");
    }

  
    // shoot an http 200 response back to python to complete the loop
    server.send(200, "text/plain", "data received");
}


// asynchronous callback function that automatically gets called when an esp_now transmission finishes
void senderCallback(const uint8_t *macAddress, esp_now_send_status_t status) {
    // this simply tells us if it was successful or not
    if (status == ESP_NOW_SEND_SUCCESS) {
        Serial.println("Packet delivered");
    } else {
        Serial.println("Packet failed");
    }
}


void setup() {
    Serial.begin(115200); // initialise serial

    Serial.println();
    Serial.println("starting sender");
    WiFi.mode(WIFI_STA); // set wifi to station mode
    WiFi.begin(ssid, password); // create wifi connection

    // block and wait until the wifi actually connects
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.println("connecting to wiFi...");
    }

    Serial.println();
    Serial.println("WiFi connected");
    
    Serial.print("Sender IP address: ");
    Serial.println(WiFi.localIP()); // print ip so i know what url to put in the python script

    Serial.print("Sender MAC address: ");
    Serial.println(WiFi.macAddress());

    Serial.print("Sender WiFi channel: ");
    Serial.println(WiFi.channel());

  
    server.on("/data", HTTP_POST, handleData); // route the /data endpoint to trigger the handledata function
    server.begin(); // configure http
    Serial.println("HTTP server started");

    
    // initialize esp_now radio
    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW initialization failed");
        return;
    }
    Serial.println("ESP-NOW initialized");

  
    // register callback so we actually know if the packet landed or failed
    esp_now_register_send_cb(senderCallback);

   
    esp_now_peer_info_t peer; // setup the reciever as a peer

    memset(&peer, 0, sizeof(peer)); // clear memory with memset so no obsolete data messes it up
    memcpy(peer.peer_addr, receiverMacAddress, 6); // copy the target mac address over

   
    // the router assigns the channel, so we just match it here to avoid the peer channel mismatch error
    peer.channel = WiFi.channel(); 
    
    peer.ifidx = WIFI_IF_STA; // use station interface
    peer.encrypt = false; // no encryption needed for this project


    // finally add the peer so esp_now knows who it is talking to
    if (esp_now_add_peer(&peer) != ESP_OK) {
        Serial.println("Peer add failed");
    } else {
        Serial.println("Receiver peer added successfully");
    }

    Serial.println();
    Serial.println("SENDER READY");
}


void loop() {
    // this constantly checks for incoming network traffic and triggers the handler if a python request hits
    server.handleClient();
}