#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP32Servo.h>
#include <Adafruit_NeoPixel.h>

// ================= LCD =================
#define SDA_PIN 8
#define SCL_PIN 9
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ================= CẢM BIẾN TẦNG =================
#define SENSOR_T1 4   // Tầng trệt
#define SENSOR_T2 5   // Tầng 1
#define SENSOR_T3 6   // Tầng 2

// ================= SERVO & BARRIER =================
Servo servoIn;
Servo servoOut;
#define SENSOR_IN 1
#define SENSOR_OUT 2
#define SERVO_IN_PIN 10
#define SERVO_OUT_PIN 11

// ================= MOTOR & ENCODER (THANG MÁY) =================
#define ENCA 14
#define ENCB 15
#define IN1 12
#define IN2 13

// ================= CẢM BIẾN THANG =================
#define SENSOR_ELEVATOR 7

// ================= LED & LDR =================
#define LED_PIN_1 18
#define LED_PIN_2 19
#define LED_COUNT_1 13
#define LED_COUNT_2 12
#define LDR_PIN    17
Adafruit_NeoPixel strip1(LED_COUNT_1, LED_PIN_1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2(LED_COUNT_2, LED_PIN_2, NEO_GRB + NEO_KHZ800);
int threshold = 2500;

// ================= MÁI CHE (RAIN SENSOR + MOTOR) =================
#define AIN1 36
#define AIN2 37
#define BIN1 38
#define BIN2 39
#define RAIN_SENSOR 42
bool isClosed = false;

// ================= FLAME SENSOR + BUZZER =================
#define FIRE_SENSOR_PIN 16
#define BUZZER_PIN 21

// ================= BIẾN TOÀN CỤC =================
volatile long encoderCount = 0;
long targetCount = 0;
bool isMoving = false;
int currentFloor = 0;
bool reached = false;

// ================= MANUAL CONTROL VARIABLES =================
#define AUTO 0
#define MANUAL 1
int operationMode = AUTO;  // Default to automatic mode

// Manual control states
bool manualBarrierInOpen = false;
bool manualBarrierOutOpen = false;
int manualElevatorTarget = -1;  // -1 means no manual command
bool manualLEDOn = false;
bool manualRainShelterOpen = false;

// ================= LED NON-BLOCKING =================
uint16_t ledIndex = 0;
unsigned long lastLEDTime = 0;
unsigned long ledInterval = 20; // 20ms mỗi bước rainbow

// ================= SERIAL COMMAND PROCESSING =================
void processSerialCommand() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    Serial.print("Received command: ");
    Serial.println(command);
    
    // Mode switching
    if (command == "MODE_AUTO") {
      operationMode = AUTO;
      Serial.println(">>> Switched to AUTO mode");
    }
    else if (command == "MODE_MANUAL") {
      operationMode = MANUAL;
      Serial.println(">>> Switched to MANUAL mode");
    }
    
    // Barrier IN controls
    else if (command == "BARRIER_IN_OPEN") {
      manualBarrierInOpen = true;
      setBarrierIn(80);  // Open position
      Serial.println(">>> BARRIER IN: OPEN");
    }
    else if (command == "BARRIER_IN_CLOSE") {
      manualBarrierInOpen = false;
      setBarrierIn(180);  // Closed position
      Serial.println(">>> BARRIER IN: CLOSED");
    }
    
    // Barrier OUT controls
    else if (command == "BARRIER_OUT_OPEN") {
      manualBarrierOutOpen = true;
      setBarrierOut(80);  // Open position
      Serial.println(">>> BARRIER OUT: OPEN");
    }
    else if (command == "BARRIER_OUT_CLOSE") {
      manualBarrierOutOpen = false;
      setBarrierOut(180);  // Closed position
      Serial.println(">>> BARRIER OUT: CLOSED");
    }
    
    // Elevator controls
    else if (command == "ELEVATOR_FLOOR_0") {
      manualElevatorTarget = 0;
      Serial.println(">>> ELEVATOR: Moving to GROUND floor");
      if (!isMoving) moveToFloor(0);
    }
    else if (command == "ELEVATOR_FLOOR_1") {
      manualElevatorTarget = 1;
      Serial.println(">>> ELEVATOR: Moving to floor 1");
      if (!isMoving) moveToFloor(1);
    }
    else if (command == "ELEVATOR_FLOOR_2") {
      manualElevatorTarget = 2;
      Serial.println(">>> ELEVATOR: Moving to floor 2");
      if (!isMoving) moveToFloor(2);
    }
    
    // LED controls
    else if (command == "LED_ALL_ON") {
      manualLEDOn = true;
      setLEDsManual(true);
      Serial.println(">>> LEDs: ALL ON");
    }
    else if (command == "LED_ALL_OFF") {
      manualLEDOn = false;
      setLEDsManual(false);
      Serial.println(">>> LEDs: ALL OFF");
    }
    
    // Rain shelter controls
    else if (command == "RAIN_SHELTER_ON") {
      manualRainShelterOpen = false;  // ON means closed (shelter deployed)
      closeRoof();
      Serial.println(">>> RAIN SHELTER: CLOSED (deployed)");
    }
    else if (command == "RAIN_SHELTER_OFF") {
      manualRainShelterOpen = true;  // OFF means open (shelter retracted)
      openRoof();
      Serial.println(">>> RAIN SHELTER: OPEN (retracted)");
    }
    
    else {
      Serial.print(">>> Unknown command: ");
      Serial.println(command);
    }
  }
}

// ================= KHỞI TẠO =================
void setup() {
  Serial.begin(115200);

  // LCD
  Wire.begin(SDA_PIN, SCL_PIN);
  lcd.init();
  lcd.backlight();

  // Cảm biến tầng
  pinMode(SENSOR_T1, INPUT_PULLUP);
  pinMode(SENSOR_T2, INPUT_PULLUP);
  pinMode(SENSOR_T3, INPUT_PULLUP);
  pinMode(SENSOR_ELEVATOR, INPUT_PULLUP);
  pinMode(SENSOR_IN, INPUT_PULLUP);
  pinMode(SENSOR_OUT, INPUT_PULLUP);

  // Motor thang máy
  pinMode(ENCA, INPUT_PULLUP);
  pinMode(ENCB, INPUT_PULLUP);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(ENCA), readEncoder, RISING);

  // Servo
  servoIn.attach(SERVO_IN_PIN);
  servoOut.attach(SERVO_OUT_PIN);
  servoIn.write(180);
  servoOut.write(180);

  // LED
  strip1.begin();
  strip2.begin();
  strip1.setBrightness(150);
  strip2.setBrightness(150);
  strip1.show();
  strip2.show();

  // Mái che
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(RAIN_SENSOR, INPUT);

  // Flame + Buzzer
  pinMode(FIRE_SENSOR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);   // Tắt buzzer ban đầu

  lcd.setCursor(0,0);
  lcd.print("WELCOME!!!");
  delay(2000);
  lcd.clear();

  Serial.println("=== He thong tong hop ESP32-S3 ===");
}

// ================= VÒNG LẶP CHÍNH =================
void loop() {
  // Process any incoming serial commands first
  processSerialCommand();
  
  // --- HỆ THỐNG THANG MÁY ---
  int t1 = digitalRead(SENSOR_T1);
  int t2 = digitalRead(SENSOR_T2);
  int t3 = digitalRead(SENSOR_T3);
  int elevator = digitalRead(SENSOR_ELEVATOR);
  int inSensor = digitalRead(SENSOR_IN);
  int outSensor = digitalRead(SENSOR_OUT);

  // Hiển thị chỗ trống trên LCD
  int emptySlots = (t1 == HIGH) + (t2 == HIGH) + (t3 == HIGH);
  lcd.setCursor(0, 0);
  if (operationMode == AUTO) {
    lcd.print("AUTO MODE    ");
  } else {
    lcd.print("MANUAL MODE  ");
  }
  lcd.setCursor(0, 1);
  lcd.print("Slots left: ");
  lcd.print(emptySlots);

  // === AUTO MODE: Automatic sensor-based control ===
  if (operationMode == AUTO) {
    // Mở barie vào
    if (inSensor == LOW) {
      servoIn.write(80);
      delay(1500);
      servoIn.write(180);
    }

    // Mở barie ra
    if (outSensor == LOW) {
      servoOut.write(80);
      delay(1500);
      servoOut.write(180);
    }

    // --- Có xe trong thang ---
    if (elevator == LOW && !isMoving) {
      delay(2000);
      if (emptySlots == 0) {
        Serial.println("FULL PARKING!");
      } else {
        if (t2 == HIGH) moveToFloor(1);
        else if (t3 == HIGH) moveToFloor(2);
        else if (t1 == HIGH) Serial.println("Park at GROUND");
      }
    }

    // --- LED theo ánh sáng môi trường ---
    int lightValue = analogRead(LDR_PIN);
    if (lightValue > threshold) {
      updateRainbowNonBlocking();
    } else {
      clearLEDs();
    }

    // --- MÁI CHE TỰ ĐỘNG ---
    handleRainSensor();
  }
  
  // === MANUAL MODE: Manual states are maintained ===
  else if (operationMode == MANUAL) {
    // Barriers remain in their manual state (no automatic changes)
    // LEDs remain in their manual state
    if (manualLEDOn) {
      // Keep LEDs on (already set by command)
    }
    // Rain shelter remains in manual state (no automatic changes)
    // Elevator can be manually controlled via commands
  }

  // --- FLAME SENSOR + BUZZER (always active in both modes) ---
  int fireRead = digitalRead(FIRE_SENSOR_PIN);
  bool fireDetected = (fireRead == LOW); // LOW = có lửa
  if (fireDetected) {
    digitalWrite(BUZZER_PIN, HIGH);
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }

  // --- SENSOR DATA OUTPUT (reduced frequency) ---
  if (millis() % 500 < 50){
    Serial.print("F1: ");
    Serial.print(t1);
    Serial.print(", F2: ");
    Serial.print(t2);
    Serial.print(", F3: ");
    Serial.print(t3);
    Serial.print(", In: ");
    Serial.print(inSensor == 0 ? 1 : 0);
    Serial.print(", Out: ");
    Serial.print(outSensor == 0 ? 1 : 0);
    Serial.print(", LDR: ");
    int lightValue = analogRead(LDR_PIN);
    Serial.print(lightValue);
    int rain = digitalRead(RAIN_SENSOR);
    Serial.print(", Rain: ");
    Serial.print(rain == 0 ? 1 : 0);
    Serial.print(", Fire: ");
    Serial.println(fireDetected);
    
  }

}

// ================= MOTOR THANG MÁY =================
void moveToFloor(int floor) {
  isMoving = true;
  currentFloor = floor;
  reached = false;

  if (floor == 1) targetCount = -1290;
  else if (floor == 2) targetCount = -2500;
  else targetCount = 0;

  if (floor != 0) {
    while (!reached) {
      long error = targetCount - encoderCount;
      if (abs(error) > 0) { 
        if (error > 0) digitalWrite(IN1,HIGH), digitalWrite(IN2,LOW);
        else digitalWrite(IN1,LOW), digitalWrite(IN2,HIGH);
      } else {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,LOW);
        reached = true;
        Serial.print("✅ Reached floor "); Serial.println(floor);
        delay(500);
      }
    }

    // Quay về tầng GROUND
    targetCount = 0;
    reached = false;
    while (!reached) {
      if (digitalRead(SENSOR_T1) == LOW) {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,LOW);
        reached = true;
        encoderCount = 0;
        Serial.println("✅ Back to GROUND (Sensor triggered)");
        delay(500);
        break;
      }

      long error = targetCount - encoderCount;
      if (abs(error) > 0) {
        if (error > 0) digitalWrite(IN1,HIGH), digitalWrite(IN2,LOW);
        else digitalWrite(IN1,LOW), digitalWrite(IN2,HIGH);
      } else {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,LOW);
        reached = true;
        encoderCount = 0;
        Serial.println("✅ Back to GROUND (Encoder reached 0)");
        delay(500);
      }
    }
  } else {
    reached = false;
    while (!reached) {
      if (digitalRead(SENSOR_T1) == LOW) {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,LOW);
        reached = true;
        encoderCount = 0;
        Serial.println("✅ Reached GROUND");
        delay(500);
        break;
      } else {
        digitalWrite(IN1,LOW);
        digitalWrite(IN2,HIGH);
      }
    }
  }

  isMoving = false;
}

// ================= ENCODER ISR =================
void readEncoder() {
  int b = digitalRead(ENCB);
  if (b > 0) encoderCount = encoderCount - 1;
  else encoderCount = encoderCount + 1;
}

// ================= LED NON-BLOCKING =================
void updateRainbowNonBlocking() {
  unsigned long currentMillis = millis();
  if (currentMillis - lastLEDTime >= ledInterval) {
    for (uint16_t i = 0; i < strip1.numPixels(); i++) {
      uint8_t pos = ((i * 256 / strip1.numPixels()) + ledIndex) & 255;
      strip1.setPixelColor(i, Wheel(pos));
    }
    for (uint16_t i = 0; i < strip2.numPixels(); i++) {
      uint8_t pos = ((i * 256 / strip2.numPixels()) + ledIndex) & 255;
      strip2.setPixelColor(i, Wheel(pos));
    }
    strip1.show();
    strip2.show();
    ledIndex = (ledIndex + 1) % 256;
    lastLEDTime = currentMillis;
  }
}

uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) return strip1.Color(255 - WheelPos * 3, 0, WheelPos * 3);
  else if (WheelPos < 170) {
    WheelPos -= 85;
    return strip1.Color(0, WheelPos * 3, 255 - WheelPos * 3);
  } else {
    WheelPos -= 170;
    return strip1.Color(WheelPos * 3, 255 - WheelPos * 3, 0);
  }
}

void clearLEDs() {
  for (int i = 0; i < LED_COUNT_1; i++) strip1.setPixelColor(i, 0);
  for (int i = 0; i < LED_COUNT_2; i++) strip2.setPixelColor(i, 0);
  strip1.show();
  strip2.show();
}

// ================= MÁI CHE =================
void handleRainSensor() {
  int rain = digitalRead(RAIN_SENSOR);

  if (rain == 0 && !isClosed) {
    // Serial.println("Phat hien mua → DONG MAI CHE...");
    closeRoof();
    isClosed = true;
  } else if (rain == 1 && isClosed) {
    // Serial.println("Het mua → MO MAI CHE...");
    openRoof();
    isClosed = false;
  }
}

void openRoof() {
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, HIGH);
  digitalWrite(BIN2, LOW);
  delay(7500);
  stopMotors();
  Serial.println(">>> Mai che DA MO HOAN TOAN!");
}

void closeRoof() {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, HIGH);
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, HIGH);
  delay(7500);
  stopMotors();
  Serial.println(">>> Mai che DA DONG HOAN TOAN!");
}

void stopMotors() {
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);
}

// ================= MANUAL CONTROL HELPER FUNCTIONS =================
void setBarrierIn(int angle) {
  servoIn.write(angle);
}

void setBarrierOut(int angle) {
  servoOut.write(angle);
}

void setLEDsManual(bool on) {
  if (on) {
    // Turn all LEDs to white
    for (int i = 0; i < LED_COUNT_1; i++) {
      strip1.setPixelColor(i, strip1.Color(255, 255, 255));
    }
    for (int i = 0; i < LED_COUNT_2; i++) {
      strip2.setPixelColor(i, strip2.Color(255, 255, 255));
    }
    strip1.show();
    strip2.show();
  } else {
    clearLEDs();
  }
}