executed = False
defaulting = False
default = None

while not executed:
    RUN_APP = default
    if not defaulting:
        RUN_APP = input("Input case: ")

    if RUN_APP.upper() == "DSN1":
        executed = True
        from cases.DSN_SENS import *

    if RUN_APP.upper() == "TW1":
        executed = True
        from cases.TW_SENS import *

    if not executed:
        if default is None:
            print("Add a default case first")
            continue
        print("Running default case:", default)
        defaulting = True


print("Add breakpoint here to hold plots")
