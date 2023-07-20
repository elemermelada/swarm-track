RUN_APP = input("Input case: ")

if RUN_APP.upper() == "DSN1":
    from cases.DSN1 import *

if RUN_APP.upper() == "MEX1":
    from cases.TW_SIMPLE_DOPPLER import *

if RUN_APP.upper() == "MEX2":
    from cases.TW_SIMPLE_RANGE import *

if RUN_APP.upper() == "CART":
    from cases.CART import *

print("Add breakpoint here to hold plots")
