/*******************************************************************************
  SPI Driver Static implementation

  Company:
    Microchip Technology Inc.

  File Name:
    drv_spi_static.c

  Summary:
    Source code for the SPI driver static implementation.

  Description:
    The SPI device driver provides a simple interface to manage the SPI
    modules on Microchip microcontrollers. This file contains static implementation
    for the SPI driver.

  Remarks:
    Static interfaces incorporate the driver instance number within the names
    of the routines, eliminating the need for an object ID or object handle.

    Static single-open interfaces also eliminate the need for the open handle.
*******************************************************************************/

//DOM-IGNORE-BEGIN
/*******************************************************************************
Copyright (c) 2015 released Microchip Technology Inc.  All rights reserved.

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
//DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

#include <string.h>
#include "system_config.h"
#include "system_definitions.h"
#include "driver/spi/static/src/drv_spi_static_local.h"
// *****************************************************************************
// *****************************************************************************
// Section: Global Data
// *****************************************************************************
// *****************************************************************************
static uint8_t sDrvSPIQueueArea[DRV_SPI_SYS_QUEUE_BUFFER_SIZE(DRV_SPI_INSTANCES_NUMBER, sizeof(DRV_SPI_JOB_OBJECT), DRV_SPI_INSTANCES_NUMBER * DRV_SPI_ELEMENTS_PER_QUEUE)];

/* This is the Queue manager object . */
static DRV_SPI_SYS_QUEUE_MANAGER_SETUP qmInitData = {
    sDrvSPIQueueArea,
    sizeof(sDrvSPIQueueArea),
    DRV_SPI_INSTANCES_NUMBER,
    sizeof(DRV_SPI_JOB_OBJECT),
    DRV_SPI_SYS_QUEUE_Fifo,
};

/* This is the Queue setup object . */
static DRV_SPI_SYS_QUEUE_SETUP qInitData =
{
    0,
    10,
    0,
};

/* This is the Queue Manager handle*/
DRV_SPI_SYS_QUEUE_MANAGER_HANDLE  hQueueManager;


// *****************************************************************************
// *****************************************************************************
// Section: Instance 0 static driver functions
// *****************************************************************************
// *****************************************************************************
/* This is the driver static object . */
DRV_SPI_OBJ  gDrvSPI0Obj ;

SYS_MODULE_OBJ DRV_SPI0_Initialize(void)
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI0Obj;

    /* Disable the SPI module to configure it*/
    PLIB_SPI_Disable ( SPI_ID_1 );

    /* Set up Master or Slave Mode*/
    PLIB_SPI_MasterEnable ( SPI_ID_1 );
    PLIB_SPI_PinDisable(SPI_ID_1, SPI_PIN_SLAVE_SELECT);

    /* Set up if the SPI is allowed to run while the rest of the CPU is in idle mode*/
    PLIB_SPI_StopInIdleEnable( SPI_ID_1 );

    /* Set up clock Polarity and output data phase*/
    PLIB_SPI_ClockPolaritySelect( SPI_ID_1, SPI_CLOCK_POLARITY_IDLE_LOW );
    PLIB_SPI_OutputDataPhaseSelect( SPI_ID_1, SPI_OUTPUT_DATA_PHASE_ON_ACTIVE_TO_IDLE_CLOCK );

    /* Set up the Input Sample Phase*/
    PLIB_SPI_InputSamplePhaseSelect ( SPI_ID_1, SPI_INPUT_SAMPLING_PHASE_IN_MIDDLE);

    /* Communication Width Selection */
    PLIB_SPI_CommunicationWidthSelect ( SPI_ID_1, SPI_COMMUNICATION_WIDTH_8BITS );

    /* Baud rate selection */
    PLIB_SPI_BaudRateSet( SPI_ID_1 , SYS_CLK_PeripheralFrequencyGet(CLK_BUS_PERIPHERAL_2), 10000000 );

    /* Protocol selection */
    PLIB_SPI_FramedCommunicationDisable( SPI_ID_1  );
    #if defined (PLIB_SPI_ExistsAudioProtocolControl)
            if (PLIB_SPI_ExistsAudioProtocolControl(SPI_ID_1))
            {
                PLIB_SPI_AudioProtocolDisable(SPI_ID_1);
            }
    #endif

    /* Buffer type selection */
    #if defined (PLIB_SPI_ExistsFIFOControl)
        if (PLIB_SPI_ExistsFIFOControl( SPI_ID_1 ))
        {
            PLIB_SPI_FIFOEnable( SPI_ID_1 );
            PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_1, SPI_FIFO_INTERRUPT_WHEN_TRANSMIT_BUFFER_IS_COMPLETELY_EMPTY);
            PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_1, SPI_FIFO_INTERRUPT_WHEN_RECEIVE_BUFFER_IS_NOT_EMPTY);
        }
    #else
        {
            SYS_ASSERT(false, "\r\nInvalid SPI Configuration.");
            return SYS_MODULE_OBJ_INVALID;
        }
    #endif

    PLIB_SPI_BufferClear( SPI_ID_1 );
    PLIB_SPI_ReceiverOverflowClear ( SPI_ID_1 );

    /* Initialize Queue only once for all instances of SPI driver*/
    if (DRV_SPI_SYS_QUEUE_Initialize(&qmInitData, &hQueueManager) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Could not create queuing system.");
        return SYS_MODULE_OBJ_INVALID;
    }

    /* Update the Queue parameters. */
    qInitData.maxElements = 10; //Queue size
    qInitData.reserveElements = 1; //Mininmum number of job queues reserved

    /* Create Queue for this instance of SPI */
    if (DRV_SPI_SYS_QUEUE_CreateQueue(hQueueManager, &qInitData, &dObj->queue) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Could not set up driver instance queue.");
        return SYS_MODULE_OBJ_INVALID;

    }

    /* Update the SPI OBJECT parameters. */
    dObj->operationStarting = NULL;
    dObj->operationEnded = NULL;

    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_TRANSMIT);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_RECEIVE);
    SYS_INT_SourceEnable(INT_SOURCE_SPI_1_ERROR);

    /* Clear all interrupt sources */
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_TRANSMIT);
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_RECEIVE);
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_ERROR);

    /* Enable the Module */
    PLIB_SPI_Enable(SPI_ID_1);

    return (SYS_MODULE_OBJ)DRV_SPI_INDEX_0 ;
}

void DRV_SPI0_Deinitialize ( void )
{
    /* Disable the interrupts */
    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_TRANSMIT);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_RECEIVE);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_ERROR);

    /* Disable the SPI Module */
    PLIB_SPI_Disable(SPI_ID_1);

    return;
}

SYS_STATUS DRV_SPI0_Status ( void )
{
    /* Return the current status of driver instance */
    return SYS_STATUS_READY;
}

void DRV_SPI0_Tasks ( void )
{
    /* Call the respective task routine */
    DRV_SPI0_ISRMasterEBM8BitTasks(&gDrvSPI0Obj);
}

DRV_HANDLE DRV_SPI0_Open ( const SYS_MODULE_INDEX index, const DRV_IO_INTENT intent )
{
    return (DRV_HANDLE)DRV_SPI_INDEX_0;
}

void DRV_SPI0_Close ( void )
{
    return;
}

int32_t DRV_SPI0_ClientConfigure ( const DRV_SPI_CLIENT_DATA * cfgData  )
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI0Obj;

    if (cfgData == NULL)
    {
        /* Nothing to do */
        return 0;
    }

    if (cfgData->operationStarting != NULL)
    {
        dObj->operationStarting = cfgData->operationStarting;
    }

    if (cfgData->operationEnded != NULL)
    {
        dObj->operationEnded = cfgData->operationEnded;
    }

    if (cfgData->baudRate != 0)
    {

        PLIB_SPI_BaudRateSet (SPI_ID_1,
                              SYS_CLK_PeripheralFrequencyGet(CLK_BUS_PERIPHERAL_2),
                              cfgData->baudRate);
    }

    return 0;
}

DRV_SPI_BUFFER_HANDLE DRV_SPI0_BufferAddRead2 ( void *rxBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context, DRV_SPI_BUFFER_HANDLE * jobHandle)
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI0Obj;

    DRV_SPI_JOB_OBJECT * pJob = NULL;

    if (DRV_SPI_SYS_QUEUE_AllocElementLock(dObj->queue, (void **)&pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error trying to get a free entry.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    memset(pJob, 0, sizeof(DRV_SPI_JOB_OBJECT));

    pJob->rxBuffer = rxBuffer;
    pJob->dataLeftToRx = size;
    pJob->dummyLeftToTx = size;
    pJob->completeCB = completeCB;
    pJob->context = context;
    pJob->status = DRV_SPI_BUFFER_EVENT_PENDING;

    if (jobHandle != NULL )
    {
        *jobHandle = (DRV_SPI_BUFFER_HANDLE)pJob;
    }

    if (DRV_SPI_SYS_QUEUE_EnqueueLock(dObj->queue, (void*)pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error enqueing new job.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    dObj->txEnabled = true;
    SYS_INT_SourceEnable(INT_SOURCE_SPI_1_TRANSMIT);

    return (DRV_SPI_BUFFER_HANDLE)pJob;
}


DRV_SPI_BUFFER_HANDLE DRV_SPI0_BufferAddWrite2 ( void *txBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context, DRV_SPI_BUFFER_HANDLE * jobHandle )
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI0Obj;

    DRV_SPI_JOB_OBJECT * pJob = NULL;
    if (DRV_SPI_SYS_QUEUE_AllocElementLock(dObj->queue, (void **)&pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error trying to get a free entry.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    memset(pJob, 0, sizeof(DRV_SPI_JOB_OBJECT));
    pJob->txBuffer = txBuffer;
    pJob->dataLeftToTx = size;
    pJob->dummyLeftToRx = size;
    pJob->completeCB = completeCB;
    pJob->context = context;
    pJob->status = DRV_SPI_BUFFER_EVENT_PENDING;

    if (jobHandle != NULL )
    {
        *jobHandle = (DRV_SPI_BUFFER_HANDLE)pJob;
    }

    if (DRV_SPI_SYS_QUEUE_EnqueueLock(dObj->queue, (void*)pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error enqueing new job.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    dObj->txEnabled = true;
    SYS_INT_SourceEnable(INT_SOURCE_SPI_1_TRANSMIT);

    return (DRV_SPI_BUFFER_HANDLE)pJob;
}


DRV_SPI_BUFFER_HANDLE DRV_SPI0_BufferAddWriteRead2 ( void *txBuffer, size_t txSize, void *rxBuffer, size_t rxSize, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context, DRV_SPI_BUFFER_HANDLE * jobHandle )
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI0Obj;

    DRV_SPI_JOB_OBJECT * pJob = NULL;
    if (DRV_SPI_SYS_QUEUE_AllocElementLock(dObj->queue, (void **)&pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error trying to get a free entry.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    memset(pJob, 0, sizeof(DRV_SPI_JOB_OBJECT));
    pJob->txBuffer = txBuffer;
    pJob->dataLeftToTx = txSize;
    pJob->rxBuffer = rxBuffer;
    pJob->dataLeftToRx = rxSize;

    if (jobHandle != NULL )
    {
        *jobHandle = (DRV_SPI_BUFFER_HANDLE)pJob;
    }
    if (rxSize > txSize)
    {
        pJob->dummyLeftToTx = rxSize - txSize;
    }
    if (txSize > rxSize)
    {
        pJob->dummyLeftToRx = txSize - rxSize;
    }
    pJob->completeCB = completeCB;
    pJob->context = context;
    pJob->status = DRV_SPI_BUFFER_EVENT_PENDING;

    if (DRV_SPI_SYS_QUEUE_EnqueueLock(dObj->queue, (void*)pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error enqueing new job.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    dObj->txEnabled = true;
    SYS_INT_SourceEnable(INT_SOURCE_SPI_1_TRANSMIT);

    return (DRV_SPI_BUFFER_HANDLE)pJob;
}


DRV_SPI_BUFFER_HANDLE DRV_SPI0_BufferAddRead ( void *rxBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context)
{
    return DRV_SPI0_BufferAddRead2(rxBuffer, size, completeCB, context, NULL);
}

DRV_SPI_BUFFER_HANDLE DRV_SPI0_BufferAddWrite ( void *txBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context )
{
    return DRV_SPI0_BufferAddWrite2(txBuffer, size, completeCB, context, NULL);
}

DRV_SPI_BUFFER_EVENT DRV_SPI0_BufferStatus ( DRV_SPI_BUFFER_HANDLE bufferHandle )
{
    DRV_SPI_JOB_OBJECT * pJob = (DRV_SPI_JOB_OBJECT *)bufferHandle;

    return pJob->status;
}



int32_t DRV_SPI0_ISRErrorTasks(struct DRV_SPI_OBJ * dObj)
{

    if (dObj->currentJob == NULL)
    {
        return 0;
    }

    register DRV_SPI_JOB_OBJECT * currentJob = dObj->currentJob;

    if (PLIB_SPI_ReceiverHasOverflowed(SPI_ID_1))
    {
        if (currentJob->completeCB != NULL)
        {
            (*currentJob->completeCB)(DRV_SPI_BUFFER_EVENT_ERROR, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
        }
        currentJob->status = DRV_SPI_BUFFER_EVENT_ERROR;
        if (dObj->operationEnded != NULL)
        {
            (*dObj->operationEnded)(DRV_SPI_BUFFER_EVENT_ERROR, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
        }
        if (DRV_SPI_SYS_QUEUE_FreeElement(dObj->queue, currentJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
        {
            SYS_ASSERT(false, "\r\nSPI Driver: Queue free element error.");
            return 0;
        }
        dObj->currentJob = NULL;
        PLIB_SPI_BufferClear(SPI_ID_1);
        PLIB_SPI_ReceiverOverflowClear (SPI_ID_1 );
        SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_ERROR);

    }
    return 0;
}

// *********************************************************************************************
// *********************************************************************************************
// Section: Old static driver compatibility APIs, these will be deprecated.
// *********************************************************************************************
// *********************************************************************************************
bool DRV_SPI0_ReceiverBufferIsFull(void)
{
    return (PLIB_SPI_ReceiverBufferIsFull(SPI_ID_1));
}

bool DRV_SPI0_TransmitterBufferIsFull(void)
{
    return (PLIB_SPI_TransmitBufferIsFull(SPI_ID_1));
}

int32_t DRV_SPI0_BufferAddWriteRead(const void * txBuffer, void * rxBuffer, uint32_t size)
{
    bool continueLoop;
    int32_t txcounter = 0;
    int32_t rxcounter = 0;
    uint8_t unitsTxed = 0;
    const uint8_t maxUnits = 16;
    do {
        continueLoop = false;
        unitsTxed = 0;
        if (PLIB_SPI_TransmitBufferIsEmpty(SPI_ID_1))
        {
            while (!PLIB_SPI_TransmitBufferIsFull(SPI_ID_1) && (txcounter < size) && unitsTxed != maxUnits)
            {
                PLIB_SPI_BufferWrite(SPI_ID_1, ((uint8_t*)txBuffer)[txcounter]);
                txcounter++;
                continueLoop = true;
                unitsTxed++;
            }
        }

        while (txcounter != rxcounter)
        {
            while (PLIB_SPI_ReceiverFIFOIsEmpty(SPI_ID_1));
            ((uint8_t*)rxBuffer)[rxcounter] = PLIB_SPI_BufferRead(SPI_ID_1);
            rxcounter++;
            continueLoop = true;
        }
        if (txcounter > rxcounter)
        {
            continueLoop = true;
        }
    }while(continueLoop);
    return txcounter;
}


// *****************************************************************************
// *****************************************************************************
// Section: Instance 1 static driver functions
// *****************************************************************************
// *****************************************************************************
/* This is the driver static object . */
DRV_SPI_OBJ  gDrvSPI1Obj ;

SYS_MODULE_OBJ DRV_SPI1_Initialize(void)
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI1Obj;

    /* Disable the SPI module to configure it*/
    PLIB_SPI_Disable ( SPI_ID_6 );

    /* Set up Master or Slave Mode*/
    PLIB_SPI_MasterEnable ( SPI_ID_6 );
    PLIB_SPI_PinDisable(SPI_ID_6, SPI_PIN_SLAVE_SELECT);

    /* Set up if the SPI is allowed to run while the rest of the CPU is in idle mode*/
    PLIB_SPI_StopInIdleEnable( SPI_ID_6 );

    /* Set up clock Polarity and output data phase*/
    PLIB_SPI_ClockPolaritySelect( SPI_ID_6, SPI_CLOCK_POLARITY_IDLE_LOW );
    PLIB_SPI_OutputDataPhaseSelect( SPI_ID_6, SPI_OUTPUT_DATA_PHASE_ON_ACTIVE_TO_IDLE_CLOCK );

    /* Set up the Input Sample Phase*/
    PLIB_SPI_InputSamplePhaseSelect ( SPI_ID_6, SPI_INPUT_SAMPLING_PHASE_IN_MIDDLE);

    /* Communication Width Selection */
    PLIB_SPI_CommunicationWidthSelect ( SPI_ID_6, SPI_COMMUNICATION_WIDTH_8BITS );

    /* Baud rate selection */
    PLIB_SPI_BaudRateSet( SPI_ID_6 , SYS_CLK_PeripheralFrequencyGet(CLK_BUS_PERIPHERAL_2), 10000000 );

    /* Protocol selection */
    PLIB_SPI_FramedCommunicationDisable( SPI_ID_6  );
    #if defined (PLIB_SPI_ExistsAudioProtocolControl)
            if (PLIB_SPI_ExistsAudioProtocolControl(SPI_ID_6))
            {
                PLIB_SPI_AudioProtocolDisable(SPI_ID_6);
            }
    #endif

    /* Buffer type selection */
    #if defined (PLIB_SPI_ExistsFIFOControl)
        if (PLIB_SPI_ExistsFIFOControl( SPI_ID_6 ))
        {
            PLIB_SPI_FIFOEnable( SPI_ID_6 );
            PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_6, SPI_FIFO_INTERRUPT_WHEN_TRANSMIT_BUFFER_IS_COMPLETELY_EMPTY);
            PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_6, SPI_FIFO_INTERRUPT_WHEN_RECEIVE_BUFFER_IS_NOT_EMPTY);
        }
    #else
        {
            SYS_ASSERT(false, "\r\nInvalid SPI Configuration.");
            return SYS_MODULE_OBJ_INVALID;
        }
    #endif

    PLIB_SPI_BufferClear( SPI_ID_6 );
    PLIB_SPI_ReceiverOverflowClear ( SPI_ID_6 );

    /* Update the Queue parameters. */
    qInitData.maxElements = 10; //Queue size
    qInitData.reserveElements = 1; //Mininmum number of job queues reserved

    /* Create Queue for this instance of SPI */
    if (DRV_SPI_SYS_QUEUE_CreateQueue(hQueueManager, &qInitData, &dObj->queue) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Could not set up driver instance queue.");
        return SYS_MODULE_OBJ_INVALID;

    }

    /* Update the SPI OBJECT parameters. */
    dObj->operationStarting = NULL;
    dObj->operationEnded = NULL;

    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_TRANSMIT);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_RECEIVE);
    SYS_INT_SourceEnable(INT_SOURCE_SPI_6_ERROR);

    /* Clear all interrupt sources */
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_TRANSMIT);
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_RECEIVE);
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_ERROR);

    /* Enable the Module */
    PLIB_SPI_Enable(SPI_ID_6);

    return (SYS_MODULE_OBJ)DRV_SPI_INDEX_1 ;
}

void DRV_SPI1_Deinitialize ( void )
{
    /* Disable the interrupts */
    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_TRANSMIT);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_RECEIVE);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_ERROR);

    /* Disable the SPI Module */
    PLIB_SPI_Disable(SPI_ID_6);

    return;
}

SYS_STATUS DRV_SPI1_Status ( void )
{
    /* Return the current status of driver instance */
    return SYS_STATUS_READY;
}

void DRV_SPI1_Tasks ( void )
{
    /* Call the respective task routine */
    DRV_SPI1_ISRMasterEBM8BitTasks(&gDrvSPI1Obj);
}

DRV_HANDLE DRV_SPI1_Open ( const SYS_MODULE_INDEX index, const DRV_IO_INTENT intent )
{
    return (DRV_HANDLE)DRV_SPI_INDEX_1;
}

void DRV_SPI1_Close ( void )
{
    return;
}

int32_t DRV_SPI1_ClientConfigure ( const DRV_SPI_CLIENT_DATA * cfgData  )
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI1Obj;

    if (cfgData == NULL)
    {
        /* Nothing to do */
        return 0;
    }

    if (cfgData->operationStarting != NULL)
    {
        dObj->operationStarting = cfgData->operationStarting;
    }

    if (cfgData->operationEnded != NULL)
    {
        dObj->operationEnded = cfgData->operationEnded;
    }

    if (cfgData->baudRate != 0)
    {

        PLIB_SPI_BaudRateSet (SPI_ID_6,
                              SYS_CLK_PeripheralFrequencyGet(CLK_BUS_PERIPHERAL_2),
                              cfgData->baudRate);
    }

    return 0;
}

DRV_SPI_BUFFER_HANDLE DRV_SPI1_BufferAddRead2 ( void *rxBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context, DRV_SPI_BUFFER_HANDLE * jobHandle)
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI1Obj;

    DRV_SPI_JOB_OBJECT * pJob = NULL;

    if (DRV_SPI_SYS_QUEUE_AllocElementLock(dObj->queue, (void **)&pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error trying to get a free entry.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    memset(pJob, 0, sizeof(DRV_SPI_JOB_OBJECT));

    pJob->rxBuffer = rxBuffer;
    pJob->dataLeftToRx = size;
    pJob->dummyLeftToTx = size;
    pJob->completeCB = completeCB;
    pJob->context = context;
    pJob->status = DRV_SPI_BUFFER_EVENT_PENDING;

    if (jobHandle != NULL )
    {
        *jobHandle = (DRV_SPI_BUFFER_HANDLE)pJob;
    }

    if (DRV_SPI_SYS_QUEUE_EnqueueLock(dObj->queue, (void*)pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error enqueing new job.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    dObj->txEnabled = true;
    SYS_INT_SourceEnable(INT_SOURCE_SPI_6_TRANSMIT);

    return (DRV_SPI_BUFFER_HANDLE)pJob;
}


DRV_SPI_BUFFER_HANDLE DRV_SPI1_BufferAddWrite2 ( void *txBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context, DRV_SPI_BUFFER_HANDLE * jobHandle )
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI1Obj;

    DRV_SPI_JOB_OBJECT * pJob = NULL;
    if (DRV_SPI_SYS_QUEUE_AllocElementLock(dObj->queue, (void **)&pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error trying to get a free entry.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    memset(pJob, 0, sizeof(DRV_SPI_JOB_OBJECT));
    pJob->txBuffer = txBuffer;
    pJob->dataLeftToTx = size;
    pJob->dummyLeftToRx = size;
    pJob->completeCB = completeCB;
    pJob->context = context;
    pJob->status = DRV_SPI_BUFFER_EVENT_PENDING;

    if (jobHandle != NULL )
    {
        *jobHandle = (DRV_SPI_BUFFER_HANDLE)pJob;
    }

    if (DRV_SPI_SYS_QUEUE_EnqueueLock(dObj->queue, (void*)pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error enqueing new job.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    dObj->txEnabled = true;
    SYS_INT_SourceEnable(INT_SOURCE_SPI_6_TRANSMIT);

    return (DRV_SPI_BUFFER_HANDLE)pJob;
}


DRV_SPI_BUFFER_HANDLE DRV_SPI1_BufferAddWriteRead2 ( void *txBuffer, size_t txSize, void *rxBuffer, size_t rxSize, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context, DRV_SPI_BUFFER_HANDLE * jobHandle )
{
    DRV_SPI_OBJ *dObj = (DRV_SPI_OBJ*)NULL;

    dObj = &gDrvSPI1Obj;

    DRV_SPI_JOB_OBJECT * pJob = NULL;
    if (DRV_SPI_SYS_QUEUE_AllocElementLock(dObj->queue, (void **)&pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error trying to get a free entry.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    memset(pJob, 0, sizeof(DRV_SPI_JOB_OBJECT));
    pJob->txBuffer = txBuffer;
    pJob->dataLeftToTx = txSize;
    pJob->rxBuffer = rxBuffer;
    pJob->dataLeftToRx = rxSize;

    if (jobHandle != NULL )
    {
        *jobHandle = (DRV_SPI_BUFFER_HANDLE)pJob;
    }
    if (rxSize > txSize)
    {
        pJob->dummyLeftToTx = rxSize - txSize;
    }
    if (txSize > rxSize)
    {
        pJob->dummyLeftToRx = txSize - rxSize;
    }
    pJob->completeCB = completeCB;
    pJob->context = context;
    pJob->status = DRV_SPI_BUFFER_EVENT_PENDING;

    if (DRV_SPI_SYS_QUEUE_EnqueueLock(dObj->queue, (void*)pJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
    {
        SYS_ASSERT(false, "\r\nSPI Driver: Error enqueing new job.");
        return (DRV_SPI_BUFFER_HANDLE)NULL;
    }

    dObj->txEnabled = true;
    SYS_INT_SourceEnable(INT_SOURCE_SPI_6_TRANSMIT);

    return (DRV_SPI_BUFFER_HANDLE)pJob;
}


DRV_SPI_BUFFER_HANDLE DRV_SPI1_BufferAddRead ( void *rxBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context)
{
    return DRV_SPI1_BufferAddRead2(rxBuffer, size, completeCB, context, NULL);
}

DRV_SPI_BUFFER_HANDLE DRV_SPI1_BufferAddWrite ( void *txBuffer, size_t size, DRV_SPI_BUFFER_EVENT_HANDLER completeCB, void * context )
{
    return DRV_SPI1_BufferAddWrite2(txBuffer, size, completeCB, context, NULL);
}

DRV_SPI_BUFFER_EVENT DRV_SPI1_BufferStatus ( DRV_SPI_BUFFER_HANDLE bufferHandle )
{
    DRV_SPI_JOB_OBJECT * pJob = (DRV_SPI_JOB_OBJECT *)bufferHandle;

    return pJob->status;
}



int32_t DRV_SPI1_ISRErrorTasks(struct DRV_SPI_OBJ * dObj)
{

    if (dObj->currentJob == NULL)
    {
        return 0;
    }

    register DRV_SPI_JOB_OBJECT * currentJob = dObj->currentJob;

    if (PLIB_SPI_ReceiverHasOverflowed(SPI_ID_6))
    {
        if (currentJob->completeCB != NULL)
        {
            (*currentJob->completeCB)(DRV_SPI_BUFFER_EVENT_ERROR, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
        }
        currentJob->status = DRV_SPI_BUFFER_EVENT_ERROR;
        if (dObj->operationEnded != NULL)
        {
            (*dObj->operationEnded)(DRV_SPI_BUFFER_EVENT_ERROR, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
        }
        if (DRV_SPI_SYS_QUEUE_FreeElement(dObj->queue, currentJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
        {
            SYS_ASSERT(false, "\r\nSPI Driver: Queue free element error.");
            return 0;
        }
        dObj->currentJob = NULL;
        PLIB_SPI_BufferClear(SPI_ID_6);
        PLIB_SPI_ReceiverOverflowClear (SPI_ID_6 );
        SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_ERROR);

    }
    return 0;
}

// *********************************************************************************************
// *********************************************************************************************
// Section: Old static driver compatibility APIs, these will be deprecated.
// *********************************************************************************************
// *********************************************************************************************
bool DRV_SPI1_ReceiverBufferIsFull(void)
{
    return (PLIB_SPI_ReceiverBufferIsFull(SPI_ID_6));
}

bool DRV_SPI1_TransmitterBufferIsFull(void)
{
    return (PLIB_SPI_TransmitBufferIsFull(SPI_ID_6));
}

int32_t DRV_SPI1_BufferAddWriteRead(const void * txBuffer, void * rxBuffer, uint32_t size)
{
    bool continueLoop;
    int32_t txcounter = 0;
    int32_t rxcounter = 0;
    uint8_t unitsTxed = 0;
    const uint8_t maxUnits = 16;
    do {
        continueLoop = false;
        unitsTxed = 0;
        if (PLIB_SPI_TransmitBufferIsEmpty(SPI_ID_6))
        {
            while (!PLIB_SPI_TransmitBufferIsFull(SPI_ID_6) && (txcounter < size) && unitsTxed != maxUnits)
            {
                PLIB_SPI_BufferWrite(SPI_ID_6, ((uint8_t*)txBuffer)[txcounter]);
                txcounter++;
                continueLoop = true;
                unitsTxed++;
            }
        }

        while (txcounter != rxcounter)
        {
            while (PLIB_SPI_ReceiverFIFOIsEmpty(SPI_ID_6));
            ((uint8_t*)rxBuffer)[rxcounter] = PLIB_SPI_BufferRead(SPI_ID_6);
            rxcounter++;
            continueLoop = true;
        }
        if (txcounter > rxcounter)
        {
            continueLoop = true;
        }
    }while(continueLoop);
    return txcounter;
}

