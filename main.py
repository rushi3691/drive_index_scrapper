import threading
from queue import Queue
from logger import logger, obj_processed

from scrapper import scrapper

from config import folders_path, WORKERS

def main():
    global obj_processed
    check = input("give url or filename: ")
    if check.startswith("https"):
        print(check)
        with open(folders_path, "w") as fl:
            fl.write(check)
        

    lock = threading.Lock()
    q = Queue()
    obj_processed = 0
    with open(folders_path) as fl:
        for i in fl:
            q.put([i.strip(), 0])

    with open(folders_path, "w") as fl:
        fl.write("")

    for i in range(WORKERS):
        thread = threading.Thread(
            name=f"Thread_{i}", target=scrapper, args=(q, lock,))
        thread.daemon = True
        thread.start()

    q.join()


main()