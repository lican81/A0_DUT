#include "usb_com.h"

USB_COM_DATA usb_comData;
/* Static buffers, suitable for DMA transfer */
#define USB_COM_MAKE_BUFFER_DMA_READY  __attribute__((coherent)) __attribute__((aligned(16)))

static uint8_t USB_COM_MAKE_BUFFER_DMA_READY writeBuffer[USB_COM_USB_CDC_COM_PORT_SINGLE_WRITE_BUFFER_SIZE];
static uint8_t USB_COM_MAKE_BUFFER_DMA_READY readBuffer [USB_COM_USB_CDC_COM_PORT_SINGLE_READ_BUFFER_SIZE];

// *****************************************************************************
// *****************************************************************************
// Section: Application Callback Functions
// *****************************************************************************
// *****************************************************************************


/*******************************************************
 * USB CDC Device Events - Application Event Handler
 *******************************************************/

USB_DEVICE_CDC_EVENT_RESPONSE USB_COM_USBDeviceCDCEventHandler
(
    USB_DEVICE_CDC_INDEX index ,
    USB_DEVICE_CDC_EVENT event ,
    void * pData,
    uintptr_t userData
)
{
    USB_COM_DATA * appDataObject;
    appDataObject = (USB_COM_DATA *)userData;
    USB_CDC_CONTROL_LINE_STATE * controlLineStateData;

    switch ( event )
    {
        case USB_DEVICE_CDC_EVENT_GET_LINE_CODING:

            /* This means the host wants to know the current line
             * coding. This is a control transfer request. Use the
             * USB_DEVICE_ControlSend() function to send the data to
             * host.  */

            USB_DEVICE_ControlSend(appDataObject->deviceHandle,
                    &appDataObject->getLineCodingData, sizeof(USB_CDC_LINE_CODING));

            break;

        case USB_DEVICE_CDC_EVENT_SET_LINE_CODING:

            /* This means the host wants to set the line coding.
             * This is a control transfer request. Use the
             * USB_DEVICE_ControlReceive() function to receive the
             * data from the host */

            USB_DEVICE_ControlReceive(appDataObject->deviceHandle,
                    &appDataObject->setLineCodingData, sizeof(USB_CDC_LINE_CODING));

            break;

        case USB_DEVICE_CDC_EVENT_SET_CONTROL_LINE_STATE:

            /* This means the host is setting the control line state.
             * Read the control line state. We will accept this request
             * for now. */

            controlLineStateData = (USB_CDC_CONTROL_LINE_STATE *)pData;
            appDataObject->controlLineStateData.dtr = controlLineStateData->dtr;
            appDataObject->controlLineStateData.carrier = controlLineStateData->carrier;

            USB_DEVICE_ControlStatus(appDataObject->deviceHandle, USB_DEVICE_CONTROL_STATUS_OK);

            break;

        case USB_DEVICE_CDC_EVENT_SEND_BREAK:

            /* This means that the host is requesting that a break of the
             * specified duration be sent.  */
            break;

        case USB_DEVICE_CDC_EVENT_READ_COMPLETE:
            /* This means that the host has sent some data*/
            appDataObject->readTransferHandle = USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID;
            
//            memcpy(writeBuffer, readBuffer, strlen(readBuffer));
//            appDataObject->writeLen = strlen(readBuffer);
            
//			readString[appDataObject->readProcessedLen] = readBuffer[0];
//			if (appDataObject->readProcessedLen < 8)
//			{
//            	appDataObject->readProcessedLen++;
//			}
            break;

        case USB_DEVICE_CDC_EVENT_CONTROL_TRANSFER_DATA_RECEIVED:

            /* The data stage of the last control transfer is
             * complete. For now we accept all the data */

            USB_DEVICE_ControlStatus(appDataObject->deviceHandle, USB_DEVICE_CONTROL_STATUS_OK);
            break;

        case USB_DEVICE_CDC_EVENT_CONTROL_TRANSFER_DATA_SENT:

            /* This means the GET LINE CODING function data is valid. We dont
             * do much with this data in this demo. */
            break;

        case USB_DEVICE_CDC_EVENT_WRITE_COMPLETE:

            /* This means that the host has sent some data*/
//            SYS_MESSAGE("Data sent\r\n");
            appDataObject->writeLen = 0;
            
            appDataObject->writeTransferHandle = USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID;
            break;

        default:
            break;
    }

    return USB_DEVICE_CDC_EVENT_RESPONSE_NONE;
}

/***********************************************
 * Application USB Device Layer Event Handler.
 ***********************************************/
void USB_COM_USBDeviceEventHandler ( USB_DEVICE_EVENT event, void * eventData, uintptr_t context )
{
    USB_DEVICE_EVENT_DATA_CONFIGURED *configuredEventData;

    switch ( event )
    {
        case USB_DEVICE_EVENT_SOF:
            break;

        case USB_DEVICE_EVENT_RESET:

            usb_comData.isConfigured = false;

            break;

        case USB_DEVICE_EVENT_CONFIGURED:

            /* Check the configuration. We only support configuration 1 */
            configuredEventData = (USB_DEVICE_EVENT_DATA_CONFIGURED*)eventData;
            if ( configuredEventData->configurationValue == 1)
            {
                /* Register the CDC Device application event handler here.
                 * Note how the usb_comData object pointer is passed as the
                 * user data */

                USB_DEVICE_CDC_EventHandlerSet(USB_DEVICE_CDC_INDEX_0, USB_COM_USBDeviceCDCEventHandler, (uintptr_t)&usb_comData);

                /* Mark that the device is now configured */
                usb_comData.isConfigured = true;

            }
            break;

        case USB_DEVICE_EVENT_POWER_DETECTED:

            /* VBUS was detected. We can attach the device */
            USB_DEVICE_Attach(usb_comData.deviceHandle);
            break;

        case USB_DEVICE_EVENT_POWER_REMOVED:

            /* VBUS is not available any more. Detach the device. */
            USB_DEVICE_Detach(usb_comData.deviceHandle);
            break;

        case USB_DEVICE_EVENT_SUSPENDED:
            break;

        case USB_DEVICE_EVENT_RESUMED:
        case USB_DEVICE_EVENT_ERROR:
        default:
            break;
    }
}

/* TODO:  Add any necessary callback functions.
*/

// *****************************************************************************
// *****************************************************************************
// Section: Application Local Functions
// *****************************************************************************
// *****************************************************************************

/******************************************************************************
  Function:
    static void USB_TX_Task (void)
    
   Remarks:
    Feeds the USB write function. 
*/
static void USB_TX_Task (void)
{
    if(!usb_comData.isConfigured)
    {
        usb_comData.writeTransferHandle = USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID;
    }
    else
    {
        /* Schedule a write if data is pending 
         */
        if ((usb_comData.writeLen > 0) && (usb_comData.writeTransferHandle == USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID))
        {
//            SYS_PRINT("Sending data (len=%d) back to the host\r\n", usb_comData.writeLen);
            USB_DEVICE_CDC_Write(USB_DEVICE_CDC_INDEX_0,
                                 &usb_comData.writeTransferHandle,
                                 writeBuffer, 
                                 usb_comData.writeLen,
                                 USB_DEVICE_CDC_TRANSFER_FLAGS_DATA_COMPLETE);
        }
    }
}

/******************************************************************************
  Function:
    static void USB_RX_Task (void)
    
   Remarks:
    Reads from the USB. 
*/
static void USB_RX_Task(void)
{
    if(!usb_comData.isConfigured)
    {
        usb_comData.readTransferHandle  = USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID;
//        usb_comData.readProcessedLen    = 0;
    }
    else
    {
        /* Schedule a read if none is pending and all previously read data
           has been processed
         */
        if( (usb_comData.readTransferHandle  == USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID))
        {
            SYS_MESSAGE("Requesting data from the host\r\n");
            USB_DEVICE_CDC_Read (USB_DEVICE_CDC_INDEX_0,
                                 &usb_comData.readTransferHandle, 
                                 readBuffer,
                                 USB_COM_USB_CDC_COM_PORT_SINGLE_READ_BUFFER_SIZE);
        };
    }
}

/* TODO:  Add any necessary local functions.
*/
int USB_Read( char **buf ) {
    if ( USB_Read_isBusy()  || !usb_comData.isConfigured ) {
        // Reading in process or data has not been processed
        return -1;
    } else {
        USB_RX_Task();
        *buf = readBuffer;
        
        return USB_COM_USB_CDC_COM_PORT_SINGLE_READ_BUFFER_SIZE;
    }
}

bool USB_Read_isBusy( void ) {
    return (usb_comData.readTransferHandle  != USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID) ||
            (usb_comData.state != USB_COM_STATE_SERVICE_TASKS);
}

int USB_Write( const char *buf, size_t count) {
    if (USB_Write_isBusy() || !usb_comData.isConfigured ) {
        // Reading in process or data has not been processed
        return -1;
    } else {
        memcpy(writeBuffer, buf, count);
        usb_comData.writeLen = count;

        USB_TX_Task();
        
        return USB_COM_USB_CDC_COM_PORT_SINGLE_WRITE_BUFFER_SIZE;
    }
}

bool USB_Write_isBusy( void ) {
    return (usb_comData.writeTransferHandle != USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID) ||
            (usb_comData.state != USB_COM_STATE_SERVICE_TASKS);
}


// *****************************************************************************
// *****************************************************************************
// Section: Application Initialization and State Machine Functions
// *****************************************************************************
// *****************************************************************************

/*******************************************************************************
  Function:
    void USB_COM_Initialize ( void )

  Remarks:
    See prototype in usb_com.h.
 */

void USB_COM_Initialize ( void )
{
    /* Place the App state machine in its initial state. */
    usb_comData.state = USB_COM_STATE_INIT;


    /* Device Layer Handle  */
    usb_comData.deviceHandle = USB_DEVICE_HANDLE_INVALID ;

    /* Device configured status */
    usb_comData.isConfigured = false;

    /* Initial get line coding state */
    usb_comData.getLineCodingData.dwDTERate   = 9600;
    usb_comData.getLineCodingData.bParityType =  0;
    usb_comData.getLineCodingData.bParityType = 0;
    usb_comData.getLineCodingData.bDataBits   = 8;

    /* Read Transfer Handle */
    usb_comData.readTransferHandle = USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID;

    /* Intialize the read data */
//    usb_comData.readProcessedLen = 0;

    /* Write Transfer Handle */
    usb_comData.writeTransferHandle = USB_DEVICE_CDC_TRANSFER_HANDLE_INVALID;
    

    
//    usb_comData.writeLen = sizeof(writeString);
//	memcpy(writeBuffer, writeString, usb_comData.writeLen);
    
    /* TODO: Initialize your application's state machine and other
     * parameters.
     */
}


/******************************************************************************
  Function:
    void USB_COM_Tasks ( void )

  Remarks:
    See prototype in usb_com.h.
 */

void USB_COM_Tasks ( void )
{

    /* Check the application's current state. */
    switch ( usb_comData.state )
    {
        /* Application's initial state. */
        case USB_COM_STATE_INIT:
        {
            bool appInitialized = true;
      
            /* Open the device layer */
            if (usb_comData.deviceHandle == USB_DEVICE_HANDLE_INVALID)
            {
                usb_comData.deviceHandle = USB_DEVICE_Open( USB_DEVICE_INDEX_0,
                                               DRV_IO_INTENT_READWRITE );
                appInitialized &= ( USB_DEVICE_HANDLE_INVALID != usb_comData.deviceHandle );
            }
        
            if (appInitialized)
            {

                /* Register a callback with device layer to get event notification (for end point 0) */
                USB_DEVICE_EventHandlerSet(usb_comData.deviceHandle,
                                           USB_COM_USBDeviceEventHandler, 0);
            
                usb_comData.state = USB_COM_STATE_SERVICE_TASKS;
                
                /*Initialize the write data */
                usb_comData.writeLen = 0;
            }
            break;
        }

        case USB_COM_STATE_SERVICE_TASKS:
        {
//            USB_RX_Task();
//            USB_TX_Task();
        
            break;
        }

        /* TODO: implement your application state machine.*/
        

        /* The default state should never be executed. */
        default:
        {
            /* TODO: Handle error in application's state machine. */
            break;
        }
    }
}

 

/*******************************************************************************
 End of File
 */
