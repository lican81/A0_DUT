/* 
 * File:   dut_ports.h
 * Author: canli
 *
 * Created on July 15, 2019, 8:15 PM
 */

#ifndef DUT_PORTS_H
#define	DUT_PORTS_H


#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include "system_config.h"
#include "system_definitions.h"

#ifdef	__cplusplus
extern "C" {
#endif

    
void GPIO_Write( char portName, uint32_t portValue );
uint32_t GPIO_Read( char portName );
void GPIO_SlewRateSelect(char portName, uint16_t slewMask, uint8_t slewRate);

void GPIO_Pin_Set( char portName, uint16_t pos );
void GPIO_Pin_Clear( char portName, uint16_t pos );
void GPIO_Pin_Toggle( char portName, uint16_t pos );

//void ADDR_REGS_Set(PORTS_DATA_TYPE value);
//void DATAIN_Set(PORTS_DATA_TYPE value);

void ROW_COL_DATA_Set(PORTS_DATA_TYPE value);
void ROW_COL_BANK_Set(PORTS_DATA_TYPE value);
void ADC_FIFO_EN_Set(PORTS_DATA_TYPE value);
PORTS_DATA_TYPE ADC_OUT_Get(void);
//
//void DATAOUT_Set(PORTS_DATA_TYPE value);
//PORTS_DATA_TYPE DATAOUT_Get(void);
//void DATAOUT_DirectionInputSet(PORTS_DATA_MASK mask);
//void DATAOUT_DirectionOutputSet(PORTS_DATA_MASK mask);



#ifdef	__cplusplus
}
#endif

#endif	/* DUT_PORTS_H */

