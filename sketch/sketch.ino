#include <Arduino_LED_Matrix.h>

ArduinoLEDMatrix matrix;

// Bitmaps for Tick (V) and Cross (X)
// 8 rows, 13 columns (Uno R4 WiFi Matrix size)
// Bitmaps for Tick (V) and Cross (X)
// 8 rows, 13 columns (Uno R4 WiFi Matrix size)
uint8_t tick_frame[8][13] = {
  {0,0,0,0,0,0,0,0,0,0,1,0,0},
  {0,0,0,0,0,0,0,0,0,1,0,0,0},
  {0,0,0,0,0,0,0,0,1,0,0,0,0},
  {0,1,0,0,0,0,0,1,0,0,0,0,0},
  {0,0,1,0,0,0,1,0,0,0,0,0,0},
  {0,0,0,1,0,1,0,0,0,0,0,0,0},
  {0,0,0,0,1,0,0,0,0,0,0,0,0},
  {0,0,0,0,0,0,0,0,0,0,0,0,0}
};

uint8_t cross_frame[8][13] = {
  {0,0,1,0,0,0,0,0,0,1,0,0,0},
  {0,0,0,0,1,0,0,0,0,1,0,0,0},
  {0,0,0,0,0,1,0,1,0,0,0,0,0},
  {0,0,0,0,0,0,1,0,0,0,0,0,0},
  {0,0,0,0,0,1,0,1,0,0,0,0,0},
  {0,0,0,0,1,0,0,0,1,0,0,0,0},
  {0,0,0,1,0,0,0,0,0,1,0,0,0},
  {0,0,1,0,0,0,0,0,0,0,1,0,0}
};

void setup() {
  Serial.begin(9600);
  matrix.begin();
  
  // Start with a neutral or Cross pattern
  matrix.renderBitmap(cross_frame, 8, 13);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // '1' for Tick (Validé), '0' for Cross (Pas validé)
    if (command == '1') {
      matrix.renderBitmap(tick_frame, 8, 13);
    } else if (command == '0') {
      matrix.renderBitmap(cross_frame, 8, 13);
    }
  }
}
