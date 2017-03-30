class TimeElapsed:
    def __init__(self, name: str):
        self.name = name
        self.begin = self._current_time()
        self.end = None

    def _current_time(self):
        import time
        return time.time()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = self._current_time()
        print('{} - time elapsed: {:.4f}'.format(self.name, self.end - self.begin))
