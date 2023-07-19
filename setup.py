RUN_APP = input("Input case: ")

if RUN_APP == "DSN1" or RUN_APP == "dsn1":
    from cases.DSN1 import *

if RUN_APP == "MEX1" or RUN_APP == "mex1":
    from cases.MEX1 import *

if RUN_APP == "CART" or RUN_APP == "cart":
    from cases.CART import *
