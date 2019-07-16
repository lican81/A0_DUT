/* 
 * File:   usb_com.h
 * Author: canli
 *
 * Created on July 15, 2019, 4:32 PM
 */

#ifndef USB_COM_H
#define	USB_COM_H


#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include "system_config.h"
#include "system_definitions.h"


#ifdef	__cplusplus
extern "C" {
#endif
    
#define USB_COM_USB_CDC_COM_PORT_SINGLE_READ_BUFFER_SIZE  512
#define USB_COM_USB_CDC_COM_PORT_SINGLE_WRITE_BUFFER_SIZE 512

typedef enum
{
	/* Application's state machine's initial state. */
	USB_COM_STATE_INIT=0,
	USB_COM_STATE_SERVICE_TASKS,

	/* TODO: Define states used by the application state machine. */

} USB_COM_STATES;


typedef struct
{
    /* The application's current state */
    USB_COM_STATES state;

    /* TODO: Define any additional data used by the application. */

    /* Device layer handle returned by device layer open function */
    USB_DEVICE_HANDLE deviceHandle;

    /* Set Line Coding Data */
    USB_CDC_LINE_CODING setLineCodingData;

    /* Device configured state */
    bool isConfigured;

    /* Get Line Coding Data */
    USB_CDC_LINE_CODING getLineCodingData;

    /* Control Line State */
    USB_CDC_CONTROL_LINE_STATE controlLineStateData;

    /* Read transfer handle */
    USB_DEVICE_CDC_TRANSFER_HANDLE readTransferHandle;

    /* Length of data read */
//    uint32_t readLen;
    
    /* Length of read data processed */
//    uint32_t readProcessedLen;

    /* Write transfer handle */
    USB_DEVICE_CDC_TRANSFER_HANDLE writeTransferHandle;
    
    /* Length of data to be written */
    uint32_t writeLen;
    

} USB_COM_DATA;


void USB_COM_Initialize ( void );

void USB_COM_Tasks( void );


bool USB_Read_isBusy( void );
bool USB_Write_isBusy( void );

int USB_Read( char **buf );
int USB_Write( const char *buf, size_t count);


#ifdef	__cplusplus
}
#endif

#endif	/* USB_COM_H */

