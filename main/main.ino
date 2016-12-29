/***
 *       Filename:  main.ino
 *
 *    Description:  Anamika Protocol for EyeBlinkConditioning.
 *
 *        Version:  0.0.1
 *        Created:  2016-09-29

 *       Revision:  none
 *
 *         Author:  Dilawar Singh <dilawars@ncbs.res.in>
 *   Organization:  NCBS Bangalore
 *
 *        License:  GNU GPL2
 */

#include <avr/wdt.h>
#include <SD.h>

// Pins etc.
#define         TOTAL_SENSOR_PINS           9
#define         LED_PIN_SDWRITE             A14
#define         LED_PIN_SENSOR              A15
int sensor_pins_[TOTAL_SENSOR_PINS] = { A0, A1, A2, A3, A4, A5, A6, A7, A8 };

int values_[ TOTAL_SENSOR_PINS ] = {};
int state_[ TOTAL_SENSOR_PINS ] = { };
long count_crossing_ = 0;
int values_sum_ = 0;

bool reboot_ = false;

unsigned long stamp_ = 0;
unsigned dt_ = 2;
unsigned write_dt_ = 2;
char msg_[40];

unsigned long trial_start_time_ = 0;
unsigned long trial_end_time_ = 0;

unsigned long currentTime( )
{
    return millis() - trial_start_time_;
}

// SD card related. 
// Filename must not be longer than 8.3. 
String prefix_ = "data";
String outfile_ = "data0.txt";

/*-----------------------------------------------------------------------------
 *  WATCH DOG
 *-----------------------------------------------------------------------------*/
/**
 * @brief Interrupt serviving routine.
 *
 * @param _vect
 */
ISR(WDT_vect)
{
    // Handle interuppts here.
    // Nothing to handle.
}

void reset_watchdog( )
{
    if( not reboot_ )
        wdt_reset( );
}


/**
 * @brief Write data line to Serial port.
 *   NOTE: Use python dictionary format. It can't be written at baud rate of
 *   38400 at least.
 * @param data
 * @param timestamp
 */
void write_data_line( )
{
    analogWrite( LED_PIN_SDWRITE, 0 );

    reset_watchdog( );
    char msg[40];
    char *pos = msg;
    unsigned long timestamp = millis() - trial_start_time_;
    pos += sprintf( pos, "%lu,", timestamp);

    int nLow = 0;
    for (size_t i = 0; i < TOTAL_SENSOR_PINS; i++) 
    {
        int data = analogRead( sensor_pins_[i] );
        if( data < 5 )
            nLow += 1;
        values_[ i ] = data;
        delay( 5 );
        pos += sprintf( pos, "%d,", data );
    }

    analogWrite( LED_PIN_SENSOR, 200 * nLow );

    // Write to SD card.
    File dataFile = SD.open( outfile_, FILE_WRITE );
    if( dataFile )
    {
        analogWrite( LED_PIN_SDWRITE, 255 );
        dataFile.println( msg );
        dataFile.close( );
    }
    else
        Serial.println( "Could not write to SD card" );

#if 0
    Serial.println(msg);
    Serial.flush( );
#endif
}


// Setup board.
void setup()
{
    Serial.begin( 38400 );

    // setup watchdog. If not reset in 2 seconds, it reboots the system.
    wdt_enable( WDTO_2S );
    wdt_reset();
    stamp_ = 0;

    for (size_t i = 0; i < TOTAL_SENSOR_PINS; i++) 
    {
        pinMode( sensor_pins_[i], INPUT );
        values_[ i ] = 0;
        state_[ i ] = 0;
    }

    pinMode( LED_PIN_SENSOR, OUTPUT );
    pinMode( LED_PIN_SDWRITE, OUTPUT );

    
    /*-----------------------------------------------------------------------------
     *  Setup SD card interface. Following configuration is from 
     *  http://MOSIw.bajdi.com/arduino-mega-2560-and-sd-card-modul/
     *  MOSI : 51
     *  MISO : 50
     *  CLK  : 52
     *  CS   : 53
     *-----------------------------------------------------------------------------*/
    Serial.println( "Initializing SD card" );
    pinMode( 53, OUTPUT );
    if( ! SD.begin( 53 ) )
    {
        while( true )
            Serial.println( "Card failed, or not present. " );
    }
    else
        Serial.println( "Card is initialized successfully " );

    // Get a filename
    for (size_t i = 0; i < 9999; i++) 
    {
        String filename = prefix_ + String( i ) + ".txt";
        if(SD.exists( filename ))
            Serial.println( "File " + filename + " exists " );
        else
        {
            outfile_ = filename;
            break;
        }
    }
    Serial.println( "Data will be written to " + outfile_ );
    delay( 200 );
}


void loop()
{
    reset_watchdog( );
    write_data_line( );
}
