import msvcrt
import time

running = True


def clear_kb_buff():
    while msvcrt.kbhit():
        msvcrt.getch()


def wait_input(wait_time):
    clear_kb_buff()
    start_time = time.perf_counter()
    end_time = start_time + wait_time

    interrupt = False
    while not interrupt and time.perf_counter() < end_time:
        interrupt = msvcrt.kbhit()
        if interrupt:
            while msvcrt.kbhit():
                msvcrt.getch()

    return interrupt


def cl_input(prompt):
    inp = input(prompt)
    clear_kb_buff()
    return inp


while running:
    print("Pulse")
    if wait_input(1):
        print("Interrupt")
        cmd = cl_input(">")
        if cmd == "quit":
            running = False
        else:
            print("Execution resumes")
