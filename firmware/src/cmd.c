

#include "cmd.h"
#include "dut_func.h"

CMD_DATA cmdData;

uint8_t __attribute__ ((aligned (16))) txData[]  = "Testing 8-bit SPI!";
uint8_t txDataSize = sizeof(txData);

//uint8_t __attribute__ ((aligned (16))) rxData[512];
uint8_t rxData[512];
uint8_t rxDataSize;

//int N_ROW = 64*3;
uint16_t read_buffer[64][64];
uint16_t read_row;
uint16_t n_row_to_send;

uint16_t dac_buffer[64][64];
uint16_t dac_buffer2[64][64];

void CMD_Initialize ( void )
{
//    SYS_WDT_Enable( false );
    /* Place the App state machine in its initial state. */
    cmdData.state = CMD_STATE_INIT;
    
    // Pull the PINs high to prevent excessive current sink to the PIC
//    default_highpins();
    
    DRV_ADC0_Open();
    DRV_ADC1_Open();
    DRV_ADC2_Open();
    DRV_ADC3_Open();
    DRV_ADC4_Open();
    
    DRV_SPI0_Open( DRV_SPI_INDEX_0, DRV_IO_INTENT_EXCLUSIVE );
    SERIAL_CHAIN_SEL_0Off();
    SERIAL_CHAIN_SEL_1Off();
    
    DRV_SPI1_Open( DRV_SPI_INDEX_1, DRV_IO_INTENT_EXCLUSIVE );
//    DRV_SPI2_Open( DRV_SPI_INDEX_2, DRV_IO_INTENT_EXCLUSIVE );
    /* TODO: Initialize your application's state machine and other
     * parameters.
     */
    
    SYS_PRINT("CMD initialized...\r\n");
//    DATAIN_Set(0xffff);\
//    DATAOUT_Set(0xffff);
//    ADDR_REGS_Set(0xff);
    GPIO_Write('H', 0xff);
}



DRV_SPI_BUFFER_HANDLE spi_handle;
DRV_SPI_BUFFER_HANDLE spi_ongoing_channel;

void CMD_Tasks ( void )
{
    /* Check the application's current state. */
//    SYS_WDT_TimerClear();
    switch ( cmdData.state )
    {
        /* Application's initial state. */
        case CMD_STATE_INIT:
        {
//            bool appInitialized = true;
            if ( !USB_Read_isBusy() )
            {
                int sz_read = USB_Read( &cmdData.usb_buf_rx );
                
                if ( sz_read != -1 ) {
                    cmdData.state = CMD_STATE_PARSE;
                    SYS_PRINT("Input next command\r\n");
                }
            }
            break;
        }
        case CMD_STATE_PARSE:
        {
            if (!USB_Read_isBusy()) {
                // Received some data
                
                if (*cmdData.usb_buf_rx != NULL){
                
                    // Received something, suppose it is a string.
//                    memcpy( cmdData.cmd, cmdData.usb_buf_rx, strlen(cmdData.usb_buf_rx) +1);
                    memcpy( cmdData.cmd, cmdData.usb_buf_rx, 512);
                    SYS_PRINT("Received: %s\r\n", cmdData.cmd );

                    char *ptr = strtok( cmdData.cmd, "," );
                    int icmd = atoi(ptr);
                    SYS_PRINT("\t Command = %d\r\n", icmd);

                    int i, j;
                    int channel;
                    char portName;
                    uint32_t portValue;
                    
                    uint16_t slewMask;
                    uint8_t slewRate;
                    
                    int pwm_width;
                    int pwm_period;
                    
                    uint8_t ser_addr;
                    int ser_len;
                    
                    uint16_t adc_result[8];
                    
                    uint8_t row, col, arr;
                    uint16_t res_read;
                    
                    switch ( icmd ) 
                    {
                        // Formal commands
                        case 201:
                            /*
                             * gpio_port_write()
                             * Commmand sample: 201,A,7676
                             * Write 7676 to port A
                             */
                            
                            ptr = strtok(NULL, ",");
                            portName = *ptr;
                            
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);
                            
                            GPIO_Write( portName, portValue );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break;
                        case 202:
                            /*
                             * gpio_port_read()
                             * Command: 202,C
                             * Read data from port C
                            */
                            
                            ptr = strtok(NULL, ",");
                            portName = *ptr;
                            
                            portValue = GPIO_Read( portName );
                            
                            SYS_PRINT("\t Read value=%x\r\n", portValue);
                            USB_Write( (char *) &portValue, 4);
                            
                            cmdData.state = CMD_STATE_INIT;
                            break;
                            
                        case 203:
                        case 204:
                        case 205:
//                        case 206:
                            /*
                             * 203: 
                             * 204: 
                             * 205: 
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);
                            
                            switch ( icmd ) {
                                case 203: ROW_COL_DATA_Set(portValue); break;
                                case 204: ROW_COL_BANK_Set(portValue); break;
                                case 205: ADC_FIFO_EN_Set(portValue); break;
                            }
                            
                            cmdData.state = CMD_STATE_INIT;
                            break;
                        case 207:
                            /*
                             * 
                             * 
                             */
                            
                            portValue = ADC_OUT_Get();
                            SYS_PRINT("\t Read value=%d\r\n", portValue);
                            USB_Write( (char *) &portValue, 4);
                            
                            cmdData.state = CMD_STATE_INIT;
                            break;
                        case 210: 
                            /*
                             * gpio_slewrate_select()
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            portName = *ptr;
                            
                            ptr = strtok(NULL, ",");
                            slewMask = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            slewRate = atoi(ptr);
                            
                            GPIO_SlewRateSelect( portName, slewMask, slewRate );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break;
                            
                        // Single pin operations
                        case 211:
                        case 212:
                        case 213:
                        case 230:
                        case 231:
                            ptr = strtok(NULL, ",");
                            portName = *ptr;
                            
                            ptr = strtok(NULL, ",");
                            uint16_t pinPos = atoi(ptr);
                            
                            switch ( icmd ) {
                                case 211: GPIO_Pin_Set(portName, pinPos); break;
                                case 212: GPIO_Pin_Clear(portName, pinPos); break;
                                case 213: GPIO_Pin_Toggle(portName, pinPos); break;
                                case 230: GPIO_PinDirection_InputSet(portName, pinPos); break;
                                case 231: GPIO_PinDirection_OutputSet(portName, pinPos); break;
                            }
                            cmdData.state = CMD_STATE_INIT;
                            break;
                            
                        case 214:
                            /*
                             * dac_write()
                             */
                            
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);
                            
                            SYS_PRINT("\t SPI: Sending data %x to DAC, size=4\r\n", portValue);

                            // SPI 6 for DAC
                            PIC_CSOn();
                            PIC_CSOff();
                            spi_handle = DRV_SPI1_BufferAddWrite( &portValue, 4, NULL, NULL); 

                            spi_ongoing_channel = 1;
                            cmdData.state = CMD_STATE_SPI;
                            
                            break;
                            
                        case 215:
                        case 219:
                            /*
                             * serial_write()
                             */
                            
                            ptr = strtok(NULL, ",");
                            ser_addr = atoi(ptr) & 0x3; // address
                            
                            ptr = strtok(NULL, ",");
                            ser_len = atoi(ptr); 
                            
                            ptr = strtok(NULL, ","); //expecting a non-zero character
                            ptr += 2;
                            SYS_PRINT("\t Sending data '%s' with addr=%x, size=%d\r\n", ptr, ser_addr, ser_len);
                            
//                            PLIB_PORTS_PinSet(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_14);
//                            PLIB_PORTS_PinClear(PORTS_ID_0, PORT_CHANNEL_D, PORTS_BIT_POS_14);
                            switch (ser_addr) {
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
//                            if (! (ser_addr & 0x1)) {
//                                SERIAL_CHAIN_SEL_0Off();
//                            }
//                                
//                            if (! (ser_addr & 0x2) ) {
//                                SERIAL_CHAIN_SEL_1Off();
//                            }
                            
                            switch ( icmd ) {
                                case 215:
                                    spi_handle = DRV_SPI0_BufferAddWrite( ptr, ser_len, NULL, NULL);
                                    spi_ongoing_channel = 0;
                                    
                                    break;
                                case 219:
                                    spi_handle = DRV_SPI0_BufferAddWriteRead2(ptr, ser_len, rxData, ser_len, NULL, NULL, NULL);
                                    rxDataSize = ser_len;
                                    spi_ongoing_channel = 0 | (0x1<<8);
                                    
                                    break;
                            }
                            cmdData.state = CMD_STATE_SPI;
                            
                            break;
                            
                        case 216:
                            /*
                             * pic_adc_read()
                             */
                            
                            DRV_ADC_Start();
                            SYS_PRINT("\t ADC started\r\n");
                            cmdData.state = CMD_STATE_ADC;
                            break; 
                        case 217:
                            /*
                             * clk_start()
                             */
                            
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);
                            
                            SYS_PRINT("\t Starting REFCLKO%d\r\n", portValue+1);
                            // 
                            PLIB_OSC_ReferenceOutputEnable( OSC_ID_0, portValue );
//                            PLIB_OSC_ReferenceOutputEnable ( OSC_ID_0, OSC_REFERENCE_3 );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                        case 218:
                            /*
                             * clk_stop()
                             */
                            
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);
                            
                            SYS_PRINT("\t Stopping REFCLKO%d\r\n", portValue+1);
                            
                            PLIB_OSC_ReferenceOutputDisable( OSC_ID_0, portValue );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                        case 220:
                            /*
                             * clk_config()
                             */
                            
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            int clk_base = atoi(ptr);
                            ptr = strtok(NULL, ",");
                            int clk_div = atoi(ptr);
                            
                            SYS_PRINT("\t Setting REFCLKO%d, base=%d, div=%d\r\n", portValue+1, clk_base, clk_div);
                            
                            /* ROSEL System Clock SYSCLK */
                            PLIB_OSC_ReferenceOscBaseClockSelect ( OSC_ID_0, portValue, clk_base );
                            /* RODIV */
                            PLIB_OSC_ReferenceOscDivisorValueSet ( OSC_ID_0, portValue, clk_div );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                        case 221:
                            /*
                             * i2c_write(addr, data)
                             */
                            ptr = strtok(NULL, ",");
                            ser_addr = atoi(ptr); // address
                            
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr); // data
                            
//                            ptr = strtok(NULL, ",");
                            SYS_PRINT("\t CMD: Sending data %x to addr=%x\r\n", portValue, ser_addr);
                            
                            I2C_Write(ser_addr, portValue);
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                        case 301:
                            /*
                             * test download_fifo()
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            ser_addr = atoi(ptr);
                            
                            uint16_t res_buff[16];
                            download_fifo( ser_addr, res_buff);
                            
                            USB_Write( (char *) res_buff, 2*16 );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                        case 302:
                            /*
                             * test pic_dac_set()
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);

                            DAC_CH ch = P_ADC_EXT_TEST_IN;
                            dac_set(ch, portValue);

                            cmdData.state = CMD_STATE_INIT;
                            break; 

                        case 303:
                            /*
                             * test blocking scan chain
                             */
                            
                            ptr = strtok(NULL, ",");
                            ser_addr = atoi(ptr) & 0x3; // address
                            
                            ptr = strtok(NULL, ",");
                            ser_len = atoi(ptr); 
                            
                            ptr = strtok(NULL, ","); //expecting a non-zero character
                            ptr += 2;
                            SYS_PRINT("\t Sending data '%s' with addr=%x, size=%d\r\n", ptr, ser_addr, ser_len);

                            serial_set( ser_addr, ser_len, ptr);
                            
                            //Handshake
                            USB_Write( "0", 1 );

                            cmdData.state = CMD_STATE_INIT;
                            break;
                        case 304:
                            /*
                             * test dac_init
                             */
                            ptr = strtok(NULL, ",");
                            portValue = atoi(ptr);
                            
                            dac_init(portValue);  
                            
                            cmdData.state = CMD_STATE_INIT;
                            break;
                        case 401:
                            /*
                             * read_single
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            row = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            col = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode: 0 is normal read, 1 is autogain
                            
                            res_read = A0_read_single(arr, row, col, channel);
                            SYS_PRINT("\t Read res_read=%x, mode=%d\r\n", res_read, channel);
                            USB_Write( (char *) &res_read, 2 );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 

                        case 411:
                            /*
                             * read_single_test
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            row = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            col = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode: 0 is normal read, 1 is autogain

                            ptr = strtok(NULL, ",");
                            uint32_t T1 = atoi(ptr); 

                            ptr = strtok(NULL, ",");
                            uint32_t T2 = atoi(ptr); 

                            ptr = strtok(NULL, ",");
                            uint32_t T3 = atoi(ptr); 

                            ptr = strtok(NULL, ",");
                            uint32_t Nt = atoi(ptr); 

                            SYS_PRINT("\t T1=%d, T1=%d, T1=%d, Nt=%d, \r\n", T1, T2, T3, Nt);
                            
                            res_read = A0_read_single_test(arr, row, col, channel, T1, T2, T3, Nt);
                            SYS_PRINT("\t Read res_read=%x, mode=%d\r\n", res_read, channel);
                            USB_Write( (char *) &res_read, 2 );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                            
                        case 412:
                            /*
                             * read_ADC_test
                             */

                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode: 0 is normal read, 1 is autogain


                            SYS_PRINT("\t ch=%d \r\n", channel);
                            
                            res_read = exp_adc_test(channel);
                            SYS_PRINT("\t Read res_read=%x, ch=%d\r\n", res_read, channel);
                            USB_Write( (char *) &res_read, 2 );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 

                        case 402:
                            /*
                             * read_batch
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);        // array number
                            
                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode: 0 is normal read, 1 is autogain

                            ptr = strtok(NULL, ",");
                            uint32_t Tdly = atoi(ptr);    // Pause between reads

                            A0_read_batch(arr, (uint16_t *)read_buffer, channel, Tdly);
                            SYS_PRINT("\t READ: batch read completed.\r\n");
                            
                            read_row = 0;
                            n_row_to_send = 64;
                            cmdData.state = CMD_STATE_USB_WRITE;
                            break; 
                        case 502:
                            /*
                             * read_batch2
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);        // array number
                            
                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode: 0 is normal read, 1 is autogain

                            A0_read_batch2(arr, (uint16_t *)read_buffer, channel );
                            SYS_PRINT("\t READ: batch read completed.\r\n");
                            
                            read_row = 0;
                            n_row_to_send = 64;
                            cmdData.state = CMD_STATE_USB_WRITE;
                            break; 
                        case 403:
                            /*
                             * dpe_batch
                             * Command example:
                             *      403,0,siz,\x01\x01....
                             */

                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);        // array number

                            ptr = strtok(NULL, ",");
                            ser_len = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode

                            ptr = strtok(NULL, ",");
                            Tdly = atoi(ptr);    // Pause between reads

                            ptr = strtok(NULL, ","); // expecting a non-zero byte after , character
                            SYS_PRINT("\t DPE on array %d, # of vectors sz=%d, Tdly=%d\r\n", arr, ser_len, Tdly);

                            if (ser_len>60) {
                                // usb buffer limit is 512, so one packet can accommodate (512-11) / 8 
                                SYS_PRINT("\t In valid # of vectors! exit...\r\n", arr, ser_len);
                            } else {
                                ptr += 2;

                                A0_dpe_batch(arr, ser_len, channel, Tdly, ptr, (uint16_t *)read_buffer);
                                
                                read_row = 0;
                                n_row_to_send = ser_len;
                                cmdData.state = CMD_STATE_USB_WRITE;
                                break; 
                            }
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                            
                        case 404:
                            /*
                             * Write single
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);        // array number

                            ptr = strtok(NULL, ",");
                            row = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            col = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode: 0 is reset, 1 is set
                            
                            ptr = strtok(NULL, ",");
                            uint16_t Vwrite_raw = atoi(ptr); 
                            
                            ptr = strtok(NULL, ",");
                            uint16_t Vgate_raw = atoi(ptr); 

                            SYS_PRINT("\t Write single arr=%d, row=%d, col=%d, mode=%d\r\n", arr, row, col, channel);
                            SYS_PRINT("\t              Vwrite_raw=0x_%x, Vgate_raw=0x_%x\r\n", Vwrite_raw, Vgate_raw);
                            
                            A0_write_single(arr, row, col, Vwrite_raw, Vgate_raw, channel);
                            //Handshake programming complete
                            USB_Write( "0", 1 );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 
                            
                        case 405:
                            /*
                             * Write batch
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);         // array number
                            
                            ptr = strtok(NULL, ",");
                            int mode = atoi(ptr);    // mode: 0 is reset, 1 is set
                            
                            ptr = strtok(NULL, ",");
                            row = atoi(ptr);         // current row
                            
                            SYS_PRINT("\t Write batch  arr=%d, mode=%d, row=%d\r\n", arr, mode, row);
                            
                            ptr = strtok(NULL, ","); //expecting a non-zero character
                            ptr += 2;
                            
                            SYS_PRINT("\t ptr=%c\r\n", *ptr);
                            
                            if (row < 64) {
                                // Vwrite
                                // Two rows at a time
                                memcpy( &dac_buffer[row][0], ptr, 256);
                            } else if (row<128) {
                                // Vgate
                                memcpy( &dac_buffer2[row-64][0], ptr, 256);
                            }
                            
                            if (row == 126){
                                // Start programming
                                A0_write_batch(arr, mode, (uint16_t *)dac_buffer, (uint16_t *)dac_buffer2);
                                
                                // Handshake
                                USB_Write( "0", 1 );
                            }

                            cmdData.state = CMD_STATE_INIT;
                            break; 

                        case 406:
                            /*
                             * Write single with external timing
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);        // array number

                            ptr = strtok(NULL, ",");
                            row = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            col = atoi(ptr);
                            
                            ptr = strtok(NULL, ",");
                            channel = atoi(ptr);    // mode: 0 is reset, 1 is set
                            
                            ptr = strtok(NULL, ",");
                            Vwrite_raw = atoi(ptr); 
                            
                            ptr = strtok(NULL, ",");
                            Vgate_raw = atoi(ptr); 
                            
                            ptr = strtok(NULL, ",");
                            uint16_t Vzero_raw = atoi(ptr); 

                            ptr = strtok(NULL, ",");
                            uint32_t Twidth = atoi(ptr); 

                            SYS_PRINT("\t Write single arr=%d, row=%d, col=%d, mode=%d\r\n", arr, row, col, channel);
                            SYS_PRINT("\t   Vwrite_raw=0x_%x, Vgate_raw=0x_%x, Vzero_raw=0x_%x, Twidth=%d us, \r\n", Vwrite_raw, Vgate_raw, Vzero_raw, Twidth);
                            
                            A0_write_single_ext(arr, row, col, Vwrite_raw, Vgate_raw, Vzero_raw, channel, Twidth);
                            //Handshake programming complete
                            USB_Write( "0", 1 );
                            
                            cmdData.state = CMD_STATE_INIT;
                            break; 

                        case 407:
                            /*
                             * Write batch with external timing
                             * 
                             */
                            ptr = strtok(NULL, ",");
                            arr = atoi(ptr);         // array number
                            
                            ptr = strtok(NULL, ",");
                            mode = atoi(ptr);    // mode: 0 is reset, 1 is set

                            ptr = strtok(NULL, ",");
                            Vzero_raw = atoi(ptr);    // 

                            ptr = strtok(NULL, ",");
                            Twidth = atoi(ptr);    // Twidth in microseconds
                            
                            ptr = strtok(NULL, ",");
                            row = atoi(ptr);         // current row
                            
                            SYS_PRINT("\t Write batch  arr=%d, mode=%d, row=%d, Vz=%x, Twidth=%d,\r\n", 
                                        arr, mode, row, Vzero_raw, Twidth);
                            
                            ptr = strtok(NULL, ","); //expecting a non-zero character
                            ptr += 2;
                            
                            SYS_PRINT("\t ptr=%c\r\n", *ptr);
                            
                            if (row < 64) {
                                // Vwrite
                                // Two rows at a time
                                memcpy( &dac_buffer[row][0], ptr, 256);
                            } else if (row<128) {
                                // Vgate
                                memcpy( &dac_buffer2[row-64][0], ptr, 256);
                            }
                            
                            if (row == 126){
                                // Start programming
                                A0_write_batch_ext(arr, mode, (uint16_t *)dac_buffer, (uint16_t *)dac_buffer2);
                                
                                // Handshake
                                USB_Write( "0", 1 );
                            }

                            cmdData.state = CMD_STATE_INIT;
                            break; 
                             
                        // Test commands
                        // Command start from 101 for fault tolerance
                        case 101:
                            // The expected format is "{cmd},{float}"
                            ptr = strtok(NULL, ",");
                            double par1 = atof( ptr );
                            SYS_PRINT("\t par1 = %f\r\n", par1);
                            cmdData.state = CMD_STATE_INIT;
                            break;
                        case 103:;
                            //test echo back
                            int res[64];
                            for (i=0; i<64; i++) {
                                res[i] = 100000 * i;
                            }
                            
                            USB_Write( (char *) &res, 4 * 64 );
                            cmdData.state = CMD_STATE_INIT;
                            break;
                        default:
                            SYS_MESSAGE("Illegal command received!\r\n");
                            cmdData.state = CMD_STATE_INIT;
                    }
                } else {
                    cmdData.state = CMD_STATE_INIT;
                }
            }
            
            break;
        }
        case CMD_STATE_SPI:
        {
            SYS_PRINT("\t SPI: Waiting for ch=%d \r\n", spi_ongoing_channel);
            switch (spi_ongoing_channel & 0xff ) {
                case 0:
                    if (DRV_SPI0_BufferStatus(spi_handle) == DRV_SPI_BUFFER_EVENT_COMPLETE) {
                        SERIAL_CHAIN_SEL_0On();
                        SERIAL_CHAIN_SEL_1On();
                        
                        if (spi_ongoing_channel & 0xff00 ) {
                            SYS_PRINT("\t SPI: Sending data back size=%d \r\n", rxDataSize);
                            USB_Write( (char *) rxData, rxDataSize );
                        }
                        
                        cmdData.state = CMD_STATE_INIT;
                    }
                    break;
                case 1:
                    if (DRV_SPI1_BufferStatus(spi_handle) == DRV_SPI_BUFFER_EVENT_COMPLETE) {
                        PIC_CSOn();
                        cmdData.state = CMD_STATE_INIT;
                    }
                    break;
                default: 
                    SYS_PRINT("\t Channel error, got ch=%d\r\n", spi_ongoing_channel);
                    cmdData.state = CMD_STATE_INIT; 
            }
          
            break;
        }
        case CMD_STATE_ADC:
        {
            int NUM_ADC = 5;
            
            uint32_t adc_read[NUM_ADC];
            
            int n_adc_completed = 0;
            
            int i;
            for (i=0; i<NUM_ADC; i++) {
             
                if ( !(n_adc_completed & (0x1<<i) ) && 
                    DRV_ADC_SamplesAvailable(i) ) {
                    adc_read[i] = DRV_ADC_SamplesRead(i);
                    
                    n_adc_completed = n_adc_completed | (0x1<<i);
                    
                    SYS_PRINT("\t ADC_%d = %x, n_adc=%x\r\n", 
                            i, adc_read[i], n_adc_completed );
                }
            }

            if (n_adc_completed == 0x1f ) {
                // Done reading
                USB_Write( (char *) adc_read, 4*NUM_ADC );
                cmdData.state = CMD_STATE_INIT;
            }
            
            break;
        }
        case CMD_STATE_USB_WRITE:
        {
            if (! USB_Write_isBusy() ) {
//                SYS_PRINT("\t READ: read_row=%d\r\n", read_row);
                USB_Write( (char *) read_buffer[read_row], 512 );
                read_row += 4;
                
                if (read_row>=n_row_to_send) {
                    cmdData.state = CMD_STATE_INIT;
                }
            }
//            cmdData.state = CMD_STATE_INIT;
        }
        case CMD_STATE_SERVICE_TASKS:
        {
        
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
