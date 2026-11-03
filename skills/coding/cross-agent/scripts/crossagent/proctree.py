"""Worker process-tree ownership, so a worker never outlives the CLI that started it.

On Windows each worker starts suspended inside a Job Object with
`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`; the job handle closes when this process
exits for any reason, which kills the whole tree. On POSIX each worker leads a
new process group that is killed on exit, SIGTERM, or SIGHUP. SIGKILL cannot be
handled there, so the engine also records the worker PID for orphan detection.
"""

from __future__ import annotations

import os
import signal
import subprocess
import threading

if os.name == "nt":
    import ctypes
    from ctypes import wintypes

    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _ntdll = ctypes.WinDLL("ntdll")

    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
    CREATE_SUSPENDED = 0x4
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    STILL_ACTIVE = 259

    class _IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_ulonglong) for name in (
            "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
            "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

    class _BasicLimits(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_longlong), ("PerJobUserTimeLimit", ctypes.c_longlong),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class _ExtendedLimits(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", _BasicLimits), ("IoInfo", _IoCounters),
                    ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

    _kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    _kernel32.CreateJobObjectW.argtypes = (wintypes.LPVOID, wintypes.LPCWSTR)
    _kernel32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD)
    _kernel32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
    _kernel32.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
    _kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
    _kernel32.OpenProcess.restype = wintypes.HANDLE
    _kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    _kernel32.GetExitCodeProcess.argtypes = (wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
    _kernel32.GetProcessTimes.argtypes = (wintypes.HANDLE, *(ctypes.POINTER(ctypes.c_ulonglong),) * 4)
    _ntdll.NtResumeProcess.argtypes = (wintypes.HANDLE,)


def popen_options() -> dict:
    """Extra Popen arguments: start suspended on Windows, in a new session on POSIX."""
    return {"creationflags": CREATE_SUSPENDED} if os.name == "nt" else {"start_new_session": True}


class Owned:
    """Own one started worker's process tree until close()."""

    def __init__(self, process: subprocess.Popen):
        self.process = process
        self.job = None
        self.started = process_started(process.pid)
        self._handlers = {}
        if os.name == "nt":
            try:
                self.job = _job_for(process)
            except OSError:
                self.job = None  # Fall back to taskkill /T; the recorded PID still detects an orphan.
            finally:
                # Never leave a worker suspended, even if the job could not be created.
                _ntdll.NtResumeProcess(wintypes.HANDLE(int(process._handle)))
        elif threading.current_thread() is threading.main_thread():
            for sig in (signal.SIGTERM, signal.SIGHUP):
                self._handlers[sig] = signal.signal(sig, _exit_on_signal)

    def kill(self) -> None:
        """Kill the whole tree; leftover descendants of a finished worker die too."""
        if self.job:
            _kernel32.TerminateJobObject(self.job, 1)
        elif os.name == "nt":
            if self.process.poll() is None:
                subprocess.run(["taskkill", "/PID", str(self.process.pid), "/T", "/F"], capture_output=True)
        else:
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        if self.process.poll() is None:
            self.process.kill()
        self.process.wait()

    def close(self) -> None:
        self.kill()
        if self.job:
            _kernel32.CloseHandle(self.job)
            self.job = None
        for sig, handler in self._handlers.items():
            signal.signal(sig, handler)
        self._handlers = {}


def _exit_on_signal(signum, _frame):
    raise SystemExit(128 + signum)


def _job_for(process: subprocess.Popen):
    job = _kernel32.CreateJobObjectW(None, None)
    if not job:
        raise OSError(ctypes.get_last_error(), "CreateJobObjectW failed")
    limits = _ExtendedLimits()
    limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if (not _kernel32.SetInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
                                              ctypes.byref(limits), ctypes.sizeof(limits))
            or not _kernel32.AssignProcessToJobObject(job, wintypes.HANDLE(int(process._handle)))):
        error = ctypes.get_last_error()
        _kernel32.CloseHandle(job)
        raise OSError(error, "Cannot place the worker in a kill-on-close Job Object")
    return job


def process_started(pid: int) -> str | None:
    """An identity stamp that distinguishes a live PID from a reused one, when available."""
    if os.name == "nt":
        handle = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return None
        try:
            times = [ctypes.c_ulonglong() for _ in range(4)]
            if _kernel32.GetProcessTimes(handle, *(ctypes.byref(value) for value in times)):
                return str(times[0].value)
            return None
        finally:
            _kernel32.CloseHandle(handle)
    try:
        with open(f"/proc/{pid}/stat", encoding="ascii") as handle:
            return handle.read().rsplit(")", 1)[1].split()[19]
    except (OSError, IndexError):
        return None


def alive(pid: int, started: str | None = None) -> bool:
    """Whether the recorded worker is still running; a reused PID is not that worker."""
    if os.name == "nt":
        handle = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        try:
            code = wintypes.DWORD()
            if not _kernel32.GetExitCodeProcess(handle, ctypes.byref(code)) or code.value != STILL_ACTIVE:
                return False
        finally:
            _kernel32.CloseHandle(handle)
    else:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            pass
    return started is None or process_started(pid) in (None, started)
