

#include "dut_ports.h"


int portName2Channel( char portName ) {
    int portChannel = portName - 'A';
    
    if (portChannel>7)  portChannel--;

    if (portChannel>=0 && portChannel<=9) {
        return portChannel;
    } else {
        return -1;
        SYS_PRINT("\t Wrong portName...\r\n");
    }
}

void GPIO_Write( char portName, uint32_t portValue ) {
    int portChannel = portName2Channel(portName);
    
    SYS_PRINT("\t Writing %c, port_id=%d, value=%x\r\n", portName, portChannel, portValue);
    PLIB_PORTS_Write(PORTS_ID_0, portChannel, portValue);
}

void GPIO_Pin_Set( char portName, uint16_t pos ){
    int portChannel = portName2Channel(portName);
    
    PLIB_PORTS_PinSet(PORTS_ID_0, portChannel, pos);
}

void GPIO_Pin_Clear( char portName, uint16_t pos ){
    int portChannel = portName2Channel(portName);
    
    PLIB_PORTS_PinClear(PORTS_ID_0, portChannel, pos);
}

void GPIO_Pin_Toggle( char portName, uint16_t pos ){
    int portChannel = portName2Channel(portName);
    
    PLIB_PORTS_PinToggle(PORTS_ID_0, portChannel, pos);
}

void GPIO_PinDirection_InputSet( char portName, uint16_t pos ){
    int portChannel = portName2Channel(portName);
    PLIB_PORTS_PinDirectionInputSet(PORTS_ID_0, portChannel, pos );
}

void GPIO_PinDirection_OutputSet( char portName, uint16_t pos ){
    int portChannel = portName2Channel(portName);
    PLIB_PORTS_PinDirectionOutputSet(PORTS_ID_0, portChannel, pos );
}

// Ref
//typedef enum {
//
//    PORTS_PIN_SLEW_RATE_FASTEST = 0x05,
//    PORTS_PIN_SLEW_RATE_FAST = 0x06,
//    PORTS_PIN_SLEW_RATE_SLOW = 0x09,
//    PORTS_PIN_SLEW_RATE_SLOWEST = 0x0A
//
//} PORTS_PIN_SLEW_RATE;

char GPIO_SLEW_RATE[4] = {0x05, 0x06, 0x09, 0x0A};

void GPIO_SlewRateSelect(char portName, uint16_t slewMask, uint8_t slewRate) {
    int portChannel = portName2Channel(portName);
    
    SYS_PRINT("\t Changing port %c(ch=%d), to slewRate of %d(0x%x), with mask=0x%x\r\n", 
            portName, portChannel, slewRate, GPIO_SLEW_RATE[slewRate], slewMask);
    PLIB_PORTS_ChannelSlewRateSelect(PORTS_ID_0, portChannel, slewMask, GPIO_SLEW_RATE[slewRate]);
}

uint32_t GPIO_Read( char portName ) {
    
    int portChannel = portName2Channel(portName);

    SYS_PRINT("\t Reading from %c, port_id=%d\r\n", portName, portChannel);
    return PLIB_PORTS_Read(PORTS_ID_0, portChannel);
}

PORTS_CHANNEL ROW_COL_DATA_PORTS[16] = {
    ROW_COL_DATA_0_PORT,
    ROW_COL_DATA_1_PORT,
    ROW_COL_DATA_2_PORT,
    ROW_COL_DATA_3_PORT,
    ROW_COL_DATA_4_PORT,
    ROW_COL_DATA_5_PORT,
    ROW_COL_DATA_6_PORT,
    ROW_COL_DATA_7_PORT,
    ROW_COL_DATA_8_PORT,
    ROW_COL_DATA_9_PORT,
    ROW_COL_DATA_10_PORT,
    ROW_COL_DATA_11_PORT,
    ROW_COL_DATA_12_PORT,
    ROW_COL_DATA_13_PORT,
    ROW_COL_DATA_14_PORT,
    ROW_COL_DATA_15_PORT
};

PORTS_BIT_POS ROW_COL_DATA_PINS[16] = {
    ROW_COL_DATA_0_PIN,
    ROW_COL_DATA_1_PIN,
    ROW_COL_DATA_2_PIN,
    ROW_COL_DATA_3_PIN,
    ROW_COL_DATA_4_PIN,
    ROW_COL_DATA_5_PIN,
    ROW_COL_DATA_6_PIN,
    ROW_COL_DATA_7_PIN,
    ROW_COL_DATA_8_PIN,
    ROW_COL_DATA_9_PIN,
    ROW_COL_DATA_10_PIN,
    ROW_COL_DATA_11_PIN,
    ROW_COL_DATA_12_PIN,
    ROW_COL_DATA_13_PIN,
    ROW_COL_DATA_14_PIN,
    ROW_COL_DATA_15_PIN
};

void ROW_COL_DATA_Set(PORTS_DATA_TYPE value) {
//    SYS_PRINT("\t Setting ROW_COL_DATA value %x\r\n", value);
    
    int i;
    for (i=0; i<16; i++) {
        PLIB_PORTS_PinWrite(PORTS_ID_0, ROW_COL_DATA_PORTS[i], ROW_COL_DATA_PINS[i], value&(0x1<<i));
    }
}

void ROW_COL_BANK_Set(PORTS_DATA_TYPE value) {
    // K0, K1, K2, K3
//    SYS_PRINT("\t Setting ROW_COL_BANK value %x (raw=%x)\r\n", value, value & 0x000f);
    
    // Only lowest four bits get written
    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_K, value & 0x000f);
}

void ADC_FIFO_EN_Set(PORTS_DATA_TYPE value) {
    // K4, K5, K6, K7
//    SYS_PRINT("\t Setting ADC_FIFO_EN value %x (raw=%x)\r\n", value, (value<<4) & 0x00f0);
    
    // Only lowest four bits get written
    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_K, (value<<4) & 0x00f0);
}

PORTS_CHANNEL ADC_OUT_PORTS[13] = {
    ADC_OUT_0_PORT,
    ADC_OUT_1_PORT,
    ADC_OUT_2_PORT,
    ADC_OUT_3_PORT,
    ADC_OUT_4_PORT,
    ADC_OUT_5_PORT,
    ADC_OUT_6_PORT,
    ADC_OUT_7_PORT,
    ADC_OUT_8_PORT,
    ADC_OUT_9_PORT,
    ADC_OUT_10_PORT,
    ADC_OUT_11_PORT,
    ADC_OUT_12_PORT
};

PORTS_BIT_POS ADC_OUT_PINS[13] = {
    ADC_OUT_0_PIN,
    ADC_OUT_1_PIN,
    ADC_OUT_2_PIN,
    ADC_OUT_3_PIN,
    ADC_OUT_4_PIN,
    ADC_OUT_5_PIN,
    ADC_OUT_6_PIN,
    ADC_OUT_7_PIN,
    ADC_OUT_8_PIN,
    ADC_OUT_9_PIN,
    ADC_OUT_10_PIN,
    ADC_OUT_11_PIN,
    ADC_OUT_12_PIN
};


PORTS_DATA_TYPE ADC_OUT_Get(void){   
    PORTS_DATA_TYPE value_dataout = 0;
    
    int i;
    for (i=0; i<13; i++) {
        // Will replace with PinGet to read PORTs directly
        value_dataout = value_dataout | (PLIB_PORTS_PinGet(PORTS_ID_0, ADC_OUT_PORTS[i], ADC_OUT_PINS[i]) << i);
    }
    
//    SYS_PRINT("\t Read ADC_OUT value %x\r\n", value_dataout);
    return value_dataout;
}

PORTS_CHANNEL ARRAY_EN_PORTS[3] = {
    ARRAY_EN_0_PORT,
    ARRAY_EN_1_PORT,
    ARRAY_EN_2_PORT
};

PORTS_BIT_POS ARRAY_EN_PINS[3] = {
    ARRAY_EN_0_PIN,
    ARRAY_EN_1_PIN,
    ARRAY_EN_2_PIN
};


void ARRAY_EN_Set(PORTS_DATA_TYPE value) {
//    SYS_PRINT("\t Setting ARRAY_EN value %x\r\n", value);
    
    int i;
    for (i=0; i<3; i++) {
        PLIB_PORTS_PinWrite(PORTS_ID_0, ARRAY_EN_PORTS[i], ARRAY_EN_PINS[i], value&(0x1<<i));
    }
}

PORTS_CHANNEL NFORCE_SAFE_PORTS[3] = {
    NFORCE_SAFE0_PORT,
    NFORCE_SAFE1_PORT,
    NFORCE_SAFE2_PORT
};

PORTS_BIT_POS NFORCE_SAFE_PINS[3] = {
    NFORCE_SAFE0_PIN,
    NFORCE_SAFE1_PIN,
    NFORCE_SAFE2_PIN
};

void NFORCE_SAFE_Set(PORTS_DATA_TYPE value) {
//    SYS_PRINT("\t Setting NFORCE_SAFE value %x\r\n", value);
    
    int i;
    for (i=0; i<3; i++) {
        PLIB_PORTS_PinWrite(PORTS_ID_0, NFORCE_SAFE_PORTS[i], NFORCE_SAFE_PINS[i], value&(0x1<<i));
    }
}


//void ADDR_REGS_Set(PORTS_DATA_TYPE value) {
//    // K0-7
//    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_K, value);
//}
//
//void DATAIN_Set(PORTS_DATA_TYPE value) {    
//    SYS_PRINT("\t Setting data value %x\r\n", value);
//    // H9-12, 15 J0, 2-7, 12-15
//    PORTS_DATA_TYPE value_port_h = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_H);
//    PORTS_DATA_TYPE value_port_j = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_J);
//    
//    SYS_PRINT("\t H=%x, J=%x\r\n", value_port_h, value_port_j);
//    value_port_h = (value_port_h & ~(0xf << 9))  | ( (value&0x000f) <<9 );
//    value_port_h = (value_port_h & ~(0x1 << 15)) | ( (value&0x0010) <<(11));
//    
//    value_port_j = (value_port_j & ~(0x01 ))     | ( (value&0x0020) >>(5));
//    value_port_j = (value_port_j & ~(0x3f << 2)) | ( (value&0x0fc0) >>(4));
//    value_port_j = (value_port_j & ~(0x0f <<12)) | ( (value&0xf000) );
//    SYS_PRINT("\t H=%x, J=%x\r\n", value_port_h, value_port_j);
//    
//    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_H, value_port_h);
//    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_J, value_port_j);
//}
//
//void DATAOUT_Set(PORTS_DATA_TYPE value) {
//    // A0-7, G14, 15, H0-3, 6-7
//    
////    SYS_PRINT("\t Setting data value %x\r\n", value);
////    PORTS_DATA_TYPE value_port_a = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_A);
////    PORTS_DATA_TYPE value_port_g = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_G);
////    PORTS_DATA_TYPE value_port_h = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_H);
////
////    SYS_PRINT("\t A=%x, G=%x, H=%x\r\n", value_port_a, value_port_g, value_port_h);
////    value_port_a = (value_port_a & ~(0xff))  | ( (value&0x00ff) );
////    
////    value_port_g = (value_port_g & ~(0x3 << 14))  | ( (value&0x0300) <<(6));
////    
////    value_port_h = (value_port_h & ~(0xf ))       | ( (value&0x3c00) >>(10) );
////    value_port_h = (value_port_h & ~(0x3 <<6))    | ( (value&0xc000) >>(8));
////    SYS_PRINT("\t A=%x, G=%x, H=%x\r\n", value_port_a, value_port_g, value_port_h);
////    
////    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_A, value_port_a);
////    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_G, value_port_g);
////    PLIB_PORTS_Write( PORTS_ID_0, PORT_CHANNEL_H, value_port_h);
//    
//    int i;
//    for (i=0; i<16; i++) {
//        PLIB_PORTS_PinWrite(PORTS_ID_0, DATAOUT_PORTS[i], DATAOUT_PINS[i], value&(0x1<<i));
//    }
//}
//
//PORTS_DATA_TYPE DATAOUT_Get(void){ 
//    // A0-7, G14, 15, H0-3, 6-7
////    PORTS_DATA_TYPE value_port_a = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_A);
////    PORTS_DATA_TYPE value_port_g = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_G);
////    PORTS_DATA_TYPE value_port_h = PLIB_PORTS_Read( PORTS_ID_0, PORT_CHANNEL_H);
////    
////    SYS_PRINT("\t A=%x, G=%x, H=%x\r\n", value_port_a, value_port_g, value_port_h);
////    
////    PORTS_DATA_TYPE value_dataout = 0;
////    
////    value_dataout = value_port_a & 0xff;
////    value_dataout = value_dataout | ( (value_port_g>>14) & 0x3) <<8;
////    
////    value_dataout = value_dataout | ( (value_port_h) & 0xf) <<10;
////    value_dataout = value_dataout | ( (value_port_h>>6) & 0x3) <<14;
//    
//    // This approach might seem 'stupid', but it is in fact more flexible and 
//    // easier to read.
//    
//    PORTS_DATA_TYPE value_dataout = 0;
//    
//    int i;
//    for (i=0; i<16; i++) {
//        // Will replace with PinGet to read PORTs directly
//        value_dataout = value_dataout | (PLIB_PORTS_PinGet(PORTS_ID_0, DATAOUT_PORTS[i], DATAOUT_PINS[i]) << i);
//    }
//    
//    return value_dataout;
//}
//
//void DATAOUT_DirectionInputSet(PORTS_DATA_MASK mask){
//    int i;
//    for (i=0; i<16; i++) {
//        if (mask&(0x1<<i)) {
//            PLIB_PORTS_PinDirectionInputSet(PORTS_ID_0, DATAOUT_PORTS[i], DATAOUT_PINS[i] );
//        } else {
//            PLIB_PORTS_PinDirectionOutputSet(PORTS_ID_0, DATAOUT_PORTS[i], DATAOUT_PINS[i] );
//        }
//    }
//}
//
////void DATAOUT_DirectionOutputSet(PORTS_DATA_MASK mask){
////    int i;
////    for (i=0; i<16; i++) {
////        PLIB_PORTS_PinDirectionOutputSet(PORTS_ID_0, DATAOUT_PORTS[i], DATAOUT_PINS[i] );
////    }
////}
