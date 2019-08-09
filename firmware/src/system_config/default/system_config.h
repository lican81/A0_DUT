/*******************************************************************************
  MPLAB Harmony System Configuration Header

  File Name:
    system_config.h

  Summary:
    Build-time configuration header for the system defined by this MPLAB Harmony
    project.

  Description:
    An MPLAB Project may have multiple configurations.  This file defines the
    build-time options for a single configuration.

  Remarks:
    This configuration header must not define any prototypes or data
    definitions (or include any files that do).  It only provides macro
    definitions for build-time configuration options that are not instantiated
    until used by another MPLAB Harmony module or application.

    Created with MPLAB Harmony Version 2.06
*******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
Copyright (c) 2013-2015 released Microchip Technology Inc.  All rights reserved.

Microchip licenses to you the right to use, modify, copy and distribute
Software only when embedded on a Microchip microcontroller or digital signal
controller that is integrated into your product or third party product
(pursuant to the sublicense terms in the accompanying license agreement).

You should refer to the license agreement accompanying this Software for
additional information regarding your rights and obligations.

SOFTWARE AND DOCUMENTATION ARE PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND,
EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION, ANY WARRANTY OF
MERCHANTABILITY, TITLE, NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
IN NO EVENT SHALL MICROCHIP OR ITS LICENSORS BE LIABLE OR OBLIGATED UNDER
CONTRACT, NEGLIGENCE, STRICT LIABILITY, CONTRIBUTION, BREACH OF WARRANTY, OR
OTHER LEGAL EQUITABLE THEORY ANY DIRECT OR INDIRECT DAMAGES OR EXPENSES
INCLUDING BUT NOT LIMITED TO ANY INCIDENTAL, SPECIAL, INDIRECT, PUNITIVE OR
CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA, COST OF PROCUREMENT OF
SUBSTITUTE GOODS, TECHNOLOGY, SERVICES, OR ANY CLAIMS BY THIRD PARTIES
(INCLUDING BUT NOT LIMITED TO ANY DEFENSE THEREOF), OR OTHER SIMILAR COSTS.
*******************************************************************************/
// DOM-IGNORE-END

#ifndef _SYSTEM_CONFIG_H
#define _SYSTEM_CONFIG_H

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************
/*  This section Includes other configuration headers necessary to completely
    define this configuration.
*/
#include "bsp.h"


// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

extern "C" {

#endif
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: System Service Configuration
// *****************************************************************************
// *****************************************************************************
// *****************************************************************************
/* Common System Service Configuration Options
*/
#define SYS_VERSION_STR           "2.06"
#define SYS_VERSION               20600

// *****************************************************************************
/* Clock System Service Configuration Options
*/
#define SYS_CLK_FREQ                        200000000ul
#define SYS_CLK_BUS_PERIPHERAL_1            100000000ul
#define SYS_CLK_BUS_PERIPHERAL_2            100000000ul
#define SYS_CLK_BUS_PERIPHERAL_3            100000000ul
#define SYS_CLK_BUS_PERIPHERAL_4            100000000ul
#define SYS_CLK_BUS_PERIPHERAL_5            100000000ul
#define SYS_CLK_BUS_PERIPHERAL_7            200000000ul
#define SYS_CLK_BUS_PERIPHERAL_8            100000000ul
#define SYS_CLK_BUS_REFERENCE_1             5000000ul
#define SYS_CLK_BUS_REFERENCE_3             5000000ul
#define SYS_CLK_CONFIG_PRIMARY_XTAL         24000000ul
#define SYS_CLK_CONFIG_SECONDARY_XTAL       32768ul
   
/*** Ports System Service Configuration ***/
#define SYS_PORT_A_ANSEL        0x3900
#define SYS_PORT_A_TRIS         0x39FF
#define SYS_PORT_A_LAT          0x0000
#define SYS_PORT_A_ODC          0x0000
#define SYS_PORT_A_CNPU         0x0000
#define SYS_PORT_A_CNPD         0x0000
#define SYS_PORT_A_CNEN         0x0000

#define SYS_PORT_B_ANSEL        0x015F
#define SYS_PORT_B_TRIS         0x605F
#define SYS_PORT_B_LAT          0x0000
#define SYS_PORT_B_ODC          0x0000
#define SYS_PORT_B_CNPU         0x7000
#define SYS_PORT_B_CNPD         0x0000
#define SYS_PORT_B_CNEN         0x0000

#define SYS_PORT_C_ANSEL        0x9FE1
#define SYS_PORT_C_TRIS         0x9FE1
#define SYS_PORT_C_LAT          0x0000
#define SYS_PORT_C_ODC          0x0000
#define SYS_PORT_C_CNPU         0x0000
#define SYS_PORT_C_CNPD         0x0000
#define SYS_PORT_C_CNEN         0x0000

#define SYS_PORT_D_ANSEL        0x0100
#define SYS_PORT_D_TRIS         0x093E
#define SYS_PORT_D_LAT          0x0000
#define SYS_PORT_D_ODC          0x0000
#define SYS_PORT_D_CNPU         0x0000
#define SYS_PORT_D_CNPD         0x0000
#define SYS_PORT_D_CNEN         0x0000

#define SYS_PORT_E_ANSEL        0xFC10
#define SYS_PORT_E_TRIS         0xFC38
#define SYS_PORT_E_LAT          0x0000
#define SYS_PORT_E_ODC          0x0000
#define SYS_PORT_E_CNPU         0x0000
#define SYS_PORT_E_CNPD         0x0000
#define SYS_PORT_E_CNEN         0x0000

#define SYS_PORT_F_ANSEL        0xCEC0
#define SYS_PORT_F_TRIS         0xCEC8
#define SYS_PORT_F_LAT          0x0000
#define SYS_PORT_F_ODC          0x0000
#define SYS_PORT_F_CNPU         0x0000
#define SYS_PORT_F_CNPD         0x0000
#define SYS_PORT_F_CNEN         0x0000

#define SYS_PORT_G_ANSEL        0x0C3C
#define SYS_PORT_G_TRIS         0xCC7E
#define SYS_PORT_G_LAT          0x0000
#define SYS_PORT_G_ODC          0x0000
#define SYS_PORT_G_CNPU         0x0000
#define SYS_PORT_G_CNPD         0x0000
#define SYS_PORT_G_CNEN         0x0000

#define SYS_PORT_H_ANSEL        0x0030
#define SYS_PORT_H_TRIS         0x6137
#define SYS_PORT_H_LAT          0x0000
#define SYS_PORT_H_ODC          0x0000
#define SYS_PORT_H_CNPU         0x0000
#define SYS_PORT_H_CNPD         0x0000
#define SYS_PORT_H_CNEN         0x0000

#define SYS_PORT_J_ANSEL        0x0B00
#define SYS_PORT_J_TRIS         0x0F02
#define SYS_PORT_J_LAT          0x0000
#define SYS_PORT_J_ODC          0x0000
#define SYS_PORT_J_CNPU         0x0000
#define SYS_PORT_J_CNPD         0x0000
#define SYS_PORT_J_CNEN         0x0000

#define SYS_PORT_K_ANSEL        0xFF00
#define SYS_PORT_K_TRIS         0xFF00
#define SYS_PORT_K_LAT          0x0000
#define SYS_PORT_K_ODC          0x0000
#define SYS_PORT_K_CNPU         0x0000
#define SYS_PORT_K_CNPD         0x0000
#define SYS_PORT_K_CNEN         0x0000


/*** Console System Service Configuration ***/

#define SYS_CONSOLE_OVERRIDE_STDIO
#define SYS_CONSOLE_DEVICE_MAX_INSTANCES        2
#define SYS_CONSOLE_INSTANCES_NUMBER            1
#define SYS_CONSOLE_UART_IDX               DRV_USART_INDEX_0
#define SYS_CONSOLE_UART_BAUD_RATE_IDX     DRV_USART_BAUD_RATE_IDX0
#define SYS_CONSOLE_UART_RD_QUEUE_DEPTH    64
#define SYS_CONSOLE_UART_WR_QUEUE_DEPTH    64
#define SYS_CONSOLE_BUFFER_DMA_READY        __attribute__((coherent)) __attribute__((aligned(16)))



/*** Debug System Service Configuration ***/
#define SYS_DEBUG_ENABLE
#define DEBUG_PRINT_BUFFER_SIZE       8192
#define SYS_DEBUG_BUFFER_DMA_READY        __attribute__((coherent)) __attribute__((aligned(16)))
#define SYS_DEBUG_USE_CONSOLE

/*** Interrupt System Service Configuration ***/
#define SYS_INT                     true
/*** Timer System Service Configuration ***/
#define SYS_TMR_POWER_STATE             SYS_MODULE_POWER_RUN_FULL
#define SYS_TMR_DRIVER_INDEX            DRV_TMR_INDEX_0
#define SYS_TMR_MAX_CLIENT_OBJECTS      5
#define SYS_TMR_FREQUENCY               1000
#define SYS_TMR_FREQUENCY_TOLERANCE     10
#define SYS_TMR_UNIT_RESOLUTION         10000
#define SYS_TMR_CLIENT_TOLERANCE        10
#define SYS_TMR_INTERRUPT_NOTIFICATION  false

// *****************************************************************************
// *****************************************************************************
// Section: Driver Configuration
// *****************************************************************************
// *****************************************************************************

/*** SPI Driver Configuration ***/
#define DRV_SPI_NUMBER_OF_MODULES		6
/*** Driver Compilation and static configuration options. ***/
/*** Select SPI compilation units.***/
#define DRV_SPI_POLLED 				0
#define DRV_SPI_ISR 				1
#define DRV_SPI_MASTER 				1
#define DRV_SPI_SLAVE 				0
#define DRV_SPI_RM 					0
#define DRV_SPI_EBM 				1
#define DRV_SPI_8BIT 				1
#define DRV_SPI_16BIT 				0
#define DRV_SPI_32BIT 				0
#define DRV_SPI_DMA 				0

/*** SPI Driver Static Allocation Options ***/
#define DRV_SPI_INSTANCES_NUMBER 		2
#define DRV_SPI_CLIENTS_NUMBER 			2
#define DRV_SPI_ELEMENTS_PER_QUEUE 		10
/*** Timer Driver Configuration ***/
#define DRV_TMR_INTERRUPT_MODE             true
#define DRV_TMR_INSTANCES_NUMBER           1
#define DRV_TMR_CLIENTS_NUMBER             1

/*** Timer Driver 0 Configuration ***/
#define DRV_TMR_PERIPHERAL_ID_IDX0          TMR_ID_1
#define DRV_TMR_INTERRUPT_SOURCE_IDX0       INT_SOURCE_TIMER_1
#define DRV_TMR_INTERRUPT_VECTOR_IDX0       INT_VECTOR_T1
#define DRV_TMR_ISR_VECTOR_IDX0             _TIMER_1_VECTOR
#define DRV_TMR_INTERRUPT_PRIORITY_IDX0     INT_PRIORITY_LEVEL1
#define DRV_TMR_INTERRUPT_SUB_PRIORITY_IDX0 INT_SUBPRIORITY_LEVEL0
#define DRV_TMR_CLOCK_SOURCE_IDX0           DRV_TMR_CLKSOURCE_INTERNAL
#define DRV_TMR_PRESCALE_IDX0               TMR_PRESCALE_VALUE_256
#define DRV_TMR_OPERATION_MODE_IDX0         DRV_TMR_OPERATION_MODE_16_BIT
#define DRV_TMR_ASYNC_WRITE_ENABLE_IDX0     false
#define DRV_TMR_POWER_STATE_IDX0            SYS_MODULE_POWER_RUN_FULL


 // *****************************************************************************
/* USART Driver Configuration Options
*/
#define DRV_USART_INTERRUPT_MODE                    true

#define DRV_USART_BYTE_MODEL_SUPPORT                false

#define DRV_USART_READ_WRITE_MODEL_SUPPORT          true

#define DRV_USART_BUFFER_QUEUE_SUPPORT              true

#define DRV_USART_CLIENTS_NUMBER                    1
#define DRV_USART_INSTANCES_NUMBER                  1

#define DRV_USART_PERIPHERAL_ID_IDX0                USART_ID_2
#define DRV_USART_OPER_MODE_IDX0                    DRV_USART_OPERATION_MODE_NORMAL
#define DRV_USART_OPER_MODE_DATA_IDX0               
#define DRV_USART_INIT_FLAG_WAKE_ON_START_IDX0      false
#define DRV_USART_INIT_FLAG_AUTO_BAUD_IDX0          false
#define DRV_USART_INIT_FLAG_STOP_IN_IDLE_IDX0       false
#define DRV_USART_INIT_FLAGS_IDX0                   0
#define DRV_USART_BRG_CLOCK_IDX0                    100000000
#define DRV_USART_BAUD_RATE_IDX0                    115200
#define DRV_USART_LINE_CNTRL_IDX0                   DRV_USART_LINE_CONTROL_8NONE1
#define DRV_USART_HANDSHAKE_MODE_IDX0               DRV_USART_HANDSHAKE_NONE
#define DRV_USART_LINES_ENABLE_IDX0                 USART_ENABLE_TX_RX_USED
#define DRV_USART_XMIT_INT_SRC_IDX0                 INT_SOURCE_USART_2_TRANSMIT
#define DRV_USART_RCV_INT_SRC_IDX0                  INT_SOURCE_USART_2_RECEIVE
#define DRV_USART_ERR_INT_SRC_IDX0                  INT_SOURCE_USART_2_ERROR
#define DRV_USART_XMIT_INT_VECTOR_IDX0              INT_VECTOR_UART2_TX
#define DRV_USART_XMIT_INT_PRIORITY_IDX0            INT_PRIORITY_LEVEL1
#define DRV_USART_XMIT_INT_SUB_PRIORITY_IDX0        INT_SUBPRIORITY_LEVEL0
#define DRV_USART_RCV_INT_VECTOR_IDX0               INT_VECTOR_UART2_RX
#define DRV_USART_RCV_INT_PRIORITY_IDX0             INT_PRIORITY_LEVEL1
#define DRV_USART_RCV_INT_SUB_PRIORITY_IDX0         INT_SUBPRIORITY_LEVEL0
#define DRV_USART_ERR_INT_VECTOR_IDX0               INT_VECTOR_UART2_FAULT
#define DRV_USART_ERR_INT_PRIORITY_IDX0             INT_PRIORITY_LEVEL1
#define DRV_USART_ERR_INT_SUB_PRIORITY_IDX0         INT_SUBPRIORITY_LEVEL0

#define DRV_USART_XMIT_QUEUE_SIZE_IDX0              10
#define DRV_USART_RCV_QUEUE_SIZE_IDX0               10


#define DRV_USART_POWER_STATE_IDX0                  SYS_MODULE_POWER_RUN_FULL

#define DRV_USART_QUEUE_DEPTH_COMBINED              20

// *****************************************************************************
// *****************************************************************************
// Section: Middleware & Other Library Configuration
// *****************************************************************************
// *****************************************************************************

/*** USB Driver Configuration ***/


/* Enables Device Support */
#define DRV_USBHS_DEVICE_SUPPORT      true

/* Disable Host Support */
#define DRV_USBHS_HOST_SUPPORT      false

/* Maximum USB driver instances */
#define DRV_USBHS_INSTANCES_NUMBER    1

/* Interrupt mode enabled */
#define DRV_USBHS_INTERRUPT_MODE      true


/* Number of Endpoints used */
#define DRV_USBHS_ENDPOINTS_NUMBER    3




/*** USB Device Stack Configuration ***/










/* The USB Device Layer will not initialize the USB Driver */
#define USB_DEVICE_DRIVER_INITIALIZE_EXPLICIT

/* Maximum device layer instances */
#define USB_DEVICE_INSTANCES_NUMBER     1

/* EP0 size in bytes */
#define USB_DEVICE_EP0_BUFFER_SIZE      64










/* Maximum instances of CDC function driver */
#define USB_DEVICE_CDC_INSTANCES_NUMBER     1










/* CDC Transfer Queue Size for both read and
   write. Applicable to all instances of the
   function driver */
#define USB_DEVICE_CDC_QUEUE_DEPTH_COMBINED 3



// *****************************************************************************
/* BSP Configuration Options
*/
#define BSP_OSC_FREQUENCY 24000000


// *****************************************************************************
// *****************************************************************************
// Section: Application Configuration
// *****************************************************************************
// *****************************************************************************
/*** Application Defined Pins ***/

/*** Functions for BSP_SWITCH_1 pin ***/
#define BSP_SWITCH_1StateGet() PLIB_PORTS_PinGet(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_12)

/*** Functions for BSP_SWITCH_2 pin ***/
#define BSP_SWITCH_2StateGet() PLIB_PORTS_PinGet(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_13)

/*** Functions for NRESET_FULL_CHIP pin ***/
#define NRESET_FULL_CHIPToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_6)
#define NRESET_FULL_CHIPOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_6)
#define NRESET_FULL_CHIPOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_6)
#define NRESET_FULL_CHIPStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_6)
#define NRESET_FULL_CHIPStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_6, Value)

/*** Functions for LATCH_CLK_DATA pin ***/
#define LATCH_CLK_DATAToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_7)
#define LATCH_CLK_DATAOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_7)
#define LATCH_CLK_DATAOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_7)
#define LATCH_CLK_DATAStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_7)
#define LATCH_CLK_DATAStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_7, Value)

/*** Functions for DPE_EXT_PULSE pin ***/
#define DPE_EXT_PULSEToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_1)
#define DPE_EXT_PULSEOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_1)
#define DPE_EXT_PULSEOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_1)
#define DPE_EXT_PULSEStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_1)
#define DPE_EXT_PULSEStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_1, Value)

/*** Functions for DPE_EXT_SH pin ***/
#define DPE_EXT_SHToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_2)
#define DPE_EXT_SHOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_2)
#define DPE_EXT_SHOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_2)
#define DPE_EXT_SHStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_2)
#define DPE_EXT_SHStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_2, Value)

/*** Functions for SERIAL_CHAIN_SEL_0 pin ***/
#define SERIAL_CHAIN_SEL_0Toggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_3)
#define SERIAL_CHAIN_SEL_0On() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_3)
#define SERIAL_CHAIN_SEL_0Off() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_3)
#define SERIAL_CHAIN_SEL_0StateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_3)
#define SERIAL_CHAIN_SEL_0StateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_3, Value)

/*** Functions for SERIAL_CHAIN_SEL_1 pin ***/
#define SERIAL_CHAIN_SEL_1Toggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_4)
#define SERIAL_CHAIN_SEL_1On() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_4)
#define SERIAL_CHAIN_SEL_1Off() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_4)
#define SERIAL_CHAIN_SEL_1StateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_4)
#define SERIAL_CHAIN_SEL_1StateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_4, Value)

/*** Functions for ADC_SEL_EXTERNAL pin ***/
#define ADC_SEL_EXTERNALToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_7)
#define ADC_SEL_EXTERNALOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_7)
#define ADC_SEL_EXTERNALOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_7)
#define ADC_SEL_EXTERNALStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_7)
#define ADC_SEL_EXTERNALStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_7, Value)

/*** Functions for ROW_WRITE_CONNECT pin ***/
#define ROW_WRITE_CONNECTToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_8)
#define ROW_WRITE_CONNECTOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_8)
#define ROW_WRITE_CONNECTOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_8)
#define ROW_WRITE_CONNECTStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_8)
#define ROW_WRITE_CONNECTStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_8, Value)

/*** Functions for PIC_SHORT_VREF_ARRAY pin ***/
#define PIC_SHORT_VREF_ARRAYToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_9)
#define PIC_SHORT_VREF_ARRAYOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_9)
#define PIC_SHORT_VREF_ARRAYOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_9)
#define PIC_SHORT_VREF_ARRAYStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_9)
#define PIC_SHORT_VREF_ARRAYStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_9, Value)

/*** Functions for WRITE_FWD pin ***/
#define WRITE_FWDToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_8)
#define WRITE_FWDOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_8)
#define WRITE_FWDOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_8)
#define WRITE_FWDStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_8)
#define WRITE_FWDStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_8, Value)

/*** Functions for WRITE_SEL_EXT pin ***/
#define WRITE_SEL_EXTToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_9)
#define WRITE_SEL_EXTOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_9)
#define WRITE_SEL_EXTOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_9)
#define WRITE_SEL_EXTStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_9)
#define WRITE_SEL_EXTStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_9, Value)

/*** Functions for DPE_INTERNAL_EN pin ***/
#define DPE_INTERNAL_ENToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_7)
#define DPE_INTERNAL_ENOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_7)
#define DPE_INTERNAL_ENOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_7)
#define DPE_INTERNAL_ENStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_7)
#define DPE_INTERNAL_ENStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_7, Value)

/*** Functions for PWR_GOOD pin ***/
#define PWR_GOODToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_9)
#define PWR_GOODOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_9)
#define PWR_GOODOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_9)
#define PWR_GOODStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_9)
#define PWR_GOODStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_9, Value)

/*** Functions for READ_BIT pin ***/
#define READ_BITToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_10)
#define READ_BITOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_10)
#define READ_BITOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_10)
#define READ_BITStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_10)
#define READ_BITStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_10, Value)

/*** Functions for WRT_INTERNAL_EN pin ***/
#define WRT_INTERNAL_ENToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_10)
#define WRT_INTERNAL_ENOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_10)
#define WRT_INTERNAL_ENOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_10)
#define WRT_INTERNAL_ENStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_10)
#define WRT_INTERNAL_ENStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_10, Value)

/*** Functions for AGC_INTERNAL_EN pin ***/
#define AGC_INTERNAL_ENToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_11)
#define AGC_INTERNAL_ENOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_11)
#define AGC_INTERNAL_ENOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_11)
#define AGC_INTERNAL_ENStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_11)
#define AGC_INTERNAL_ENStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_11, Value)

/*** Functions for COL_WRITE_CONNECT pin ***/
#define COL_WRITE_CONNECTToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_13)
#define COL_WRITE_CONNECTOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_13)
#define COL_WRITE_CONNECTOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_13)
#define COL_WRITE_CONNECTStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_13)
#define COL_WRITE_CONNECTStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_13, Value)

/*** Functions for COL_ROW_SEL pin ***/
#define COL_ROW_SELToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_12)
#define COL_ROW_SELOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_12)
#define COL_ROW_SELOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_12)
#define COL_ROW_SELStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_12)
#define COL_ROW_SELStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_12, Value)

/*** Functions for WRITE_ADD_CAP pin ***/
#define WRITE_ADD_CAPToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_15)
#define WRITE_ADD_CAPOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_15)
#define WRITE_ADD_CAPOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_15)
#define WRITE_ADD_CAPStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_15)
#define WRITE_ADD_CAPStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_B, PORTS_BIT_POS_15, Value)

/*** Functions for PIC_CS pin ***/
#define PIC_CSToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_14)
#define PIC_CSOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_14)
#define PIC_CSOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_14)
#define PIC_CSStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_14)
#define PIC_CSStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_14, Value)

/*** Functions for PIC_SCK pin ***/
#define PIC_SCKToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_15)
#define PIC_SCKOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_15)
#define PIC_SCKOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_15)
#define PIC_SCKStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_15)
#define PIC_SCKStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_15, Value)

/*** Functions for PIC_TGP pin ***/
#define PIC_TGPToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_2)
#define PIC_TGPOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_2)
#define PIC_TGPOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_2)
#define PIC_TGPStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_2)
#define PIC_TGPStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_2, Value)

/*** Functions for PIC_SHORT_VREF_HI_CMP pin ***/
#define PIC_SHORT_VREF_HI_CMPToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_8)
#define PIC_SHORT_VREF_HI_CMPOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_8)
#define PIC_SHORT_VREF_HI_CMPOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_8)
#define PIC_SHORT_VREF_HI_CMPStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_8)
#define PIC_SHORT_VREF_HI_CMPStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_8, Value)

/*** Functions for CONNECT_TIA pin ***/
#define CONNECT_TIAToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_4)
#define CONNECT_TIAOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_4)
#define CONNECT_TIAOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_4)
#define CONNECT_TIAStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_4)
#define CONNECT_TIAStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_4, Value)

/*** Functions for PICIC2_SDA pin ***/
#define PICIC2_SDAToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_5)
#define PICIC2_SDAOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_5)
#define PICIC2_SDAOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_5)
#define PICIC2_SDAStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_5)
#define PICIC2_SDAStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_5, Value)

/*** Functions for READ_DPE pin ***/
#define READ_DPEToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_14)
#define READ_DPEOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_14)
#define READ_DPEOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_14)
#define READ_DPEStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_14)
#define READ_DPEStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_14, Value)

/*** Functions for CONNECT_COLUMN_T pin ***/
#define CONNECT_COLUMN_TToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_15)
#define CONNECT_COLUMN_TOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_15)
#define CONNECT_COLUMN_TOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_15)
#define CONNECT_COLUMN_TStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_15)
#define CONNECT_COLUMN_TStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_A, PORTS_BIT_POS_15, Value)

/*** Functions for PIC_CLR pin ***/
#define PIC_CLRToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_9)
#define PIC_CLROn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_9)
#define PIC_CLROff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_9)
#define PIC_CLRStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_9)
#define PIC_CLRStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_9, Value)

/*** Functions for DPE_EXT_OVERRIDE_EN pin ***/
#define DPE_EXT_OVERRIDE_ENToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_10)
#define DPE_EXT_OVERRIDE_ENOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_10)
#define DPE_EXT_OVERRIDE_ENOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_10)
#define DPE_EXT_OVERRIDE_ENStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_10)
#define DPE_EXT_OVERRIDE_ENStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_10, Value)

/*** Functions for PIC_LDAC pin ***/
#define PIC_LDACToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_0)
#define PIC_LDACOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_0)
#define PIC_LDACOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_0)
#define PIC_LDACStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_0)
#define PIC_LDACStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_0, Value)

/*** Functions for UPDATE_TIA_CONF pin ***/
#define UPDATE_TIA_CONFToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_13)
#define UPDATE_TIA_CONFOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_13)
#define UPDATE_TIA_CONFOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_13)
#define UPDATE_TIA_CONFStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_13)
#define UPDATE_TIA_CONFStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_13, Value)

/*** Functions for PICI2C_RESET pin ***/
#define PICI2C_RESETToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_14)
#define PICI2C_RESETOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_14)
#define PICI2C_RESETOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_14)
#define PICI2C_RESETStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_14)
#define PICI2C_RESETStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_C, PORTS_BIT_POS_14, Value)

/*** Functions for PICIC2_SCL pin ***/
#define PICIC2_SCLToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_12)
#define PICIC2_SCLOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_12)
#define PICIC2_SCLOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_12)
#define PICIC2_SCLStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_12)
#define PICIC2_SCLStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_12, Value)

/*** Functions for NRESET_DPE_ENGINE pin ***/
#define NRESET_DPE_ENGINEToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_13)
#define NRESET_DPE_ENGINEOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_13)
#define NRESET_DPE_ENGINEOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_13)
#define NRESET_DPE_ENGINEStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_13)
#define NRESET_DPE_ENGINEStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_13, Value)

/*** Functions for AMP_EN pin ***/
#define AMP_ENToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_1)
#define AMP_ENOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_1)
#define AMP_ENOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_1)
#define AMP_ENStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_1)
#define AMP_ENStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_F, PORTS_BIT_POS_1, Value)

/*** Functions for ADC_FIFO_ADVANCE pin ***/
#define ADC_FIFO_ADVANCEToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_0)
#define ADC_FIFO_ADVANCEOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_0)
#define ADC_FIFO_ADVANCEOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_0)
#define ADC_FIFO_ADVANCEStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_0)
#define ADC_FIFO_ADVANCEStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_0, Value)

/*** Functions for AGC_PULSE pin ***/
#define AGC_PULSEToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_0)
#define AGC_PULSEOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_0)
#define AGC_PULSEOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_0)
#define AGC_PULSEStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_0)
#define AGC_PULSEStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_0, Value)

/*** Functions for WRT_PULSE pin ***/
#define WRT_PULSEToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_1)
#define WRT_PULSEOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_1)
#define WRT_PULSEOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_1)
#define WRT_PULSEStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_1)
#define WRT_PULSEStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_1, Value)

/*** Functions for DPE_PULSE pin ***/
#define DPE_PULSEToggle() PLIB_PORTS_PinToggle(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_12)
#define DPE_PULSEOn() PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_12)
#define DPE_PULSEOff() PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_12)
#define DPE_PULSEStateGet() PLIB_PORTS_PinGetLatched(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_12)
#define DPE_PULSEStateSet(Value) PLIB_PORTS_PinWrite(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_12, Value)

/*** Functions for SERIAL_CLK_OUT pin ***/
#define SERIAL_CLK_OUTStateGet() PLIB_PORTS_PinGet(PORTS_ID_0, PORT_CHANNEL_E, PORTS_BIT_POS_5)

/*** Functions for ADC_DONE pin ***/
#define ADC_DONEStateGet() PLIB_PORTS_PinGet(PORTS_ID_0, PORT_CHANNEL_G, PORTS_BIT_POS_1)

/*** Functions for ADC_OUT_9 pin ***/
#define ADC_OUT_9_PORT PORT_CHANNEL_G
#define ADC_OUT_9_PIN PORTS_BIT_POS_15
#define ADC_OUT_9_PIN_MASK (0x1 << 15)

/*** Functions for ADC_OUT_5 pin ***/
#define ADC_OUT_5_PORT PORT_CHANNEL_A
#define ADC_OUT_5_PIN PORTS_BIT_POS_5
#define ADC_OUT_5_PIN_MASK (0x1 << 5)

/*** Functions for ROW_COL_DATA_12 pin ***/
#define ROW_COL_DATA_12_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_12_PIN PORTS_BIT_POS_12
#define ROW_COL_DATA_12_PIN_MASK (0x1 << 12)

/*** Functions for ROW_COL_BANK_0 pin ***/
#define ROW_COL_BANK_0_PORT PORT_CHANNEL_K
#define ROW_COL_BANK_0_PIN PORTS_BIT_POS_0
#define ROW_COL_BANK_0_PIN_MASK (0x1 << 0)

/*** Functions for ADC_OUT_0 pin ***/
#define ADC_OUT_0_PORT PORT_CHANNEL_A
#define ADC_OUT_0_PIN PORTS_BIT_POS_0
#define ADC_OUT_0_PIN_MASK (0x1 << 0)

/*** Functions for ROW_COL_DATA_13 pin ***/
#define ROW_COL_DATA_13_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_13_PIN PORTS_BIT_POS_13
#define ROW_COL_DATA_13_PIN_MASK (0x1 << 13)

/*** Functions for ROW_COL_DATA_14 pin ***/
#define ROW_COL_DATA_14_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_14_PIN PORTS_BIT_POS_14
#define ROW_COL_DATA_14_PIN_MASK (0x1 << 14)

/*** Functions for ROW_COL_DATA_15 pin ***/
#define ROW_COL_DATA_15_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_15_PIN PORTS_BIT_POS_15
#define ROW_COL_DATA_15_PIN_MASK (0x1 << 15)

/*** Functions for ADC_OUT_10 pin ***/
#define ADC_OUT_10_PORT PORT_CHANNEL_H
#define ADC_OUT_10_PIN PORTS_BIT_POS_0
#define ADC_OUT_10_PIN_MASK (0x1 << 0)

/*** Functions for ADC_OUT_11 pin ***/
#define ADC_OUT_11_PORT PORT_CHANNEL_H
#define ADC_OUT_11_PIN PORTS_BIT_POS_1
#define ADC_OUT_11_PIN_MASK (0x1 << 1)

/*** Functions for ADC_OUT_12 pin ***/
#define ADC_OUT_12_PORT PORT_CHANNEL_H
#define ADC_OUT_12_PIN PORTS_BIT_POS_2
#define ADC_OUT_12_PIN_MASK (0x1 << 2)

/*** Functions for ARRAY_EN_0 pin ***/
#define ARRAY_EN_0_PORT PORT_CHANNEL_H
#define ARRAY_EN_0_PIN PORTS_BIT_POS_3
#define ARRAY_EN_0_PIN_MASK (0x1 << 3)

/*** Functions for NFORCE_SAFE0 pin ***/
#define NFORCE_SAFE0_PORT PORT_CHANNEL_B
#define NFORCE_SAFE0_PIN PORTS_BIT_POS_9
#define NFORCE_SAFE0_PIN_MASK (0x1 << 9)

/*** Functions for ROW_COL_BANK_1 pin ***/
#define ROW_COL_BANK_1_PORT PORT_CHANNEL_K
#define ROW_COL_BANK_1_PIN PORTS_BIT_POS_1
#define ROW_COL_BANK_1_PIN_MASK (0x1 << 1)

/*** Functions for ROW_COL_BANK_2 pin ***/
#define ROW_COL_BANK_2_PORT PORT_CHANNEL_K
#define ROW_COL_BANK_2_PIN PORTS_BIT_POS_2
#define ROW_COL_BANK_2_PIN_MASK (0x1 << 2)

/*** Functions for ROW_COL_BANK_3 pin ***/
#define ROW_COL_BANK_3_PORT PORT_CHANNEL_K
#define ROW_COL_BANK_3_PIN PORTS_BIT_POS_3
#define ROW_COL_BANK_3_PIN_MASK (0x1 << 3)

/*** Functions for ADC_OUT_1 pin ***/
#define ADC_OUT_1_PORT PORT_CHANNEL_A
#define ADC_OUT_1_PIN PORTS_BIT_POS_1
#define ADC_OUT_1_PIN_MASK (0x1 << 1)

/*** Functions for ARRAY_EN_1 pin ***/
#define ARRAY_EN_1_PORT PORT_CHANNEL_H
#define ARRAY_EN_1_PIN PORTS_BIT_POS_6
#define ARRAY_EN_1_PIN_MASK (0x1 << 6)

/*** Functions for ARRAY_EN_2 pin ***/
#define ARRAY_EN_2_PORT PORT_CHANNEL_H
#define ARRAY_EN_2_PIN PORTS_BIT_POS_7
#define ARRAY_EN_2_PIN_MASK (0x1 << 7)

/*** Functions for ROW_COL_DATA_0 pin ***/
#define ROW_COL_DATA_0_PORT PORT_CHANNEL_H
#define ROW_COL_DATA_0_PIN PORTS_BIT_POS_9
#define ROW_COL_DATA_0_PIN_MASK (0x1 << 9)

/*** Functions for ROW_COL_DATA_1 pin ***/
#define ROW_COL_DATA_1_PORT PORT_CHANNEL_H
#define ROW_COL_DATA_1_PIN PORTS_BIT_POS_10
#define ROW_COL_DATA_1_PIN_MASK (0x1 << 10)

/*** Functions for ROW_COL_DATA_2 pin ***/
#define ROW_COL_DATA_2_PORT PORT_CHANNEL_H
#define ROW_COL_DATA_2_PIN PORTS_BIT_POS_11
#define ROW_COL_DATA_2_PIN_MASK (0x1 << 11)

/*** Functions for ADC_OUT_2 pin ***/
#define ADC_OUT_2_PORT PORT_CHANNEL_A
#define ADC_OUT_2_PIN PORTS_BIT_POS_2
#define ADC_OUT_2_PIN_MASK (0x1 << 2)

/*** Functions for ADC_OUT_3 pin ***/
#define ADC_OUT_3_PORT PORT_CHANNEL_A
#define ADC_OUT_3_PIN PORTS_BIT_POS_3
#define ADC_OUT_3_PIN_MASK (0x1 << 3)

/*** Functions for ADC_OUT_4 pin ***/
#define ADC_OUT_4_PORT PORT_CHANNEL_A
#define ADC_OUT_4_PIN PORTS_BIT_POS_4
#define ADC_OUT_4_PIN_MASK (0x1 << 4)

/*** Functions for ADC_FIFO_EN_0 pin ***/
#define ADC_FIFO_EN_0_PORT PORT_CHANNEL_K
#define ADC_FIFO_EN_0_PIN PORTS_BIT_POS_4
#define ADC_FIFO_EN_0_PIN_MASK (0x1 << 4)

/*** Functions for ADC_FIFO_EN_1 pin ***/
#define ADC_FIFO_EN_1_PORT PORT_CHANNEL_K
#define ADC_FIFO_EN_1_PIN PORTS_BIT_POS_5
#define ADC_FIFO_EN_1_PIN_MASK (0x1 << 5)

/*** Functions for ADC_FIFO_EN_2 pin ***/
#define ADC_FIFO_EN_2_PORT PORT_CHANNEL_K
#define ADC_FIFO_EN_2_PIN PORTS_BIT_POS_6
#define ADC_FIFO_EN_2_PIN_MASK (0x1 << 6)

/*** Functions for ROW_COL_DATA_3 pin ***/
#define ROW_COL_DATA_3_PORT PORT_CHANNEL_H
#define ROW_COL_DATA_3_PIN PORTS_BIT_POS_12
#define ROW_COL_DATA_3_PIN_MASK (0x1 << 12)

/*** Functions for ROW_COL_DATA_4 pin ***/
#define ROW_COL_DATA_4_PORT PORT_CHANNEL_H
#define ROW_COL_DATA_4_PIN PORTS_BIT_POS_15
#define ROW_COL_DATA_4_PIN_MASK (0x1 << 15)

/*** Functions for ROW_COL_DATA_5 pin ***/
#define ROW_COL_DATA_5_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_5_PIN PORTS_BIT_POS_0
#define ROW_COL_DATA_5_PIN_MASK (0x1 << 0)

/*** Functions for ROW_COL_DATA_6 pin ***/
#define ROW_COL_DATA_6_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_6_PIN PORTS_BIT_POS_2
#define ROW_COL_DATA_6_PIN_MASK (0x1 << 2)

/*** Functions for ROW_COL_DATA_7 pin ***/
#define ROW_COL_DATA_7_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_7_PIN PORTS_BIT_POS_3
#define ROW_COL_DATA_7_PIN_MASK (0x1 << 3)

/*** Functions for ADC_FIFO_EN_3 pin ***/
#define ADC_FIFO_EN_3_PORT PORT_CHANNEL_K
#define ADC_FIFO_EN_3_PIN PORTS_BIT_POS_7
#define ADC_FIFO_EN_3_PIN_MASK (0x1 << 7)

/*** Functions for ADC_OUT_6 pin ***/
#define ADC_OUT_6_PORT PORT_CHANNEL_A
#define ADC_OUT_6_PIN PORTS_BIT_POS_6
#define ADC_OUT_6_PIN_MASK (0x1 << 6)

/*** Functions for ADC_OUT_7 pin ***/
#define ADC_OUT_7_PORT PORT_CHANNEL_A
#define ADC_OUT_7_PIN PORTS_BIT_POS_7
#define ADC_OUT_7_PIN_MASK (0x1 << 7)

/*** Functions for ROW_COL_DATA_8 pin ***/
#define ROW_COL_DATA_8_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_8_PIN PORTS_BIT_POS_4
#define ROW_COL_DATA_8_PIN_MASK (0x1 << 4)

/*** Functions for ROW_COL_DATA_9 pin ***/
#define ROW_COL_DATA_9_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_9_PIN PORTS_BIT_POS_5
#define ROW_COL_DATA_9_PIN_MASK (0x1 << 5)

/*** Functions for ROW_COL_DATA_10 pin ***/
#define ROW_COL_DATA_10_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_10_PIN PORTS_BIT_POS_6
#define ROW_COL_DATA_10_PIN_MASK (0x1 << 6)

/*** Functions for ROW_COL_DATA_11 pin ***/
#define ROW_COL_DATA_11_PORT PORT_CHANNEL_J
#define ROW_COL_DATA_11_PIN PORTS_BIT_POS_7
#define ROW_COL_DATA_11_PIN_MASK (0x1 << 7)

/*** Functions for ADC_OUT_8 pin ***/
#define ADC_OUT_8_PORT PORT_CHANNEL_G
#define ADC_OUT_8_PIN PORTS_BIT_POS_14
#define ADC_OUT_8_PIN_MASK (0x1 << 14)

/*** Functions for NFORCE_SAFE1 pin ***/
#define NFORCE_SAFE1_PORT PORT_CHANNEL_G
#define NFORCE_SAFE1_PIN PORTS_BIT_POS_13
#define NFORCE_SAFE1_PIN_MASK (0x1 << 13)

/*** Functions for NFORCE_SAFE2 pin ***/
#define NFORCE_SAFE2_PORT PORT_CHANNEL_E
#define NFORCE_SAFE2_PIN PORTS_BIT_POS_2
#define NFORCE_SAFE2_PIN_MASK (0x1 << 2)


/*** Application Instance 0 Configuration ***/

//DOM-IGNORE-BEGIN
#ifdef __cplusplus
}
#endif
//DOM-IGNORE-END

#endif // _SYSTEM_CONFIG_H
/*******************************************************************************
 End of File
*/
