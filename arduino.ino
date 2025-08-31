#include <Servo.h>
Servo myservo;

int trigPin = 7;
int echoPin = 6;
int ledPin = 8;
int touchPin = 5;
int touchLed = 4;
int buzzer = 10;

int distance_threshold = 30;
float duration_us, distance_cm;
bool touchHandled = false;

void setup()
{
    Serial.begin(9600);
    pinMode(trigPin, OUTPUT);
    pinMode(echoPin, INPUT);
    pinMode(ledPin, OUTPUT);
    pinMode(touchPin, INPUT);
    pinMode(touchLed, OUTPUT);
    pinMode(buzzer, OUTPUT);
    myservo.attach(9);
}

void loop()
{
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    int touchState = digitalRead(touchPin);

    duration_us = pulseIn(echoPin, HIGH);

    distance_cm = 0.017 * duration_us;

    if (distance_cm < distance_threshold)
    {
        Serial.println("1");
        delay(5000);
    }
    else
    {
        Serial.println("0");
        delay(1500);
    }

    // Serial.print("Distance : ");
    // Serial.println(distance_cm);
    // delay(1000);

    if (Serial.available())
    {
        char command = Serial.read();
        if (command == 'S')
        {
            digitalWrite(ledPin, HIGH);
            delay(800);
            myservo.write(180);
            delay(2500);
            myservo.write(90);
            digitalWrite(ledPin, LOW);
        }
    }

    if (touchState == HIGH && !touchHandled)
    {
        Serial.println("0");
        Serial.println("2");
        digitalWrite(touchLed, HIGH);
        myservo.write(180);
        delay(2500);
        myservo.write(90);
        digitalWrite(touchLed, LOW);
    }
    if (touchState == LOW)
    {
        bool touchHandled = false;
    }
}