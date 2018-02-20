int relay = 13;
char data = 0;
void setup() {
    Serial.begin(9600);
    pinMode(relay, OUTPUT);
}
void loop() {
    if(Serial.available() > 0)
    {
        data = Serial.read();
        Serial.print(data);
        Serial.print("\n");
        if(data == '1')
            digitalWrite(relay, HIGH);
        else if(data === '0')
            digitalWrite(relay, LOW);
    }
}
