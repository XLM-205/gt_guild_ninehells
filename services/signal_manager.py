"""Initialization Shutdown manager"""
import signal
from typing import Callable, Dict


class SigManager:
    # For "Termination", "Interrupt" (Ctrl+C), "Abort" (abort()), "Floating Point Error" ( x/0 )
    _sig_callbacks: Dict = {"SIGTERM": [signal.SIGTERM, None], "SIGINT": [signal.SIGINT, None],
                            "SIGABRT": [signal.SIGABRT, None], "SIGFPE": [signal.SIGFPE, None]}

    def set_callback(self, sig_id: str, callback: Callable):
        if sig_id.upper() in self._sig_callbacks and callback is not None:
            self._sig_callbacks[sig_id][1] = callback
            signal.signal(self._sig_callbacks[sig_id][0], callback)

    def get_supported(self):
        return list(self._sig_callbacks.keys())

    def get_callbacks(self):
        return list(self._sig_callbacks.items())


SignalManager = SigManager()
