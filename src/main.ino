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

#define         DRY_RUN                     1
// Pins etc.
#define         SENSOR_PIN                  A0

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
    reset_watchdog( );
    int data = analogRead( SENSOR_PIN );
    unsigned long timestamp = millis() - trial_start_time_;
    
    sprintf(msg_  , "%lu,%d" , timestamp, data);
    Serial.println(msg_);
    Serial.flush( );
    delay( 50 );
}


void setup()
{
    Serial.begin( 38400 );

    // setup watchdog. If not reset in 2 seconds, it reboots the system.
    wdt_enable( WDTO_2S );
    wdt_reset();
    stamp_ = 0;

    pinMode( SENSOR_PIN, INPUT );
}


void loop()
{
    reset_watchdog( );
    write_data_line( );
}
