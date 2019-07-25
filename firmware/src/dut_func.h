/* 
 * File:   dut_func.h
 * Author: canli
 *
 * Created on July 19, 2019, 1:27 PM
 */

#ifndef DUT_FUNC_H
#define	DUT_FUNC_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include "system_config.h"
#include "system_definitions.h"


#ifdef	__cplusplus
extern "C" {
#endif

    
#define READ_CORE_TIMER()                 _CP0_GET_COUNT()          // Read the MIPS Core Timer

void BSP_DelayUs(uint16_t microseconds);
void I2C_Write(uint8_t addr, uint32_t data);


#ifdef	__cplusplus
}
#endif

#endif	/* DUT_FUNC_H */

