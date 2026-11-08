from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal, Slot

class ObservableDict(QObject):
    value_change = Signal(str, object)
    def __init__(self, data=None):
        super().__init__()
        self._data = data if data is not None else {}

    def __setitem__(self,key,value):
        self._data[key] = value
        self.value_change.emit(key, value)

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

@dataclass
class AppState:
    active_cameras:  int = 0
