import time
import threading
from collections import deque

import can
from can import BusABC, Message
from can.exceptions import CanOperationError, CanInitializationError

from controlcan import DeviceType
from CANChannel import CANChannel, CanError


class Waveshare_USB_CAN_B_Bus(BusABC):
    def __init__(self, channel=0, bitrate=500_000, dev_type=DeviceType, device_index=0, poll_interval=0.001, tx_timeout=1.0, can_filters=None, **kwargs):
        super().__init__(channel, can_filters=can_filters, **kwargs)
        
        self._CANChannel = None
        self._lock = threading.RLock()
        self._rxq = deque()
        self._poll = poll_interval
        self._tx_timeout = tx_timeout
        
        self.channel_info = f"ControlCAN dev{dev_type}:{device_index} ch{channel} @ {bitrate}"
        
        try:
            self._CANChannel = CANChannel(dev_type, device_index, int(channel)).open(bitrate)
        except (CanError, ValueError) as e:
            raise CanInitializationError(str(e)) from e

    def send(self, msg:can.Message, timeout=None): # [ref. https://python-can.readthedocs.io/en/stable/bus.html#can.BusABC.send]
        data_frame = CANChannel.make_VCI_CAN_OBJ(msg.arbitration_id,
                                                 bytes(msg.data) if not(msg.is_remote_frame) else b"", # if remote_frame, data is empty, DataLen is expected data
                                                 ExternFlag=int(msg.is_extended_id), 
                                                 RemoteFlag=int(msg.is_remote_frame))
        
        if msg.is_remote_frame:
            data_frame.DataLen = msg.dlc   # make_obj() sets VCI_CAN_OBJ().DataLen = 0, but for remote DataLen is length of expected data
            
        deadline = time.monotonic() + (self._tx_timeout if timeout is None else timeout)
        
        while True:
            try:
                with self._lock:
                    if self._CANChannel is None:
                        raise CanOperationError("Waveshare USB-CAN-B bus is shut down")
                    n = self._CANChannel.transmit([data_frame])
            except CanError as e:
                raise CanOperationError(str(e)) from e
            if n == 1:
                return
            if time.monotonic() >= deadline:
                raise CanOperationError("transmit timeout (tx buffer full)")
            time.sleep(self._poll)

    def _recv_internal(self, timeout): # [ref. https://python-can.readthedocs.io/en/stable/internal-api.html#can.BusABC._recv_internal]
        # https://python-can.readthedocs.io/en/stable/bus.html#can.BusABC.recv;        
        deadline = None if timeout is None else time.monotonic() + timeout
        
        while True:
            if self._rxq:   # if thre's data in rx_queue, pull them first
                msg = self._VCI_CAN_OBJ_to_CANMessage(self._rxq.popleft())
                return msg, False   # During BusABC recv() call, it calls _recv_internal() and returns only the msg.
            
            try:
                with self._lock:
                    if self._CANChannel is None:
                        raise CanOperationError("Waveshare USB-CAN-B bus is shut down")
                    VCI_CAN_OBJ_frame = self._CANChannel.receive(wait_ms=0)   # never block while holding the lock
            except CanError as e:
                raise CanOperationError(str(e)) from e
            
            if VCI_CAN_OBJ_frame:
                self._rxq.extend(VCI_CAN_OBJ_frame)
                continue
            
            if deadline is not None and time.monotonic() >= deadline:
                return None, False
            
            time.sleep(self._poll)

    @staticmethod
    def _VCI_CAN_OBJ_to_CANMessage(data_frame) -> can.Message:
        """VCI_CAN_OBJ to can.Message format conversion"""
        is_remote = bool(data_frame.RemoteFlag)        
        msg = Message(arbitration_id    = data_frame.ID,
                      is_extended_id    = bool(data_frame.ExternFlag),
                      is_remote_frame   = is_remote,
                      dlc               = data_frame.DataLen,
                      data              = b"" if is_remote else bytes(data_frame.Data[:data_frame.DataLen]),
                      timestamp         = time.time())        
        return msg


    def reset_rx(self): # custom method outside BusABC
        with self._lock:
            if self._CANChannel is None:
                raise CanOperationError("Waveshare USB-CAN-B bus is shut down")
            self._rxq.clear()
            self._CANChannel.clear_buffer()

    def shutdown(self): # [ref. https://python-can.readthedocs.io/en/stable/bus.html#can.BusABC.shutdown]
        super().shutdown()
        with self._lock:
            if self._CANChannel is not None:
                self._CANChannel.close()
                self._CANChannel = None


can.interfaces.BACKENDS["Waveshare_USB_CAN_B"] = (__name__, "Waveshare_USB_CAN_B_Bus")



## Test Cases
if __name__ == "__main__":
    a = Waveshare_USB_CAN_B_Bus(channel=0, bitrate=1_000_000)
    b = Waveshare_USB_CAN_B_Bus(channel=1, bitrate=1_000_000)
    res = []

    def check(name, ok):
        res.append(bool(ok)); print(f"[{'PASS' if ok else 'FAIL'}] {name}")

    def same(m, id, data, ext=False, rtr=False):
        return (m is not None and m.arbitration_id == id and m.is_extended_id == ext
                and m.is_remote_frame == rtr and bytes(m.data) == bytes(data))

    try:
        a.reset_rx(); b.reset_rx()

        # data frames, both directions
        a.send(Message(arbitration_id=0x123, data=bytes(range(1, 9)), is_extended_id=False))
        check("a->b std, 8 bytes", same(b.recv(0.5), 0x123, bytes(range(1, 9))))
        b.send(Message(arbitration_id=0x581, data=[0x4B, 0x41, 0x60, 0, 0x50, 0x02, 0, 0], is_extended_id=False))
        check("b->a std (SDO-reply shaped)", same(a.recv(0.5), 0x581, [0x4B, 0x41, 0x60, 0, 0x50, 0x02, 0, 0]))

        # id/length edge cases
        a.send(Message(arbitration_id=0x1ABCDE, data=[0xDE, 0xAD], is_extended_id=True))
        check("a->b ext 29-bit, 2 bytes", same(b.recv(0.5), 0x1ABCDE, [0xDE, 0xAD], ext=True))
        a.send(Message(arbitration_id=0x7FF, data=[], is_extended_id=False))
        check("a->b max std id, 0 bytes", same(b.recv(0.5), 0x7FF, []))
        a.send(Message(arbitration_id=0x000, data=[0x01, 0x00], is_extended_id=False))
        check("a->b id 0x000 (NMT-shaped)", same(b.recv(0.5), 0x000, [0x01, 0x00]))

        # remote frame
        a.send(Message(arbitration_id=0x701, is_remote_frame=True, dlc=1, is_extended_id=False))
        m = b.recv(0.5)
        check("a->b remote frame, dlc=1", same(m, 0x701, [], rtr=True) and m.dlc == 1)

        # SDO-style request/reply round trip
        a.send(Message(arbitration_id=0x601, data=[0x40, 0x41, 0x60, 0, 0, 0, 0, 0], is_extended_id=False))
        req = b.recv(0.5)
        b.send(Message(arbitration_id=0x581, data=[0x4B, 0x41, 0x60, 0, 0x50, 0x02, 0, 0], is_extended_id=False))
        rep = a.recv(0.5)
        check("SDO round trip (0x601 -> 0x581)", same(req, 0x601, [0x40, 0x41, 0x60, 0, 0, 0, 0, 0]) and rep is not None and rep.arbitration_id == 0x581)

        # burst: order and count
        for i in range(50):
            a.send(Message(arbitration_id=0x200 + i, data=[i], is_extended_id=False))
        got = [b.recv(0.5) for _ in range(50)]
        check("burst of 50, all received, in order",
              all(m is not None for m in got) and [m.arbitration_id for m in got] == [0x200 + i for i in range(50)])

        # software filter (python-can applies it, our _recv_internal returns filtered=False)
        b.set_filters([{"can_id": 0x300, "can_mask": 0x7FF, "extended": False}])
        a.send(Message(arbitration_id=0x2FF, data=[1], is_extended_id=False))
        a.send(Message(arbitration_id=0x300, data=[2], is_extended_id=False))
        check("software filter passes 0x300 only", same(b.recv(0.5), 0x300, [2]))
        b.set_filters(None)

        # timeout, nothing pending
        t0 = time.monotonic()
        check("recv(0.2) on idle bus returns None after ~0.2 s", b.recv(0.2) is None and 0.15 < time.monotonic() - t0 < 0.5)
        check("recv(0) returns immediately", b.recv(0) is None)

        # reset_rx drops stale frames
        a.send(Message(arbitration_id=0x400, data=[9], is_extended_id=False))
        time.sleep(0.1); b.reset_rx()
        check("reset_rx discards waiting frame", b.recv(0.2) is None)

        # closed-bus guard
        a.shutdown()
        try:
            a.send(Message(arbitration_id=0x1, data=[], is_extended_id=False)); check("send after shutdown raises", False)
        except can.exceptions.CanOperationError:
            check("send after shutdown raises", True)
    finally:
        a.shutdown(); b.shutdown()
        print(f"\n{sum(res)}/{len(res)} passed")
        
        