executed = False
defaulting = False
default = "TWMSE"

print("By Elemer 😘")

while not executed:
    RUN_APP = default
    if not defaulting:
        RUN_APP = input(f"Input case{'' if default is None else f' [{default}]'}: ")

    if RUN_APP.upper() == "PROP":
        executed = True
        from cases.PROP_VS_SPICE import *

    if RUN_APP.upper() == "DSNS":
        executed = True
        from cases.DSN_SENS import *

    if RUN_APP.upper() == "TWS":
        executed = True
        from cases.TW_SENS import *

    if RUN_APP.upper() == "TWD":
        executed = True
        from cases.TW_DISTR import *

    if RUN_APP.upper() == "DSNMSO":
        executed = True
        from cases.DSN_MEX_SIMPLE_OBS import *

    if RUN_APP.upper() == "DSNMSA":
        executed = True
        from cases.DSN_MEX_SIMPLE_ALT import *

    if RUN_APP.upper() == "DSNMSE":
        executed = True
        from cases.DSN_MEX_SIMPLE_EST import *

    if RUN_APP.upper() == "DSNMBE":
        executed = True
        from cases.DSN_MEX_BATCH_EST import *

    if RUN_APP.upper() == "DSNMBO":
        executed = True
        from cases.DSN_MEX_BATCH_OBS import *

    if RUN_APP.upper() == "DSNMRE":
        executed = True
        from cases.DSN_MEX_RANGE_EST import *

    if RUN_APP.upper() == "DSNMRO":
        executed = True
        from cases.DSN_MEX_RANGE_OBS import *

    if RUN_APP.upper() == "TWMSE":
        executed = True
        from cases.TW_MEX_SIMPLE_EST import *

    if RUN_APP.upper() == "TWMSO":
        executed = True
        from cases.TW_MEX_SIMPLE_OBS import *

    if not executed:
        if default is None:
            print("Add a default case first")
            continue
        print("Running default case:", default)
        defaulting = True

print("Add breakpoint here to hold plots")
