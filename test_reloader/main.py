import time
from class_reloaded import class_reloaded
import utils_reloaded
def main_loop():
    print("start main loop")
    index = 0
    while True:
        value = utils_reloaded.get_closure_value()
        print(value)
        time.sleep(1)
        index += 1
        if index == 2:
            print('try to hotfix')
            from reloader_utils import run_all_hotfix_in_dir
            run_all_hotfix_in_dir('hotfix_file')
            print("hotfix end")
main_loop()