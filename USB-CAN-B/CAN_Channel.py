from lib.controlcan import (
    DeviceType,
    VCI_BOARD_INFO, VCI_CAN_OBJ, VCI_INIT_CONFIG,
    VCI_OpenDevice, VCI_CloseDevice, VCI_InitCAN, VCI_ReadBoardInfo,
    VCI_GetReceiveNum, VCI_ClearBuffer, VCI_StartCAN, VCI_ResetCAN,
    VCI_Transmit, VCI_Receive, VCI_UsbDeviceReset, VCI_FindUsbDevice2
)

# status code enums
STATUS_OK, STATUS_ERR = 1, 0
VCI_ERR = 0xFFFFFFFF # unsigned equivalnet of (signed int)-1


BAUDRATE_TABLE = {
    # baudrate: [Timing0, Timing1] -->> [ref. 2.1.4] VCI_INIT_CONFIG
    1_000_000:  [0x00, 0x14],
    800_000:    [0x00, 0x16],
    666_000:    [0x80, 0xB6],
    500_000:    [0x00, 0x1C],
    400_000:    [0x80, 0xFA],
    250_000:    [0x01, 0x1C],
    200_000:    [0x81, 0xFA],
    125_000:    [0x03, 0x1C],
    100_000:    [0x04, 0x1C],
    80_000:     [0x83, 0xFF],
    50_000:     [0x09, 0x1C],
    40_000:     [0x87, 0xFF],
    20_000:     [0x18, 0x1C],
    10_000:     [0x31, 0x1C],
    5_000:      [0xBF, 0xFF],
}


class CanError(Exception):
    pass



class CANChannel:
    _devs = {}  # holds list of currenlty opened device interfaces and channels
                # {}          -->> init
                # {(4, 0): 1} -->> adapter 0 open, one channel in use (ch0 only)
                # {(4, 0): 2} -->> adapter 0 open, two channels in use (ch0 and ch1)

    def __init__(self, DevType=DeviceType, DevInd=0, CANInd=0, rx_size=2500):
        self.DevType    = DevType
        self.DevInd     = DevInd
        self.CANInd     = CANInd
        
        if rx_size < 2500: # [ref. 2.2.10] VCI_Receive
            raise ValueError(f"rx_size must be >= 2500 (vendor requirement)")
        
        self._rx_size   = rx_size
        self._rx_buff   = (VCI_CAN_OBJ * rx_size)()
        self._open      = False
        self._started   = False
        
    def __enter__(self): return self
    
    def __exit__(self, *a): self.close()


    def open(self, baudrate=500_000, Mode=0, AccCode=0, AccMask=0xFFFFFFFF, Filter=1, start=True):
        """
        This function is used to connect devices and then initialize the specified CAN channel.        
        Args:

            Mode: Operating mode, 0 = normal operation, 1 = Listen-only mode, 2 = spontaneous admission and sending test mode.
        Returns:
            CANChannel: Returns current CANChannel object instanse (i.e., self)
        """
        if baudrate not in BAUDRATE_TABLE:
            raise CanError(f"unsupported bitrate {baudrate}")
        
        key = (self.DevType, self.DevInd)
        
        if key not in self._devs: # if the device has not been opened yet...
            if VCI_OpenDevice(self.DevType, self.DevInd, 0) != STATUS_OK:
                raise CanError("VCI_OpenDevice failed")
            self._devs[key] = 0
            
        self._devs[key] += 1
        self._open = True
        
        cfg = VCI_INIT_CONFIG()
        cfg.AccCode = AccCode
        cfg.AccMask = AccMask
        cfg.Filter  = Filter
        cfg.Mode    = Mode
        cfg.Timing0, cfg.Timing1 = BAUDRATE_TABLE[baudrate]
        
        try:
            if VCI_InitCAN(self.DevType, self.DevInd, self.CANInd, cfg) != STATUS_OK:
                raise CanError("VCI_InitCAN failed")
            if start:
                self.start()
                
        except CanError:
            self.close()
            raise
        
        return self

    def start(self):
        """This function is used to start the CAN controller and the internal interrupt reception function of the adapter."""
        if VCI_StartCAN(self.DevType, self.DevInd, self.CANInd) != STATUS_OK:
            raise CanError("VCI_StartCAN failed")
        self._started = True

    def reset(self):
        """This function is used to reset the CAN controller."""
        if VCI_ResetCAN(self.DevType, self.DevInd, self.CANInd) != STATUS_OK:
            raise CanError("VCI_ResetCAN failed")
        self._started = False

    def close(self):
        """This function is used to reset the CAN controller and then close the connection."""
        if not self._open:
            return
        
        self._open = False
        
        if self._started:
            VCI_ResetCAN(self.DevType, self.DevInd, self.CANInd)
            self._started = False
            
        key = (self.DevType, self.DevInd)
        self._devs[key] -= 1
        
        if self._devs[key] == 0:
            del self._devs[key]
            VCI_CloseDevice(self.DevType, self.DevInd)


    
    @staticmethod
    def make_VCI_CAN_OBJ(ID, data=b"", ExternFlag=0, RemoteFlag=0, SendType=0) -> VCI_CAN_OBJ:
        if len(data) > 8:
            raise ValueError("DataLen > 8")
        
        vco = VCI_CAN_OBJ()
        vco.ID          = ID
        vco.ExternFlag  = ExternFlag
        vco.RemoteFlag  = RemoteFlag
        vco.SendType    = SendType
        vco.DataLen     = len(data)
        
        for i, bit in enumerate(data):
            vco.Data[i] = bit
            
        return vco


    def transmit(self, VCI_CAN_OBJ_frames):
        n = len(VCI_CAN_OBJ_frames)
        data_frame_array = (VCI_CAN_OBJ * n)(*VCI_CAN_OBJ_frames)
        r = VCI_Transmit(self.DevType, self.DevInd, self.CANInd, data_frame_array, n)
        if r == VCI_ERR:
            raise CanError("VCI_Transmit failed")
        return r

    def receive(self, wait_ms=0):
        r = VCI_Receive(self.DevType, self.DevInd, self.CANInd, self._rx_buff, self._rx_size, wait_ms)
        if r == VCI_ERR:
            raise CanError("VCI_Receive failed")
        
        VCI_CAN_OBJ_frames = []
        for i in range(r):
            VCI_CAN_OBJ_frames.append(VCI_CAN_OBJ.from_buffer_copy(self._rx_buff[i]))
                    
        return VCI_CAN_OBJ_frames

    def pending(self):
        """This function is used to specify the received but has not been read frames in the designated receiving buffer."""
        r = VCI_GetReceiveNum(self.DevType, self.DevInd, self.CANInd)
        if r == VCI_ERR:
            raise CanError("VCI_GetReceiveNum failed")
        return r

    def clear_buffer(self):
        """This function is used to clear the receive and send buffer of the designated channel specified by USB-CAN adapter."""
        if VCI_ClearBuffer(self.DevType, self.DevInd, self.CANInd) != STATUS_OK:
            raise CanError("VCI_ClearBuffer failed")

    def board_info(self) -> VCI_BOARD_INFO:
        """This function is used to read the adapter hardware information."""
        info = VCI_BOARD_INFO()
        if VCI_ReadBoardInfo(self.DevType, self.DevInd, info) != STATUS_OK:
            raise CanError("VCI_ReadBoardInfo failed")
        return info
    
    def usb_reset(self):
        """Reset USB-CAN adapter, need to re-open the device after reset by using VCI_OpenDevice."""
        r = VCI_UsbDeviceReset(self.DevType, self.DevInd, 0)
        if r != STATUS_OK:
            raise CanError("VCI_UsbDeviceReset failed")        
        self._open      = False
        self._started   = False
        self._devs.pop((self.DevType, self.DevInd), None)
        return r

    @staticmethod
    def usb_find():
        """When the same PC using multiple USB-CAN, user can use this function to find the current device."""
        info = (VCI_BOARD_INFO *32)() # Assuming max 32 devices
        r = VCI_FindUsbDevice2(info)
        return r
        
        
    
    
    
## TEST CASES
if __name__ == "__main__":
    print(__file__)
    
    print(CANChannel.usb_find())
    
    ch = CANChannel(DeviceType, 0, 0).open(500_000)     # open + init + start
    
    try:
        info = ch.board_info()
        print("#######################################")
        print("hw_Version    ", f"v{info.hw_Version >> 8:X}.{info.hw_Version & 0xFF:02X}")
        print("fw_Version    ", f"v{info.fw_Version >> 8:X}.{info.fw_Version & 0xFF:02X}")
        print("dr_Version    ", f"v{info.dr_Version >> 8:X}.{info.dr_Version & 0xFF:02X}")
        print("in_Version    ", f"v{info.in_Version >> 8:X}.{info.in_Version & 0xFF:02X}")
        print("irq_Num       ", info.irq_Num, "(system reserved)")
        print("can_Num       ", info.can_Num, "CAN channels")
        print("str_Serial_Num", info.str_Serial_Num.decode(errors="replace"))
        print("str_hw_Type   ", info.str_hw_Type.decode(errors="replace"))
        print("Reserved      ", list(info.Reserved), "(system reserved)")

        print("#######################################")
        print("pending before clear:", ch.pending())
        ch.clear_buffer()
        print("pending after clear:", ch.pending())
        print("#######################################")

        print("transmit:", ch.transmit([CANChannel.make_VCI_CAN_OBJ(0x7FF, b"\x01\x02", SendType=1)]))  # single-shot, no ack needed

        
        for o in ch.receive(wait_ms=100):
            print(f"rx id=0x{o.ID:03X} dlc={o.DataLen} data={bytes(o.Data[:o.DataLen]).hex()}")

        ch.reset(); ch.start()                           # stop/start cycle
    finally:
        ch.close()
        
    print("#######################################")
    print("devs after close:", CANChannel._devs)         # expect {}