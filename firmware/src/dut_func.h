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

typedef enum
{
	PLANE_VPP=0,
    DAC_VREF_ARRAY= 1,
    P_VREF_TIA=2,
    DAC_VREF_HI_CMP=3,
    P_VREF_SH=4,
    DAC_VP_PAD=5,
    P_TVDD=6,
    P_VAGC_0=7,
    P_VAGC_1=8,
    P_ADC_EXT_TEST_IN=9,
    P_AMP_VREF=10,
    P_AMP_INPUT=11,
    DAC_SPARE1=12,
    DAC_SPARE2=13,
    DAC_DRIVE_VN=14,
    DAC_SCHOTTKY=15

} DAC_CH;


void BSP_DelayUs(double microseconds);
void I2C_Write(uint8_t addr, uint32_t data);


void pads_default();


void gen_data_row(uint8_t row, uint16_t * data_row);
void gen_data_col(uint8_t col, uint16_t * data_col);
void gen_data_col_row(uint8_t col, uint8_t row, uint16_t * data_col_row);
uint8_t get_fifo_en(uint8_t arr, uint8_t col);
uint8_t get_fifo_ch(uint8_t arr, uint8_t col);
void load_vectors(uint8_t arr, uint16_t * vector, bool is_row);

void download_fifo( uint8_t fifo_en, uint16_t * data );
int dac_set( DAC_CH ch, uint16_t value);
int serial_set(uint8_t addr,  int size, uint8_t * buffer);
int dac_init(uint8_t span);

uint16_t A0_read_single(uint8_t arr, uint8_t row, uint8_t col, int mode);
void A0_read_batch( uint8_t arr, uint16_t *read_buffer, int mode, uint32_t Tdly );
void A0_read_batch2( uint8_t arr, uint16_t *read_buffer, int mode );
void A0_dpe_batch( uint8_t arr, int len, int mode, uint32_t Tdly, uint8_t *input_buffer, uint16_t *output_buffer);

int A0_write_single(uint8_t arr, uint8_t row, uint8_t col, 
                        uint16_t Vwrite_raw, uint16_t Vgate_raw, 
                        uint8_t is_set);

int A0_write_batch(uint8_t arr, uint8_t mode, uint16_t * Vwrite_raw, uint16_t * Vgate_raw);

#ifdef	__cplusplus
}
#endif

#endif	/* DUT_FUNC_H */

