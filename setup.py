RUN_APP = input("Input case: ")

if RUN_APP.upper() == "DSN1":
    from cases.DSN_SPICE import *

if RUN_APP.upper() == "DSN2":
    from cases.DSN_PROP import *

if RUN_APP.upper() == "DSN3":
    from cases.DSN_SENS import *

if RUN_APP.upper() == "MEX1":
    from cases.TW_SIMPLE_DOPPLER import *

if RUN_APP.upper() == "MEX2":
    from cases.TW_SIMPLE_RANGE import *

if RUN_APP.upper() == "MEX3":
    from cases.TW_PROP import *

if RUN_APP.upper() == "CART":
    from cases.CART import *

print("Add breakpoint here to hold plots")
