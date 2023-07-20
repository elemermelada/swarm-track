RUN_APP = input("Input case: ")

if RUN_APP.upper() == "DSN1":
    from cases.DSN1 import *

if RUN_APP.upper() == "MEX1":
    from cases.MEX1 import *

if RUN_APP.upper() == "CART":
    from cases.CART import *
