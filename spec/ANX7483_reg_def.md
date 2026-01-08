Based on the image provided, here is the table converted to Markdown format. I have included the header information found above the table columns as well.

**Table 71 DTX1_PORT_CFG_3**

*   **Name:** DTX1\_PORT\_CFG\_3
*   **I2C Address:** 0x7c
*   **Offset:** 0x4B

| Bit | Name | Type | Default value | Description |
| :--- | :--- | :--- | :--- | :--- |
| 7:3 | DTX1\_RTERM | R/W | 0x0 | termination res value selection for DTX1 path.<br>10000~11111:61 ohms; 00000:50 ohms 00001: 00010: 01111:41 ohms ??? |
| 2 | DTX1\_RTERM\_R0T1 | R/W | 0x0 | termination resistance configuration for RX/TX mode for DTX1 path. 0: used for input resistance termination when DTX1 port is configured as RX input port, 1: used for output driver resistance termination when DTX1 port is configured as RX input port |
| 1 | DTX1\_RTERM\_EN | R/W | 0x1 | enable termination res for DTX1 path. 0:disable 1: enable |
| 0 | DTX1\_VGA\_GAIN\_HIGH | R/W | 0x0 | vga gain selection when DTX1 port is configured as RX input port, combined with REG\_DTX1\_VGA\_GAIN[1:0].<br>REG\_DTX1\_VGA\_GAIN\_HIGH=0: 000:0.7dB, 001:1.7dB, 010:2.7dB, 011:3.7 dB;<br>REG\_DTX1\_VGA\_GAIN\_HIGH=1: 100:2.3dB, 101:3.3dB, 110:4.3dB ,111:5.3dB |


"write_register(0x7c, 0x4B, 0x3A)",
                "write_register(0x7c, 0x37, 0x3A)",
                "write_register(0x7c, 0x5F, 0x3A)",
                "write_register(0x7c, 0x23, 0x3A)",
				
				
				
				
				
				
				


**Table 24 UTX2_PORT_CFG_1**

*   **Name:** UTX2\_PORT\_CFG\_1
*   **I2C Address:** 0x7c
*   **Offset:** 0x17

| Bit | Name | Type | Default value | Description |
| :--- | :--- | :--- | :--- | :--- |
| 7:6 | UTX2\_EQ\_IDAC | R/W | 0x3 | leq stage bias current selection when UTX2 port is configured as RX input port. 00 @13.5Gbps 10 @20Gbps |
| 5:3 | UTX2\_EQ\_MFR | R/W | 0x5 | leq middle-freq resistance selection when UTX2 port is configured as RX input port.000: 111 |
| 2:0 | UTX2\_EQ\_MFC | R/W | 0x6 | leq middle-freq capacitance selection when UTX2 port is configured as RX input port. 000: &nbsp; 111: |

                "write_register(0x7c, 0x17, 0xE8)",
                "write_register(0x7c, 0x2B, 0xE8)",
                "write_register(0x7c, 0x3F, 0xE8)",
                "write_register(0x7c, 0x53, 0xE8)",
				





			
				
				
				
				


				
				
				
				
