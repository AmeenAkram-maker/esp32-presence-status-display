#include <Adafruit_GFX.h>    // core graphics library used for drawing shapes and text
#include <Adafruit_ST7735.h> // hardware specific library for our st7735 screen
#include <SPI.h>             // needed for hardware spi communication with the screen
#include <esp_now.h>         // the wireless protocol we use to get data from the sender
#include <WiFi.h>            // wifi library required to connect to the router for ntp
#include <esp_wifi.h>        // lower level wifi library to manage the radio channel
#include <ArduinoJson.h>     // library to parse the raw json text into an object
#include <time.h>            // needed to fetch and store real world time via ntp
// the above are the libraries that we need for the reciever sid eof the project ]

#define TFT_SCK 18  // spi clock pin
#define TFT_SDA 23  // spi data out pin (mosi)
#define TFT_RES 32  // reset pin for the screen
#define TFT_DC 33   // data/command pin
#define TFT_CS 25   // chip select pin
#define TFT_BL 17   // backlight control pin
// the above i teh definition for the pins for the tft. sck sda res dc cs and bl are: sck is simply the spi clock line. it tells the tft when to read each bit from the data line. sda is the spi data line. this contains actual pixel data from the esp32 ==>tft res resets the screen. dc tells the type of information. 0 means set the rotation or clear the screen while 1 means data like pixel colours. cs means chip select. specifies that the esp32 is talking to the tft at a given moment in time since multiple spi devices can us ethe asme bus. and lastly bl means controls the led backlight, you can turn it on or off or change the brightness using pwm

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RES); // these creates a tft object with the definitions that we created before 


char buffer[512]; // this is the buffer for the characters that we recieve. it is in bytes. ultimately trhis contains the json data that the sender sends over. 
volatile bool recieved = false; // this is a flag variable for if the callback recieves data. its volatile since its modified during an interrupt. 

JsonDocument calendarDocument; // here i create a json object. this stores the parsed calendar data 
unsigned long lastTimeCheck = 0; // this is the variable needed for the non blocking timer. we need it to store the time taht has passed since the esp32 started. 
const unsigned long TIME_CHECK_INTERVAL = 1000; // this is the itnerval i am using to check y
int displayedActivityIndex = -2;
// i have certain sentinal values to check what activity is being displayed on the tft. -1 means no activity, 0 means its the first activity, 1 = the second activity etc. 


const char* ssid = ""; // wifi ssd
const char* password = ""; // wifi password
// needed to create http server etc. 



// this is the conways game of life section, 
// i want this to run when theres no activity, the cells should fit nicely on screen
#define CELL_SIZE 4          // here ive defined pixel size of the cells 
#define MAX_GRID_COLS 40     // this is jsuta safe upper bound for the grid arrays 
#define MAX_GRID_ROWS 40     // safe upper limit for rows to prevent memory overflow

#define STALE_LIMIT 5        // start the game again if the pattern doesnt change
#define MAX_GENERATIONS 600  // after 600 generations restartt the game anyway since its probably either fizzled out or stable

const unsigned long LIFE_FRAME_DELAY = 150; // this is the nubmer of ms between generatyions.

int gridCols = 0; // actual columns we will use based on screen width
int gridRows = 0; // actual rows we will use based on screen height

bool lifeGrid[MAX_GRID_ROWS][MAX_GRID_COLS];     // 2d array holding the current generation of cells
bool lifeGridNext[MAX_GRID_ROWS][MAX_GRID_COLS]; // 2d array to calculate the next state into

bool gameOfLifeInitialized = false; // flag so we only calculate grid dimensions once
unsigned long lastLifeTick = 0;     // tracks the time for the animation frame rate
int staleGenerations = 0;           // counts how many frames the grid has been stuck
unsigned long generationCount = 0;  // total frames since the animation started


void drawCell(int row, int col, bool alive) {
    // pick white if the cell is alive, otherwise paint it black to hide it
    uint16_t color = alive ? ST77XX_WHITE : ST77XX_BLACK;
    // draw the actual square on the tft at the correct x and y coordinates
    tft.fillRect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE, color);
}


void randomizeGrid() {
    // loop through every row in the active grid
    for (int row = 0; row < gridRows; row++) {
        // loop through every column
        for (int col = 0; col < gridCols; col++) {
            // roughly 28% alive gives the game enough density so it doesnt just die straight away
            lifeGrid[row][col] = (random(100) < 28);
        }
    }
}


void drawFullGrid() {
    // iterate through all rows
    for (int row = 0; row < gridRows; row++) {
        // iterate through all columns
        for (int col = 0; col < gridCols; col++) {
            // draws the entire board. i only really use this right after randomising the grid
            drawCell(row, col, lifeGrid[row][col]);
        }
    }
}


int countAliveNeighbours(int row, int col) {
    int count = 0; // start neighbour counter at 0

    // loop from -1 to +1 to check the row above, current row, and row below
    for (int dr = -1; dr <= 1; dr++) {
        // loop from -1 to +1 to check the left, middle, and right columns
        for (int dc = -1; dc <= 1; dc++) {
            // skip the current cell itself because it isnt its own neighbour
            if (dr == 0 && dc == 0) continue; 

            // use modulo to wrap the edges so shapes dont just hit the wall and disappear
            int neighbourRow = (row + dr + gridRows) % gridRows;
            int neighbourCol = (col + dc + gridCols) % gridCols;

            // if the wrapped neighbour cell is alive, increment the counter
            if (lifeGrid[neighbourRow][neighbourCol]) {
                count++;
            }
        }
    }

    return count; // return total number of living neighbours
}


void randomizeAndRedraw() {
    randomizeGrid();             // reset the array with a new random layout
    tft.fillScreen(ST77XX_BLACK); // clear the screen completely black
    drawFullGrid();              // render the new starting layout
    staleGenerations = 0;        // reset the stuck counter
    generationCount = 0;         // reset the total frames counter
}


void initGameOfLife() {
    // figure out how many columns fit based on screen width
    gridCols = tft.width() / CELL_SIZE;
    // figure out how many rows fit based on screen height
    gridRows = tft.height() / CELL_SIZE;

    // clamping the values so we never write outside the array limits and crash memory
    if (gridCols > MAX_GRID_COLS) gridCols = MAX_GRID_COLS;
    if (gridRows > MAX_GRID_ROWS) gridRows = MAX_GRID_ROWS;

    randomizeAndRedraw(); // set up the first random board
    gameOfLifeInitialized = true; // flag it as initialized so we dont run this again
}


void stepGameOfLife() {
    int aliveCount = 0;    // track if the entire board is dead
    bool changed = false;  // track if the board actually moved this frame

    // loop through all rows
    for (int row = 0; row < gridRows; row++) {
        // loop through all columns
        for (int col = 0; col < gridCols; col++) {
            // check how many neighbours this specific cell has
            int neighbours = countAliveNeighbours(row, col);
            bool alive = lifeGrid[row][col]; // current state of the cell
            bool nextAlive; // what the cell will become next frame

            if (alive) {
                // a live cell survives if it has 2 or 3 neighbours, else it dies
                nextAlive = (neighbours == 2 || neighbours == 3);
            } else {
                // a dead cell comes back to life if it has exactly 3 neighbours
                nextAlive = (neighbours == 3);
            }

            // save the new state into the buffer array
            lifeGridNext[row][col] = nextAlive;

            if (nextAlive) {
                aliveCount++; // keep track of total living cells
            }

            // only update the tft pixels for cells that actually changed to save processing time
            if (nextAlive != alive) {
                changed = true; // the board is not stuck
                drawCell(row, col, nextAlive); // redraw just this one cell
            }
        }
    }

    // copy the new calculated state over to the main active grid array
    memcpy(lifeGrid, lifeGridNext, sizeof(lifeGrid));

    // if there are no live cells left, just restart the game immediately
    if (aliveCount == 0) {
        randomizeAndRedraw();
        return;
    }

    // if the board didnt change at all, increment the stuck counter
    if (!changed) {
        staleGenerations++;
    } else {
        staleGenerations = 0; // reset it if things are still moving
    }

    // restart the simulation if it gets permanently stuck or runs for too long
    if (staleGenerations >= STALE_LIMIT || generationCount >= MAX_GENERATIONS) {
        randomizeAndRedraw();
        return;
    }

    generationCount++; // increment total generation frames
}


void drawGameOfLife() {
    // if we just switched to empty calendar, set up the grid
    if (!gameOfLifeInitialized) {
        initGameOfLife();
    }

    // non blocking timer so the animation runs on its own framerate
    if (millis() - lastLifeTick < LIFE_FRAME_DELAY) {
        return; // exit early if it isnt time for the next frame yet
    }
    lastLifeTick = millis(); // update the timer

    stepGameOfLife(); // calculate and draw the next generation
}

void recievercallback(const uint8_t *senderMacAddress, const uint8_t *senderdata, int length) {
    // checking to make sure the incoming packet isnt bigger than the buffer to prevent overflow
    if (length >= sizeof(buffer)) {
        Serial.println("ERROR: Incoming packet too large");
        return; // drop the packet if its too big
    }

    // safely copy the data into our buffer array
    memcpy(buffer, senderdata, length);

    // add a null terminator so c++ treats the buffer as a valid string
    buffer[length] = '\0';

    // raise the flag so the main loop knows we have fresh data to parse
    recieved = true;
}


int timeToMinutes(const char* timeString) {
    int hour;   // variable to hold extracted hour
    int minute; // variable to hold extracted minute

    // extract the integers from the HH:MM formatted string
    sscanf(timeString, "%d:%d", &hour, &minute);
    // return total minutes past midnight for easy inequality math later
    return (hour * 60) + minute;
}


void displayActivity(JsonObject activity) {
    // extract all the fields from the json object
    const char* activityName = activity["Activity"];
    const char* startTime = activity["Start_Time"];
    const char* endTime = activity["End_Time"];
    const char* category = activity["Category"];

    // print everything to serial for debugging
    Serial.println();
    Serial.println("DISPLAYING CURRENT ACTIVITY");
    Serial.print("Activity: ");
    Serial.println(activityName);
    Serial.print("Start: ");
    Serial.println(startTime);
    Serial.print("End: ");
    Serial.println(endTime);
    Serial.print("Category: ");
    Serial.println(category);

    // wipe the screen to black before drawing new text
    tft.fillScreen(ST77XX_BLACK);

    // reset the cursor to the top left
    tft.setCursor(0, 0);

    // set font color to white and size to standard
    tft.setTextColor(ST77XX_WHITE);
    tft.setTextSize(1);

    // print the actual calendar details to the tft display
    tft.println("CALENDAR");
    tft.println();
    tft.print("Activity: ");
    tft.println(activityName);
    tft.print("Start: ");
    tft.println(startTime);
    tft.print("End: ");
    tft.println(endTime);
    tft.print("Category: ");
    tft.println(category);
}


void displayNoActivity() {
    // debug print
    Serial.println();
    Serial.println("NO CURRENT ACTIVITY");
    
    // clear screen to black
    tft.fillScreen(ST77XX_BLACK);
    // reset cursor
    tft.setCursor(0, 0);
    // set text styling
    tft.setTextColor(ST77XX_WHITE);
    tft.setTextSize(1);
    
    // print the empty state message
    tft.println("CALENDAR");
    tft.println();
    tft.println("No current activity");
}


int findCurrentActivity() {
    // check if the global json document is empty first
    if (calendarDocument.isNull()) {
        return -1; // return the no activity sentinel value
    }

    // cast the root json object into an array we can loop over
    JsonArray activities = calendarDocument.as<JsonArray>();

    // double check that it actually parsed as an array correctly
    if (activities.isNull()) {
        Serial.println("ERROR: Calendar JSON is not an array");
        return -1; // abort if the json structure is wrong
    }

    // create a struct to hold the real world time
    struct tm timeinfo;

    // fetch the time from ntp
    if (!getLocalTime(&timeinfo)) {
        Serial.println("FAILED TO GET CURRENT TIME");
        return -1; // abort if we dont know what time it is
    }

    // convert the current hours and minutes into total minutes past midnight
    int currentMinutes = (timeinfo.tm_hour * 60) + timeinfo.tm_min;

    // print current time variables for debugging
    Serial.print("Current time: ");
    Serial.println(&timeinfo, "%H:%M:%S");
    Serial.print("Current minutes: ");
    Serial.println(currentMinutes);

    // loop through every single activity in the json array
    for (int i = 0; i < activities.size(); i++) {
        JsonObject activity = activities[i]; // get the specific activity object
        
        // pull the start and end time strings
        const char* startTime = activity["Start_Time"];
        const char* endTime = activity["End_Time"];

        // convert them into minutes for the math check
        int startMinutes = timeToMinutes(startTime);
        int endMinutes = timeToMinutes(endTime);

        // debug prints to track the loop progress
        Serial.print("Checking index ");
        Serial.println(i);
        Serial.print("Start: ");
        Serial.println(startMinutes);
        Serial.print("End: ");
        Serial.println(endMinutes);

        // check if current time is equal to or greater than start, and strictly less than end
        if (currentMinutes >= startMinutes && currentMinutes < endMinutes) {
            return i; // return the index of the activity that is happening right now
        }
    }

    // if the loop finishes and nothing matched, return -1 to show schedule is empty
    return -1;
}


void setup() {
    // start serial monitor at 115200 baud rate
    Serial.begin(115200);

    // start the spi bus using our custom defined pins
    SPI.begin(TFT_SCK, -1, TFT_SDA);
    // initialize the adafruit screen object
    tft.initR(INITR_BLACKTAB);
    // fill it black so it doesnt show garbage pixels on boot
    tft.fillScreen(ST77XX_BLACK);

    // set the backlight pin to output mode
    pinMode(TFT_BL, OUTPUT);
    // turn the backlight on immediately
    digitalWrite(TFT_BL, HIGH);

    // set wifi to station mode (client)
    WiFi.mode(WIFI_STA);
    // connect to the home router
    WiFi.begin(ssid, password);

    Serial.println("Connecting to WiFi...");

    // block the code and wait until wifi actually connects
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi connected");
    // print the mac address so we can copy it into the sender code
    Serial.print("Receiver MAC: ");
    Serial.println(WiFi.macAddress());

    // configure the timezone to uk gmt/bst and set the ntp servers
    configTzTime("GMT0BST,M3.5.0/1,M10.5.0/2", "pool.ntp.org", "time.nist.gov");
    Serial.println("Waiting for time synchronisation...");

    struct tm timeinfo;
    // block the code and loop until we successfully get a time sync from the internet
    while (!getLocalTime(&timeinfo)) {
        Serial.println("Waiting for NTP...");
        delay(500);
    }

    Serial.println("Time synchronised");
    // print out the time we just got to confirm it works
    Serial.print("Current time: ");
    Serial.println(&timeinfo, "%H:%M:%S");

    // FIX: don't force a fixed channel here. This board is already
    // connected to the router on its real channel (see WiFi.begin()
    // above) - both boards being on the same router already puts
    // them on the same channel. Forcing this to 6 was overriding
    // that with a guess, which is what caused the sender's peer
    // channel (also previously hardcoded) to disagree with reality.

    // initialize the esp now protocol
    if (esp_now_init() != ESP_OK) {
        Serial.println("ESP-NOW initialization failed");
        return; // stop execution if radio fails
    }

    // link our custom callback function so it runs when a packet arrives
    esp_now_register_recv_cb(recievercallback);

    // visual separator for the serial monitor to show setup is completely finished
    Serial.println();
    Serial.println("================================");
    Serial.println("RECEIVER READY");
    Serial.println("================================");
}


void loop() {
    // check if the interrupt callback flagged that a new packet arrived
    if (recieved) {
        Serial.println();
        Serial.println("NEW CALENDAR DATA RECEIVED");

        // parse the raw text buffer into the actual json document object
        DeserializationError error = deserializeJson(calendarDocument, buffer);

        // if the parsing fails (like bad quotes or corrupt data), catch it here
        if (error) {
            Serial.print("JSON DESERIALIZATION FAILED: ");
            Serial.println(error.c_str());
            recieved = false; // reset the flag so we dont get stuck in a loop
            return; // exit this loop iteration early
        }

        Serial.println("JSON DESERIALIZATION SUCCESS");
        recieved = false; // reset the flag since we successfully stored the new data
    }

    // non blocking timer to check the time every 1000 milliseconds
    if (millis() - lastTimeCheck >= TIME_CHECK_INTERVAL) {
        lastTimeCheck = millis(); // update the timer

        // call the function to figure out what we should be doing right now
        int currentActivityIndex = findCurrentActivity();

        // only redraw the screen if the activity actually changed to stop flickering
        if (currentActivityIndex != displayedActivityIndex) {
            if (currentActivityIndex != -1) {
                // if it isnt -1, it means a real activity is happening
                JsonArray activities = calendarDocument.as<JsonArray>();
                JsonObject currentActivity = activities[currentActivityIndex];
                // pass that specific object to the display function
                displayActivity(currentActivity);
            } else {
                // Transitioning to No Activity: start a brand new
                // Game of Life pattern next time we go idle.
                gameOfLifeInitialized = false; // reset the game flag
                tft.fillScreen(0x0000);        // clear the screen to black
            }
            // update the state tracker so we know what is currently on the screen
            displayedActivityIndex = currentActivityIndex;
        }
    }

    // Kept outside the 1000ms timer block so the animation steps
    // on its own faster interval (LIFE_FRAME_DELAY) rather than
    // only updating once a second.
    if (displayedActivityIndex == -1) {
        // if the calendar is empty, run the animation
        drawGameOfLife();
    }
}