import time

import keyboard

tests = """$$xno
$tsla
/intra $tsla
/intra $$btc
/chart $tsla
/chart $$btc
/help
/trending""".split(
    "\n"
)

print("press enter to start")
keyboard.wait("enter")

for test in tests:
    print(test)
    keyboard.write(test)
    time.sleep(1)
    keyboard.press_and_release("enter")
