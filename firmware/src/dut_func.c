
#include "dut_func.h"

void BSP_DelayUs(uint16_t microseconds)
{
    uint32_t time;
    
    time = READ_CORE_TIMER(); // Read Core Timer    
    time += (SYS_CLK_FREQ / 2 / 1000000) * microseconds; // calc the Stop Time    
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
    
    PICIC2_SCLOn();
    BSP_DelayUs(T_DLY * 2);
    PICIC2_SDAOn();
      
    SYS_PRINT("\r\n I2C: Completed! \r\n");
}