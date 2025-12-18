#include <Arduino_RouterBridge.h>

// Définition de la broche
const int RELAY_PIN = 2; // Ton relais est sur la broche D2
const int TASER_PIN = 6;

const int BUTTON_RELAY_PIN = 3;
const int BUTTON_TASER_PIN = 7;

void setup() {
  // On configure la broche D2 comme une sortie
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(TASER_PIN, OUTPUT);
  
  pinMode(BUTTON_RELAY_PIN, INPUT_PULLUP);
  pinMode(BUTTON_TASER_PIN, INPUT_PULLUP);
  
  // Initialisation : On démarre le moniteur série pour suivre ce qui se passe
  Serial.begin(9600);
  Serial.println("Test du relais démarré");

  Bridge.begin();
  Bridge.provide("trigger_relay", trigger_relay);
  Bridge.provide("trigger_taser", trigger_taser);
}

void loop() {
  delay(50); // Faster polling
  
  if (digitalRead(BUTTON_RELAY_PIN) == HIGH) {
     trigger_relay();
  }
  
  if (digitalRead(BUTTON_TASER_PIN) == HIGH) {
     trigger_taser();
  }
}

void trigger_relay() {
  Serial.println("cmd: trigger_relay received");
  Serial.println("Relais activé (ON)");
  digitalWrite(RELAY_PIN, HIGH); // Envoie 5V sur D2 pour coller le relais
  delay(1000); // Active pour 1 seconde
  digitalWrite(RELAY_PIN, LOW);
  Serial.println("Relais désactivé (OFF)");
}

void trigger_taser() {
  Serial.println("cmd: trigger_taser received");
  Serial.println("Taser activé (ON)");
  digitalWrite(TASER_PIN, HIGH); 
  delay(500); // Active pour 1 seconde
  digitalWrite(TASER_PIN, LOW);
  Serial.println("Taser désactivé (OFF)");
}