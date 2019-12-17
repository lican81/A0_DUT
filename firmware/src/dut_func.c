/*
 * COPYRIGHT Hewlett Packard Labs
 * 
 * created by Can Li, can.li@hpe.com
 * 
 */


#include "dut_func.h"

void BSP_DelayUs(double microseconds)
{
    /**
     * Pause for certain microseconds
     * 
     * @param microseconds number of microseconds to pause
     * @return NA
     * 
     */

    uint32_t time;

    //SYS_PRINT("\t [D] T = %f\r\n", microseconds);
    
    time = READ_CORE_TIMER(); // Read Core Timer    
    //SYS_PRINT("\t [D] T1 = %d, ", time);
    time += (SYS_CLK_FREQ / 2 / 1000000) * microseconds; // calc the Stop Time    
    //SYS_PRINT("T2 = %d\r\n", time);
    
    while ((int32_t)(time - READ_CORE_TIMER()) > 0){};    
}

void I2C_Write(uint8_t addr, uint32_t data)
{
    SYS_PRINT("\t I2C: Sending data %x to addr=%x\r\n \t I2C data: ", data, addr);
    
    // One clock period is roughly T_DLY * 4
    // T_DLY = 5 is roughly 50 kHz
    
    uint16_t T_DLY = 5; // us
    uint8_t i =0;
    
    data = ( ( data & 0xff )<<1 ) | ( (addr & 0xc7f) << 11 );
    
    PICIC2_SCLOn();
    PICIC2_SDAOn();
    
    BSP_DelayUs(T_DLY);
            
    PICIC2_SDAOff();
    
    BSP_DelayUs(T_DLY);
    
    for (i=17; i--; i>=0) {
        if (data & (1<<i) ) {
            PICIC2_SDAOn();
            SYS_PRINT("1");
        } else {
            PICIC2_SDAOff();
            SYS_PRINT("0");
        }
        
        BSP_DelayUs(T_DLY);
        PICIC2_SCLOn();
        BSP_DelayUs(T_DLY * 2);
        PICIC2_SCLOff();
        BSP_DelayUs(T_DLY);
    }
    
    BSP_DelayUs(T_DLY);
    PICIC2_SCLOn();
    BSP_DelayUs(T_DLY);
    PICIC2_SDAOn();
      
    SYS_PRINT("\r\n I2C: Completed! \r\n");
}

void pads_default() {
    /**
     Set all the pads to a default state
    */
    CONNECT_COLUMN_TOff();
    BSP_DelayUs(1);
    
    ROW_COL_DATA_Set(0x0);
    COL_ROW_SELOff();
    ROW_COL_BANK_Set(0x0);
    
    LATCH_CLK_DATAOff();
    READ_BITOff();
    READ_DPEOff();
    COL_WRITE_CONNECTOff();
    CONNECT_TIAOff();
    DPE_PULSEOff();
    AGC_PULSEOff();
    DPE_INTERNAL_ENOff();
    AGC_INTERNAL_ENOff();
    DPE_EXT_OVERRIDE_ENOff();
    DPE_EXT_PULSEOff();
    DPE_EXT_SHOff();
    WRITE_FWDOff();
    WRT_INTERNAL_ENOff();
    WRT_PULSEOff();
    WRITE_SEL_EXTOff();
    WRITE_ADD_CAPOff();
    ADC_FIFO_ADVANCEOff();
    
    ADC_FIFO_EN_Set(0x0);
    
    ADC_SEL_EXTERNALOff();
//    SERIAL_BUS_INOff();
//    SERIAL_CK_INOff();
    UPDATE_TIA_CONFOff();
    SERIAL_CHAIN_SEL_0On();
    SERIAL_CHAIN_SEL_1On();
}


void gen_data_row(uint8_t row, uint16_t * data_row) {
    /**
     * Generate the row data to load
     * 
     * @param row The row to enable
     * @param data_row[4] The data buffer to be loaded. .
     * 
     * @return NA
     * 
     */
    uint8_t ROW_DICT[4] = {2,0,1,3};

    uint8_t bank_row;
    uint8_t bit_pos;

    // Row data
    bank_row = ROW_DICT[row/16];
    bit_pos = row%16/2;
    if (row<32) {
        if (row%2) {
            data_row[bank_row] |= ( 0x1<<(bit_pos+8) );
        } else {
            data_row[bank_row] |= ( 0x1<<(bit_pos ) );
        }
    } else {
        if (row%2) {
            data_row[bank_row] |= ( 0x1<<(15-bit_pos) );
        } else {
            data_row[bank_row] |= ( 0x1<<(7-bit_pos) );
        }
    }
}

void gen_data_col(uint8_t col, uint16_t * data_col) {
    /**
     * Generate the col data to load
     * 
     * @param col The col to enable
     * @param data_col[4] The data buffer to be loaded. .
     * 
     * @return NA
     * 
     */
    
    uint8_t bank_col;

    bank_col = col/32 * 2 + col%2;
    if (col<32) {
        data_col[bank_col] |= ( 0x1<<(15-col/2));
    } else {
        data_col[bank_col] |= ( 0x1<<((col-32)/2));
    }
}

void gen_data_row_col(uint8_t row, uint8_t col, uint16_t * data_col_row) {
    /**
     * Generate the row and col data to load
     * 
     * @param col The col to enable
     * @param row The row to enable
     * @param data_col[8] The data buffer to be loaded. .
     * 
     * @return NA
     * 
     */
    
    gen_data_row(row, data_col_row);
    gen_data_col(col, data_col_row+4);
}

uint8_t get_fifo_en(uint8_t arr, uint8_t col) {
    /*
     * Return the fifo_en
     */
    
    return (2-arr)*2 + col/32 + col%2*6;
}

uint8_t get_fifo_ch(uint8_t arr, uint8_t col) {
    /*
     * Return the fifo_ch
     */
    
    if (col<32) {
        return (col/16)*8 + (7-col%16/2);
    } else {
        return (3-col/16)*8 + col%16/2;
    }
}


void load_vectors(uint8_t arr, uint16_t * vector, bool is_row) {
    /**
     * Load row or column vectors
     * 
     * @param arr The array number
     * @param data_row[4] The data buffer to be loaded.
     * @param is_row Load row vector if True.
     * 
     * @return NA
     * 
     */
    
    if (arr<0 && arr>=4) {
        SYS_PRINT("\t Wrong array number!! arr = %d\r\n", arr);
        return;
    }
    
    LATCH_CLK_DATAOff();
    
    ARRAY_EN_Set( 0x1 << arr );
    
    if (is_row) {
        COL_ROW_SELOff();
    } else {
        COL_ROW_SELOn();
    }
        
    int n_bank = 0;
    for (n_bank=0; n_bank<4; n_bank++) {
        ROW_COL_BANK_Set( 0x1<<n_bank );
        ROW_COL_DATA_Set( vector[n_bank] );
        
        BSP_DelayUs(0.1);
        LATCH_CLK_DATAOn();
        BSP_DelayUs(0.1);
        LATCH_CLK_DATAOff();
    }
}

void download_fifo( uint8_t fifo_en, uint16_t * data ) {
    /*
     * Download FIFO data
     * 
     * @param addr The FIFO address, 0-11
     * @param data The data buffer for the result
     * 
     */
    
    int FIFO_DEPTH = 16;
    int i;
    
    ADC_FIFO_ADVANCEOff();
    ADC_FIFO_EN_Set( fifo_en );
    
    for (i=0; i<FIFO_DEPTH; i++) {
        data[i] = ADC_OUT_Get();
        
        // Strobe 
        BSP_DelayUs(0.5);
        ADC_FIFO_ADVANCEOn();
        BSP_DelayUs(0.5);
        ADC_FIFO_ADVANCEOff();
        BSP_DelayUs(0.5);
    }
}

/*
 * All the functions start with A0 are 4xx commands
 */

void reset_dpe() {
    NRESET_DPE_ENGINEOff();
    BSP_DelayUs(1);
    NRESET_DPE_ENGINEOn();
}

uint16_t A0_read_single(uint8_t arr, uint8_t row, uint8_t col, int mode) {
    /*
     * Read a single device
     * 
     */
    
    uint16_t data_row[4];
    uint16_t data_col[4];
    
    uint16_t res_buff[16];
    
    uint8_t fifo_en, fifo_ch;
    int i;
    
    for (i=0; i<4; i++) {
        data_row[i] = 0;
        data_col[i] = 0;
    }
    
    gen_data_row(row, data_row);
    gen_data_col(col, data_col);
    
    load_vectors(arr, data_row, true);
    load_vectors(arr, data_col, false);
    
    reset_dpe();
    
    if (mode==0) {
        DPE_INTERNAL_ENOn();
    } else {
        AGC_INTERNAL_ENOn();
    }
    
    READ_BITOn();
    READ_DPEOff();
    
    NFORCE_SAFE_Set( 0x1 << arr );
    
    CONNECT_TIAOn();
    CONNECT_COLUMN_TOn();
    
    if (mode==0) {
        DPE_PULSEOn();
        BSP_DelayUs(0.2);
        DPE_PULSEOff();
    } else {
        AGC_PULSEOn();
        BSP_DelayUs(0.2);
        AGC_PULSEOff();
    }
    
    fifo_en = get_fifo_en(arr, col);
    fifo_ch = get_fifo_ch(arr, col);
    
    //SYS_PRINT("\t FIFO_%d, ch=%d\r\n", fifo_en, fifo_ch);
//    BSP_DelayUs(5.2);
    
    while ( ADC_DONEStateGet() == 0) {
//        SYS_PRINT("\t Wait for ADC_DONE\r\n");
    }
    BSP_DelayUs(0.2);
    
    download_fifo( fifo_en, res_buff);
//
//    CONNECT_COLUMN_TOff();
//    CONNECT_TIAOff();
//    NFORCE_SAFE_Set( 0 );
//    READ_BITOff();
//    
    return res_buff[fifo_ch];
}

uint16_t A0_read_single_test(uint8_t arr, uint8_t row, uint8_t col, int mode, 
                            uint32_t T1, uint32_t T2, uint32_t T3, uint32_t Nt ) {
    /*
     * Read a single device
     * 
     */
    
    uint16_t data_row[4];
    uint16_t data_col[4];
    
    uint16_t res_buff[16];
    
    uint8_t fifo_en, fifo_ch;
    int i;
    
    // for (i=0; i<4; i++) {
    //     data_row[i] = 0;
    //     data_col[i] = 0;
    // }
    
    // gen_data_row(row, data_row);
    // gen_data_col(col, data_col);
    
    // load_vectors(arr, data_row, true);
    // load_vectors(arr, data_col, false);

    // BSP_DelayUs(T1);    

//    BSP_DelayUs(Nt*2 * 0.02);
//    
//    if (mode==0) {
//        DPE_INTERNAL_ENOn();
//    } else {
//        AGC_INTERNAL_ENOn();
//    }
    
//    READ_BITOn();
//    READ_BITOff();
    
//    BSP_DelayUs(Nt*1 * 0.02);
//    NFORCE_SAFE_Set( 0x1 << arr );
//    BSP_DelayUs(Nt*1 * 0.02);
    
//    CONNECT_TIAOn();
//    BSP_DelayUs(Nt*2 * 0.02);
//    CONNECT_COLUMN_TOn();
//    BSP_DelayUs(Nt*2 * 0.02);
    
    reset_dpe();
    BSP_DelayUs(T1);

    if (mode==0) {
        DPE_PULSEOn();
        BSP_DelayUs(Nt*2 * 0.02);
        DPE_PULSEOff();
    } else {
        AGC_PULSEOn();
        BSP_DelayUs(Nt*2 * 0.02);
        AGC_PULSEOff();
    }
    
    fifo_en = get_fifo_en(arr, col);
    fifo_ch = get_fifo_ch(arr, col);
    
    //SYS_PRINT("\t FIFO_%d, ch=%d\r\n", fifo_en, fifo_ch);
    BSP_DelayUs(T2);
    
    while ( ADC_DONEStateGet() == 0) {
//        SYS_PRINT("\t Wait for ADC_DONE\r\n");
    }
    BSP_DelayUs(Nt*2 * 0.02);
    
    download_fifo( fifo_en, res_buff);

//    CONNECT_COLUMN_TOff();
//    BSP_DelayUs(Nt*2 * 0.02);
//    CONNECT_TIAOff();
//    BSP_DelayUs(Nt*2 * 0.02);
//    NFORCE_SAFE_Set( 0 );
//    BSP_DelayUs(Nt*2 * 0.02);
//    READ_BITOff();

    BSP_DelayUs(T3);
    
    return res_buff[fifo_ch];
}

void A0_read_batch( uint8_t arr, uint16_t *read_buffer, int mode, uint32_t Tdly) {
    /*
     * Read the entire array.
     * 
     * @param read_buffer The raw adc buffer for the readout result
     * @param Tdly          The pause time between reads, in microseconds
     * 
     */
    int r, c; // row, column

    for (r=0; r<64; r++) {
        for (c=0; c<64; c++) {
            read_buffer[ r*64 + c] = A0_read_single(arr, r, c, mode);
            BSP_DelayUs(Tdly);
        }
    }
}


void A0_read_batch2( uint8_t arr, uint16_t *read_buffer, int mode ) {
    /*
     * Read the entire array.
     * 
     * @param read_buffer The raw adc buffer for the readout result
     * 
     */
    int i, r, c; // row, column

    uint16_t data_row[4];
    uint16_t res_buff[16];
    
    uint8_t fifo_en, fifo_ch;
    
    if (mode==0) {
        DPE_INTERNAL_ENOn();
    } else {
        AGC_INTERNAL_ENOn();
    }
    
    READ_BITOn();
    READ_BITOff();
    
    NFORCE_SAFE_Set( 0x1 << arr );

    for (c=0; c<64; c++) {
        uint16_t data_col[4];

        for (i=0; i<4; i++) {
            data_col[i] = 0;
        }

        gen_data_col(c, data_col);
        load_vectors(arr, data_col, false);

        CONNECT_TIAOn();
        CONNECT_COLUMN_TOn();

        fifo_en = get_fifo_en(arr, c);
        fifo_ch = get_fifo_ch(arr, c);

        for (r=0; r<64; r++) {

            for (i=0; i<4; i++) {
                data_row[i] = 0;
            }
            
            gen_data_row(r, data_row);   
            
            load_vectors(arr, data_row, true);
            reset_dpe();
 
            if (mode==0) {
                DPE_PULSEOn();
                BSP_DelayUs(0.2);
                DPE_PULSEOff();
            } else {
                AGC_PULSEOn();
                BSP_DelayUs(0.2);
                AGC_PULSEOff();
            }
            
            //SYS_PRINT("\t FIFO_%d, ch=%d\r\n", fifo_en, fifo_ch);
            
            while ( ADC_DONEStateGet() == 0) {
        //        SYS_PRINT("\t Wait for ADC_DONE\r\n");
            }
            BSP_DelayUs(0.2);
            
            download_fifo( fifo_en, res_buff);
            read_buffer[ r*64 + c] = res_buff[fifo_ch];
        }
    }
}


// void A0_dpe_single( uint_8 arr, )

void A0_dpe_batch( uint8_t arr, int len, int mode, uint32_t Tdly, uint8_t *input_buffer, uint16_t *output_buffer) {
    /*
     * Perform vector-matrix multiplication
     * 
     * @param arr The array number: 0-2
     * @param len The number of vectors
     * @param mode Read mode, bit 1: 0 -> ground unselected wires; 1->float unselected wires
     *                        bit 2: 0 -> normal reading;  1-> autogain
     * @param input_buffer The input vectors, each vector is composed of 
     *                      eight bytes (64 bits)
     * @param output_buffer The multiplication results
     */

    int i_vector = 0;

    // for (i=0; i<portValue; i++) {
    //     SYS_PRINT("\t i=%d,  data=0x %x\r\n", i, ptr[i]);
    // }

    uint16_t data_row[4];
    uint16_t fifo_buff[12][16];

    uint8_t fifo_en_list[4] = {(2-arr)*2, (2-arr)*2+6, (2-arr)*2+1, (2-arr)*2+7};

    // TODO Select only part of the columns
    // Attach all TIAs to the columns
//    uint16_t data_col[4] = {0xffff, 0xffff, 0xffff, 0xffff};
//    load_vectors(arr, data_col, false);
    
    int i, j;

    for (i_vector=0; i_vector<len; i_vector++) {
    
        for (i=0; i<4; i++) {
            data_row[i] = 0;
        }
        
        for (i=0; i<64; i++) {
            if (input_buffer[7-(i/8)] & (0x1<<i%8) ) {
                gen_data_row(i, data_row);
            } 
        }

        input_buffer += 8;
        load_vectors(arr, data_row, true);

        reset_dpe();
        
        if ( (mode&0x2) ==0) {
            DPE_INTERNAL_ENOn();
        } else {
            AGC_INTERNAL_ENOn();
        }

        READ_BITOn();
        
        if ( (mode&0x1) ==0) {
            READ_DPEOn();
        } else {
            READ_DPEOff();
        }
        
        NFORCE_SAFE_Set( 0x1 << arr );
        
        CONNECT_TIAOn();
        CONNECT_COLUMN_TOn();
        
        if ( (mode&0x2) ==0) {
            DPE_PULSEOn();
            BSP_DelayUs(0.2);
            DPE_PULSEOff();
        } else {
            AGC_PULSEOn();
            BSP_DelayUs(0.2);
            AGC_PULSEOff();
        }
        
        //SYS_PRINT("\t FIFO_%d, ch=%d\r\n", fifo_en, fifo_ch);
        
        while ( ADC_DONEStateGet() == 0) {
    //        SYS_PRINT("\t Wait for ADC_DONE\r\n");
        }
        BSP_DelayUs(0.2);

        for (i=0; i<4; i++) {
            download_fifo( fifo_en_list[i], fifo_buff[ fifo_en_list[i] ]);
        }
        
        for (i=0; i<4; i++) {
            for (j=0; j<16; j++) {
                uint8_t col=j+16*i;
                
                output_buffer[j] = fifo_buff[get_fifo_en(arr, col)][ get_fifo_ch(arr, col) ];
            }

            output_buffer += 16;
        }

        BSP_DelayUs(Tdly);

    } //end for i_vector
    
    CONNECT_COLUMN_TOff();
    CONNECT_TIAOff();
    NFORCE_SAFE_Set( 0 );
    READ_BITOff();
}


int dac_set( DAC_CH ch, uint16_t value) {
    /*
     * Set the DAC value. It is pre-configured beforehand. 
     * 
     * @param ch The DAC channel
     * @param value The raw DAC value in 16-bit binaries
     */

    PIC_CSOn();
    PIC_CSOff();

    uint32_t cmd = (0x3<<20) | (ch<<16) | value;
    
    uint8_t cmd_b[4];
    cmd_b[3] = (uint8_t) (cmd >>  0u);
    cmd_b[2] = (uint8_t) (cmd >>  8u);
    cmd_b[1] = (uint8_t) (cmd >> 16u);
    cmd_b[0] = (uint8_t) (cmd >> 24u);

//    SYS_PRINT("\t DAC cmd=%x\r\n", cmd);
//    SYS_PRINT("\t DAC re cmd=%x %x %x %x\r\n", cmd_b[0], cmd_b[1] , cmd_b[2] , cmd_b[3] );
    
    DRV_SPI_BUFFER_HANDLE spi_handle = DRV_SPI1_BufferAddWrite( cmd_b, 4, NULL, NULL); 

    while (DRV_SPI0_BufferStatus(spi_handle) != DRV_SPI_BUFFER_EVENT_COMPLETE) {
//        SYS_PRINT("\t Wait spi (DAC) to complete...\r\n");
    }
    
//    BSP_DelayUs(10);

    PIC_CSOn();
    return 0;
}

int dac_init(uint8_t span) {
    /*
     * Initialize the DAC
     * 
     * @param span The span code
     */
    
    PIC_LDACOn();
    PIC_TGPOn();

    PIC_CLROff();
    BSP_DelayUs(1);
    PIC_CLROn();

    PIC_CSOn();
    PIC_CSOff();

    // Hardcoded to 0-5 V for now
    // span = 0;
    
    uint32_t cmd = (0xe<<20) | span;

    uint8_t cmd_b[4];
    cmd_b[3] = (uint8_t) (cmd >>  0u);
    cmd_b[2] = (uint8_t) (cmd >>  8u);
    cmd_b[1] = (uint8_t) (cmd >> 16u);
    cmd_b[0] = (uint8_t) (cmd >> 24u);

    SYS_PRINT("\t DAC cmd=%x, span=%x\r\n", cmd, span);
    SYS_PRINT("\t DAC re cmd=%x %x %x %x\r\n", cmd_b[0], cmd_b[1] , cmd_b[2] , cmd_b[3] );
    
    DRV_SPI_BUFFER_HANDLE spi_handle = DRV_SPI1_BufferAddWrite( cmd_b, 4, NULL, NULL); 

    while (DRV_SPI0_BufferStatus(spi_handle) != DRV_SPI_BUFFER_EVENT_COMPLETE) {
        SYS_PRINT("\t Wait spi (DAC) to complete...\r\n");
    }
    
    PIC_CSOn();
    return 0;
}

int serial_set(uint8_t addr,  int size, uint8_t * buffer) {
    /*
     * Send the scan_chain data to the A0 chip
     * 
     * @param addr The scan chain address
     * @param size The size of the data to send, in bytes
     * @param buffer The data to send
     */

    // Setting the address
    switch (addr) {
        case 0b00:
            SERIAL_CHAIN_SEL_0Off();
            SERIAL_CHAIN_SEL_1Off();
            break;
        case 0b01:
            SERIAL_CHAIN_SEL_0On();
            SERIAL_CHAIN_SEL_1Off();
            break;
        case 0b10:
            SERIAL_CHAIN_SEL_0Off();
            SERIAL_CHAIN_SEL_1On();
            break;
        default:
            SERIAL_CHAIN_SEL_0On();
            SERIAL_CHAIN_SEL_1On();
            SYS_PRINT("\t Wrong address!!!");
    }
    
    DRV_SPI_BUFFER_HANDLE spi_handle = DRV_SPI0_BufferAddWrite( buffer, size, NULL, NULL);

    while (DRV_SPI0_BufferStatus(spi_handle) != DRV_SPI_BUFFER_EVENT_COMPLETE) {
    }

    // Clear the address to a safe state
    SERIAL_CHAIN_SEL_0On();
    SERIAL_CHAIN_SEL_1On();
}


int A0_write_single_ext(uint8_t arr, uint8_t row, uint8_t col, 
                        uint16_t Vwrite_raw, uint16_t Vgate_raw, uint16_t Vzero_raw,
                        uint8_t is_set, uint32_t Twidth) {
    /*
     * Program a single device
     * 
     */
    uint16_t data_row[4];
    uint16_t data_col[4];
    
    uint8_t fifo_en, fifo_ch;
    int i;
    
    for (i=0; i<4; i++) {
        data_row[i] = 0;
        data_col[i] = 0;
    }
    
    gen_data_row(row, data_row);
    gen_data_col(col, data_col);
    
    load_vectors(arr, data_row, true);
    load_vectors(arr, data_col, false);
    
    WRT_INTERNAL_ENOff();
    WRITE_ADD_CAPOff();
    WRITE_SEL_EXTOn();

    reset_dpe();

    // Clear DAC
    dac_set( P_TVDD, Vzero_raw);
    dac_set( DAC_VP_PAD, Vzero_raw);
    BSP_DelayUs(1);
    
    NFORCE_SAFE_Set( 0x1 << arr );

    if (is_set==true) {
        WRITE_FWDOn();
        ROW_WRITE_CONNECTOn();
    } else {
        WRITE_FWDOff();
        COL_WRITE_CONNECTOn();
    }
    
    dac_set( P_TVDD, Vgate_raw);
    dac_set( DAC_VP_PAD, Vwrite_raw);
    
    //wait for DAC settling
    BSP_DelayUs(10);
    
    CONNECT_COLUMN_TOn();
    BSP_DelayUs(Twidth);
    CONNECT_COLUMN_TOff();
    ROW_WRITE_CONNECTOff();
    NFORCE_SAFE_Set( 0x0 );
    
    // Clear DAC
    dac_set( DAC_VP_PAD, Vzero_raw);
    dac_set( P_TVDD, Vzero_raw);
    
    return 0;
}

int A0_write_batch_ext(uint8_t arr, uint8_t mode, uint16_t * Vwrite_raw, uint16_t * Vgate_raw, 
                        uint16_t Vzero_raw, uint32_t Twidth) {
  
    SYS_PRINT("\tStart Prog.\r\n", arr, mode);
    
    int i, j;
    
    // for (i=0; i<4; i++) {
    //     SYS_PRINT("[DW] r=%d | ", i*16);
    //     for (j=0; j<4; j++) {
    //         SYS_PRINT("%x, ", Vwrite_raw[(i*16)*64 + j*16]);
    //     }
    //     SYS_PRINT("\r\n");
    // }

    // for (i=0; i<4; i++) {
    //     SYS_PRINT("[DG] r=%d | ", i*16);
    //     for (j=0; j<4; j++) {
    //         SYS_PRINT("%x, ", Vgate_raw[(i*16)*64 + j*16]);
    //     }
    //     SYS_PRINT("\r\n");
    // }
    
    for (i=0; i<64; i++) {
        for (j=0; j<64; j++) {
            if ( (Vwrite_raw[i*64 + j] == 0x0) || (Vgate_raw[i*64 + j] ==0x0 )) {
                // Skip
//                SYS_PRINT("(%d,%d) ", i, j);
                continue;
            } else {
                A0_write_single_ext(arr, i, j, Vwrite_raw[i*64 + j], Vgate_raw[i*64 + j], 
                                Vzero_raw, mode, Twidth);
            }
        }
    }
  
    return 0;
}

int A0_write_single(uint8_t arr, uint8_t row, uint8_t col, 
                        uint16_t Vwrite_raw, uint16_t Vgate_raw, 
                        uint8_t is_set) {
    /*
     * Program a single device
     * 
     */
    uint16_t data_row[4];
    uint16_t data_col[4];
    
    uint8_t fifo_en, fifo_ch;
    
    if ( (Vwrite_raw == 0x0) || (Vgate_raw ==0x0 ) ) {
        return -1;
    }
    
    SYS_PRINT("(%d,%d) ", row, col);
    
    int i;
    
    for (i=0; i<4; i++) {
        data_row[i] = 0;
        data_col[i] = 0;
    }
    
    gen_data_row(row, data_row);
    gen_data_col(col, data_col);
    
    load_vectors(arr, data_row, true);
    load_vectors(arr, data_col, false);
    
    WRT_INTERNAL_ENOn();
    WRITE_ADD_CAPOff();
    WRITE_SEL_EXTOff();

    reset_dpe();

    // dac_set( DAC_VP_PAD, 0x00);
    
    NFORCE_SAFE_Set( 0x1 << arr );

    if (is_set==true) {
        WRITE_FWDOn();
        ROW_WRITE_CONNECTOn();
    } else {
        WRITE_FWDOff();
        COL_WRITE_CONNECTOn();
    }
    
    CONNECT_COLUMN_TOn();

    dac_set( P_TVDD, Vgate_raw);
    dac_set( DAC_VP_PAD, Vwrite_raw);
    
    // Wait for the DAC
    BSP_DelayUs(5);
    
    WRT_PULSEOn();
    BSP_DelayUs(0.2);
    WRT_PULSEOff();
    
    BSP_DelayUs(1);

    CONNECT_COLUMN_TOff();
    ROW_WRITE_CONNECTOff();
    NFORCE_SAFE_Set( 0x0 );
    
    return 0;
}

int A0_write_batch(uint8_t arr, uint8_t mode, uint16_t * Vwrite_raw, uint16_t * Vgate_raw) {
  
    SYS_PRINT("\tStart Prog.%d,%d\r\n", arr, mode);
    
    int i, j;
    
//     for (i=0; i<4; i++) {
//         SYS_PRINT("[DW] r=%d | ", i*16);
//         for (j=0; j<4; j++) {
//             SYS_PRINT("%x, ", Vwrite_raw[(i*16)*64 + j*16]);
//         }
//         SYS_PRINT("\r\n");
//     }
//
//     for (i=0; i<4; i++) {
//         SYS_PRINT("[DG] r=%d | ", i*16);
//         for (j=0; j<4; j++) {
//             SYS_PRINT("%x, ", Vgate_raw[(i*16)*64 + j*16]);
//         }
//         SYS_PRINT("\r\n");
//     }
//    
    for (i=0; i<64; i++) {
        for (j=0; j<64; j++) {
            if ( (Vwrite_raw[i*64 + j] == 0x0) || (Vgate_raw[i*64 + j] ==0x0 )) {
                // Skip
//                SYS_PRINT("(%d,%d) ", i, j);
                continue;
            } else {
                A0_write_single(arr, i, j, Vwrite_raw[i*64 + j], Vgate_raw[i*64 + j], mode);
            }
        }
    }
    
    return 0;
}



uint16_t exp_adc_test( uint8_t fifo_en) {
    /*
     * Read a single device
     * 
     */
    uint16_t res_buff[16];
    
    reset_dpe();
    
    ARRAY_EN_Set(0x7);
    NFORCE_SAFE_Set( 0x7 );
    
    CONNECT_TIAOff();
    CONNECT_COLUMN_TOff();

    ADC_SEL_EXTERNALOn();
    DPE_EXT_OVERRIDE_ENOn();

    // DPE_EXT_SHOn();
    
    DPE_EXT_SHOff();
    reset_dpe();
    DPE_EXT_SHOn();

    while ( ADC_DONEStateGet() == 0) {}
    BSP_DelayUs(0.2);

    DPE_EXT_SHOff();
    
    download_fifo( fifo_en, res_buff);

    return res_buff[15];
}