/*******************************************************************************
  SPI Driver Functions for Static Driver Tasks Functions

  Company:
    Microchip Technology Inc.

  File Name:
    drv_spi_static_tasks.c

  Summary:
    SPI driver tasks functions

  Description:
    The SPI device driver provides a simple interface to manage the SPI
    modules on Microchip microcontrollers. This file contains implemenation
    for the SPI driver.

  Remarks:
  This file is generated from framework/driver/spi/template/drv_spi_static_tasks.c.ftl
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
#include "system_config.h"
#include "system_definitions.h"
#include "driver/spi/static/src/drv_spi_static_local.h"



int32_t DRV_SPI0_ISRMasterEBM8BitTasks ( struct DRV_SPI_OBJ * dObj )
{
    volatile bool continueLoop;
    /* Disable the interrupts */
    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_RECEIVE);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_TRANSMIT);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_1_ERROR);
    do {
        
        DRV_SPI_JOB_OBJECT * currentJob = dObj->currentJob;

        /* Check for a new task */
        if (dObj->currentJob == NULL)
        {
            if (DRV_SPI_SYS_QUEUE_Dequeue(dObj->queue, (void *)&(dObj->currentJob)) != DRV_SPI_SYS_QUEUE_SUCCESS)
            {
                SYS_ASSERT(false, "\r\nSPI Driver: Error in dequeing.");
                return 0;
            }
            if (dObj->currentJob == NULL)
            {
                dObj->txEnabled = false;
                return 0;
            }
            currentJob = dObj->currentJob;

            dObj->symbolsInProgress = 0;

            /* Call the operation starting function pointer.  This can be used to modify the slave select lines */
            if (dObj->operationStarting != NULL)
            {
                (*dObj->operationStarting)(DRV_SPI_BUFFER_EVENT_PROCESSING, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
            }

            /* List the new job as processing*/
            currentJob->status = DRV_SPI_BUFFER_EVENT_PROCESSING;
            if (currentJob->dataLeftToTx +currentJob->dummyLeftToTx > PLIB_SPI_RX_8BIT_FIFO_SIZE(SPI_ID_1))
            {
                PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_1, SPI_FIFO_INTERRUPT_WHEN_TRANSMIT_BUFFER_IS_1HALF_EMPTY_OR_MORE);
                PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_1, SPI_FIFO_INTERRUPT_WHEN_RECEIVE_BUFFER_IS_1HALF_FULL_OR_MORE);
            }
            /* Flush out the Receive buffer */
            PLIB_SPI_BufferClear(SPI_ID_1);
        }


        continueLoop = false;
        
        /* Execute the sub tasks */
            if
            (currentJob->dataLeftToTx +currentJob->dummyLeftToTx != 0)
        {
            DRV_SPI0_MasterEBMSend8BitISR(dObj);
        }
        
        DRV_SPI0_ISRErrorTasks(dObj);
        
        /* Figure out how many bytes are left to be received */
        volatile size_t bytesLeft = currentJob->dataLeftToRx + currentJob->dummyLeftToRx;
        
        // Check to see if we have any data left to receive and update the bytes left.
        if (bytesLeft != 0)
        {
            DRV_SPI0_MasterEBMReceive8BitISR(dObj);
            bytesLeft = currentJob->dataLeftToRx + currentJob->dummyLeftToRx;
        }
        if (bytesLeft == 0)
        {
                    // Disable the interrupt, or more correctly don't re-enable it later*/
                    dObj->rxEnabled = false;
                    /* Job is complete*/
                    currentJob->status = DRV_SPI_BUFFER_EVENT_COMPLETE;
                    /* Call the job complete call back*/
                    if (currentJob->completeCB != NULL)
                    {
                        (*currentJob->completeCB)(DRV_SPI_BUFFER_EVENT_COMPLETE, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
                    }

                    /* Call the operation complete call back.  This is different than the
                       job complete callback.  This can be used to modify the Slave Select line.*/

                    if (dObj->operationEnded != NULL)
                    {
                        (*dObj->operationEnded)(DRV_SPI_BUFFER_EVENT_COMPLETE, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
                    }

                    /* Return the job back to the free queue*/
                    if (DRV_SPI_SYS_QUEUE_FreeElement(dObj->queue, currentJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
                    {
                        SYS_ASSERT(false, "\r\nSPI Driver: Queue free element error.");
                        return 0;
                    }
                    /* Clean up */
                    dObj->currentJob = NULL;
                    if (!DRV_SPI_SYS_QUEUE_IsEmpty(dObj->queue))
                    {
                        continueLoop = true;
                        continue;
                    }
                    else
                    {
                        break;
                    }
                }


        /* Check to see if the interrupts would fire again if so just go back into
           the loop instead of suffering the interrupt latency of exiting and re-entering*/
        if (dObj->currentJob != NULL)
        {   
            /* Clear the Interrupts */
            SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_RECEIVE);
            SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_TRANSMIT);
            SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_ERROR);
            /* Interrupts should immediately become active again if they're in a fired condition */
            if ((SYS_INT_SourceStatusGet(INT_SOURCE_SPI_1_RECEIVE)) ||
                (SYS_INT_SourceStatusGet(INT_SOURCE_SPI_1_TRANSMIT)) ||
                (SYS_INT_SourceStatusGet(INT_SOURCE_SPI_1_ERROR)))
            {
                /* Interrupt would fire again anyway so we should just go back to the start*/
                continueLoop = true;
                continue;
            }
             /* If we're here then we know that the interrupt should not be firing again immediately, so re-enable them and exit*/
                SYS_INT_SourceEnable(INT_SOURCE_SPI_1_RECEIVE);
                SYS_INT_SourceEnable(INT_SOURCE_SPI_1_TRANSMIT);
            return 0;
        }

    } while(continueLoop);
    /* if we're here it means that we have no more jobs in the queue, tx and rx interrupts will be re-enabled by the BufferAdd* functions*/
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_RECEIVE);
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_1_TRANSMIT);
    return 0;
}


int32_t DRV_SPI1_ISRMasterEBM8BitTasks ( struct DRV_SPI_OBJ * dObj )
{
    volatile bool continueLoop;
    /* Disable the interrupts */
    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_RECEIVE);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_TRANSMIT);
    SYS_INT_SourceDisable(INT_SOURCE_SPI_6_ERROR);
    do {
        
        DRV_SPI_JOB_OBJECT * currentJob = dObj->currentJob;

        /* Check for a new task */
        if (dObj->currentJob == NULL)
        {
            if (DRV_SPI_SYS_QUEUE_Dequeue(dObj->queue, (void *)&(dObj->currentJob)) != DRV_SPI_SYS_QUEUE_SUCCESS)
            {
                SYS_ASSERT(false, "\r\nSPI Driver: Error in dequeing.");
                return 0;
            }
            if (dObj->currentJob == NULL)
            {
                dObj->txEnabled = false;
                return 0;
            }
            currentJob = dObj->currentJob;

            dObj->symbolsInProgress = 0;

            /* Call the operation starting function pointer.  This can be used to modify the slave select lines */
            if (dObj->operationStarting != NULL)
            {
                (*dObj->operationStarting)(DRV_SPI_BUFFER_EVENT_PROCESSING, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
            }

            /* List the new job as processing*/
            currentJob->status = DRV_SPI_BUFFER_EVENT_PROCESSING;
            if (currentJob->dataLeftToTx +currentJob->dummyLeftToTx > PLIB_SPI_RX_8BIT_FIFO_SIZE(SPI_ID_6))
            {
                PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_6, SPI_FIFO_INTERRUPT_WHEN_TRANSMIT_BUFFER_IS_1HALF_EMPTY_OR_MORE);
                PLIB_SPI_FIFOInterruptModeSelect(SPI_ID_6, SPI_FIFO_INTERRUPT_WHEN_RECEIVE_BUFFER_IS_1HALF_FULL_OR_MORE);
            }
            /* Flush out the Receive buffer */
            PLIB_SPI_BufferClear(SPI_ID_6);
        }


        continueLoop = false;
        
        /* Execute the sub tasks */
            if
            (currentJob->dataLeftToTx +currentJob->dummyLeftToTx != 0)
        {
            DRV_SPI1_MasterEBMSend8BitISR(dObj);
        }
        
        DRV_SPI1_ISRErrorTasks(dObj);
        
        /* Figure out how many bytes are left to be received */
        volatile size_t bytesLeft = currentJob->dataLeftToRx + currentJob->dummyLeftToRx;
        
        // Check to see if we have any data left to receive and update the bytes left.
        if (bytesLeft != 0)
        {
            DRV_SPI1_MasterEBMReceive8BitISR(dObj);
            bytesLeft = currentJob->dataLeftToRx + currentJob->dummyLeftToRx;
        }
        if (bytesLeft == 0)
        {
                    // Disable the interrupt, or more correctly don't re-enable it later*/
                    dObj->rxEnabled = false;
                    /* Job is complete*/
                    currentJob->status = DRV_SPI_BUFFER_EVENT_COMPLETE;
                    /* Call the job complete call back*/
                    if (currentJob->completeCB != NULL)
                    {
                        (*currentJob->completeCB)(DRV_SPI_BUFFER_EVENT_COMPLETE, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
                    }

                    /* Call the operation complete call back.  This is different than the
                       job complete callback.  This can be used to modify the Slave Select line.*/

                    if (dObj->operationEnded != NULL)
                    {
                        (*dObj->operationEnded)(DRV_SPI_BUFFER_EVENT_COMPLETE, (DRV_SPI_BUFFER_HANDLE)currentJob, currentJob->context);
                    }

                    /* Return the job back to the free queue*/
                    if (DRV_SPI_SYS_QUEUE_FreeElement(dObj->queue, currentJob) != DRV_SPI_SYS_QUEUE_SUCCESS)
                    {
                        SYS_ASSERT(false, "\r\nSPI Driver: Queue free element error.");
                        return 0;
                    }
                    /* Clean up */
                    dObj->currentJob = NULL;
                    if (!DRV_SPI_SYS_QUEUE_IsEmpty(dObj->queue))
                    {
                        continueLoop = true;
                        continue;
                    }
                    else
                    {
                        break;
                    }
                }


        /* Check to see if the interrupts would fire again if so just go back into
           the loop instead of suffering the interrupt latency of exiting and re-entering*/
        if (dObj->currentJob != NULL)
        {   
            /* Clear the Interrupts */
            SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_RECEIVE);
            SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_TRANSMIT);
            SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_ERROR);
            /* Interrupts should immediately become active again if they're in a fired condition */
            if ((SYS_INT_SourceStatusGet(INT_SOURCE_SPI_6_RECEIVE)) ||
                (SYS_INT_SourceStatusGet(INT_SOURCE_SPI_6_TRANSMIT)) ||
                (SYS_INT_SourceStatusGet(INT_SOURCE_SPI_6_ERROR)))
            {
                /* Interrupt would fire again anyway so we should just go back to the start*/
                continueLoop = true;
                continue;
            }
             /* If we're here then we know that the interrupt should not be firing again immediately, so re-enable them and exit*/
                SYS_INT_SourceEnable(INT_SOURCE_SPI_6_RECEIVE);
                SYS_INT_SourceEnable(INT_SOURCE_SPI_6_TRANSMIT);
            return 0;
        }

    } while(continueLoop);
    /* if we're here it means that we have no more jobs in the queue, tx and rx interrupts will be re-enabled by the BufferAdd* functions*/
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_RECEIVE);
    SYS_INT_SourceStatusClear(INT_SOURCE_SPI_6_TRANSMIT);
    return 0;
}


