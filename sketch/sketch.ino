// Définition de la broche
const int RELAY_PIN = 2; // Ton relais est sur la broche D2
const int TASER_PIN = 6;

void setup() {
  // On configure la broche D2 comme une sortie
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(TASER_PIN, OUTPUT);
  
  // Initialisation : On démarre le moniteur série pour suivre ce qui se passe
  Serial.begin(9600);
  Serial.println("Test du relais démarré");
}

void loop() {
  // -- ACTION : ON --
  Serial.println("Relais activé (ON)");
  digitalWrite(RELAY_PIN, HIGH); // Envoie 5V sur D2 pour coller le relais
  digitalWrite(TASER_PIN, HIGH); // Envoie 5V sur D2 pour coller le relais
  delay(2000); // Attendre 2 secondes

  // -- ACTION : OFF --
  Serial.println("Relais désactivé (OFF)");
  digitalWrite(RELAY_PIN, LOW);  // Coupe le signal sur D2
  digitalWrite(TASER_PIN, LOW); // Coupe le signal sur D2
  delay(2000); // Attendre 2 secondes
}