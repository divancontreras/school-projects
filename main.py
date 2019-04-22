from threading import Thread
from time import sleep
from serial import Serial
from queue import Queue
from pynput.mouse import Button, Controller

mouse = Controller()


class SerialListener(Serial):
    def __init__(self, port, baudrate):
        super().__init__(self, port, baudrate)
        self.open()
        self.jobs = Queue()
        Thread(target=self.listen, daemon=True).start()
        if not self.open:
            raise Exception("Serial connection failed!")

    def listen(self):
        while True:
            read = self.read_until()
            self.jobs.put(read)


class MouseController:
    def __init__(self, port, baudrate):
        self.listener = SerialListener(port, baudrate)
        self.mouse = Mouse()
        self.jobs_map = dict(r=self.mouse.move_right,
                             l=self.mouse.move_left,
                             u=self.mouse.move_up,
                             d=self.mouse.move_down,
                             x=self.mouse.right_click,
                             z=self.mouse.left_click)
        Thread(target=self.worker, daemon=True).start()

    def worker(self):
        while True:
            try:
                job = self.listener.jobs.get()
                self.jobs_map[job]()
            except KeyError:
                breakpoint()
                pass


class Mouse(Controller):
    def __init__(self):
        super().__init__(self)
        Thread(target=self.mouse_tracker, daemon=True).start()

    def move_right(self):
        self.move(5, 0)

    def move_left(self):
        self.move(-5, 0)

    def move_up(self):
        self.move(0, 5)

    def move_down(self):
        self.move(0, -5)

    def right_click(self):
        self.press(Button.right)
        self.release(Button.right)

    def left_click(self):
        self.press(Button.left)
        self.release(Button.left)

    def mouse_tracker(self):
        print(self.position)
        sleep(.25)


if __name__ == "__main__":
    br = 9600
    port_name = "COM5"
    m = MouseController(port_name, br)
