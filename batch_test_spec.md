
help me create a batch test python file:

(1) leveage the verify_instrument.py and verify_dut_client_standalone. It is actually to run verify_instrument.py multiple times with different dutclient seting, saving different project name and report.
(2) An independent file contains the batch run config: each run has same test ids, different i2c commands and macros, such as multiple `write_register(0x7c, 0x02, 0x01)`(i2c) and `eq 3`(macro).
    All of them shall be in config file.
(3) A summary report shall show up in end of batch file to tell user items result(Results Received: ID: 119042, Pass: False, Margin: -999.0) of each run.
(4) do not run verify this batch python file because of long time. Let me review the code once completed.