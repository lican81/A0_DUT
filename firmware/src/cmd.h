/* 
 * File:   cmd.h
 * Author: canli
 *
 * Created on July 15, 2019, 4:24 PM
 */

#ifndef CMD_H
#define	CMD_H


#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include "system_config.h"
#include "system_definitions.h"


#ifdef	__cplusplus
extern "C" {
#endif

typedef enum
{
	/* Application's state machine's initial state. */
	CMD_STATE_INIT=0,
	CMD_STATE_SERVICE_TASKS,
    CMD_STATE_PARSE,     
    CMD_STATE_ADC,
    CMD_STATE_SPI,
    CMD_STATE_USB_WRITE
	/* TODO: Define states used by the application state machine. */

} CMD_STATES;

typedef struct
{
    /* The application's current state */
    CMD_STATES state;

    /* TODO: Define any additional data used by the application. */
    char *usb_buf_rx;
    char cmd[512];
} CMD_DATA;

void CMD_Tasks( void );


#ifdef	__cplusplus
}
#endif

#endif	/* CMD_H */

