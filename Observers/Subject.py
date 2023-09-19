class Subject:
    def __init__(self):
        self._observers = []
        self._keys = []

    def add_observer(self, observer, key):
        if key not in self._keys:
            self._observers.append(observer)
            self._keys.append(key)

    def remove_observer(self, observer, key):
        self._observers.remove(observer)
        self._observers.remove(key)

    def notify_observers(self):
        for observer in self._observers:
            observer.update()

subject = Subject()