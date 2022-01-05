import keyboard
import time


tests = """$$xno
/info $tsla
/info $$btc
/news $tsla
/news $$btc
/stat $tsla
/stat $$btc
/cap $tsla
/cap $$btc
/dividend $tsla
/dividend $msft
/dividend $$btc
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
