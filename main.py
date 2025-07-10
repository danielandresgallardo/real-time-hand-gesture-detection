from multiprocessing import Process, Queue, Event
from gesture_detector import run_gesture_detection
from hud_display import run_hud
import time

if __name__ == "__main__":
    queue = Queue()
    stop_event = Event()

    p1 = Process(target=run_gesture_detection, args=(queue, stop_event))
    p2 = Process(target=run_hud, args=(queue, stop_event))
    p1.start()
    time.sleep(1)
    p2.start()
    p1.join()
    p2.join()