import ctypes
from ctypes import Structure, c_int, c_uint, c_uint8, c_uint16, c_uint32, c_char, POINTER, c_void_p

# CONFIG
LIB_PATH = "libcontrolcan.so"

# LIB DEFs
DeviceType = 4 # [ref. 2.1.1] DEV_USBCAN2: USBCAN-2A, USBCAN-2C, CANalyst-II, MiniPCIe-CAN

# Load DLL
lib = ctypes.CDLL(LIB_PATH) # future: add file check


# ref. typedef  struct  _VCI_BOARD_INFO{} VCI_BOARD_INFO;
class VCI_BOARD_INFO(Structure):
    _fields_ = [("hw_Version",      c_uint16), 
                ("fw_Version",      c_uint16), 
                ("dr_Version",      c_uint16), 
                ("in_Version",      c_uint16),
                ("irq_Num",         c_uint16), 
                ("can_Num",         c_uint8),
                ("str_Serial_Num",  c_char * 20), 
                ("str_hw_Type",     c_char * 40), 
                ("Reserved",        c_uint16 * 4)]

# ref. typedef  struct  _VCI_CAN_OBJ{} VCI_CAN_OBJ;
class VCI_CAN_OBJ(Structure):
    _fields_ = [("ID",          c_uint32),
                ("TimeStamp",   c_uint32),
                ("TimeFlag",    c_uint8),
                ("SendType",    c_uint8),
                ("RemoteFlag",  c_uint8), # Whether it is a remote frame
                ("ExternFlag",  c_uint8), # Whether it is an extended frame
                ("DataLen",     c_uint8),
                ("Data",        c_uint8 * 8),
                ("Reserved",    c_uint8 * 3)]

# ref. typedef struct _INIT_CONFIG{} VCI_INIT_CONFIG;
class VCI_INIT_CONFIG(Structure):
    _fields_ = [("AccCode",     c_uint32),
                ("AccMask",     c_uint32),
                ("Reserved",    c_uint32),
                ("Filter",      c_uint8),
                ("Timing0",     c_uint8),
                ("Timing1",     c_uint8),
                ("Mode",        c_uint8)]

# ref. typedef struct _VCI_FILTER_RECORD{} VCI_FILTER_RECORD;
class VCI_FILTER_RECORD(Structure):
    _fields_ = [("ExtFrame",    c_uint32),
                ("Start",       c_uint32),
                ("End",         c_uint32)]
    
# check if each wrapper class objects are of same size as in static lib header definition.
assert (ctypes.sizeof(VCI_BOARD_INFO), ctypes.sizeof(VCI_CAN_OBJ), ctypes.sizeof(VCI_INIT_CONFIG)) == (80, 24, 16)

### Public APIs
# ref. EXTERN_C DWORD VCI_OpenDevice(DWORD DeviceType,DWORD DeviceInd,DWORD Reserved);
VCI_OpenDevice = lib.VCI_OpenDevice
VCI_OpenDevice.argtypes = [c_uint32, c_uint32, c_uint32]
VCI_OpenDevice.restype  = c_uint32

# ref. EXTERN_C DWORD VCI_CloseDevice(DWORD DeviceType,DWORD DeviceInd);
VCI_CloseDevice = lib.VCI_CloseDevice
VCI_CloseDevice.argtypes = [c_uint32, c_uint32]
VCI_CloseDevice.restype  = c_uint32

# ref. EXTERN_C DWORD VCI_InitCAN(DWORD DeviceType, DWORD DeviceInd, DWORD CANInd, PVCI_INIT_CONFIG pInitConfig);
VCI_InitCAN = lib.VCI_InitCAN
VCI_InitCAN.argtypes = [c_uint32, c_uint32, c_uint32, POINTER(VCI_INIT_CONFIG)]
VCI_InitCAN.restype  = c_uint32

# ref. EXTERN_C DWORD VCI_ReadBoardInfo(DWORD DeviceType,DWORD DeviceInd,PVCI_BOARD_INFO pInfo);
VCI_ReadBoardInfo = lib.VCI_ReadBoardInfo
VCI_ReadBoardInfo.argtypes = [c_uint32, c_uint32, POINTER(VCI_BOARD_INFO)]
VCI_ReadBoardInfo.restype  = c_uint32

# ref. EXTERN_C DWORD VCI_SetReference(DWORD DeviceType,DWORD DeviceInd,DWORD CANInd,DWORD RefType,PVOID pData);
VCI_SetReference = lib.VCI_SetReference
VCI_SetReference.argtypes = [c_uint32, c_uint32, c_uint32, c_uint32, c_void_p]
VCI_SetReference.restype  = c_uint32

# ref. EXTERN_C ULONG VCI_GetReceiveNum(DWORD DeviceType,DWORD DeviceInd,DWORD CANInd);
VCI_GetReceiveNum = lib.VCI_GetReceiveNum
VCI_GetReceiveNum.argtypes = [c_uint32, c_uint32, c_uint32]
VCI_GetReceiveNum.restype  = c_uint32

# ref. EXTERN_C DWORD VCI_ClearBuffer(DWORD DeviceType,DWORD DeviceInd,DWORD CANInd);
VCI_ClearBuffer = lib.VCI_ClearBuffer
VCI_ClearBuffer.argtypes = [c_uint32, c_uint32, c_uint32]
VCI_ClearBuffer.restype  = c_uint32

# ref. EXTERN_C DWORD VCI_StartCAN(DWORD DeviceType,DWORD DeviceInd,DWORD CANInd);
VCI_StartCAN = lib.VCI_StartCAN
VCI_StartCAN.argtypes = [c_uint32, c_uint32, c_uint32]
VCI_StartCAN.restype  = c_uint32

# ref. EXTERN_C DWORD VCI_ResetCAN(DWORD DeviceType,DWORD DeviceInd,DWORD CANInd);
VCI_ResetCAN = lib.VCI_ResetCAN
VCI_ResetCAN.argtypes = [c_uint32, c_uint32, c_uint32]
VCI_ResetCAN.restype  = c_uint32

# ref. EXTERN_C ULONG VCI_Transmit(DWORD DeviceType,DWORD DeviceInd,DWORD CANInd,PVCI_CAN_OBJ pSend,UINT Len);
VCI_Transmit = lib.VCI_Transmit
VCI_Transmit.argtypes = [c_uint32, c_uint32, c_uint32, POINTER(VCI_CAN_OBJ), c_uint]
VCI_Transmit.restype  = c_uint32

# ref. EXTERN_C ULONG VCI_Receive(DWORD DeviceType,DWORD DeviceInd,DWORD CANInd,PVCI_CAN_OBJ pReceive,UINT Len,INT WaitTime);
VCI_Receive = lib.VCI_Receive
VCI_Receive.argtypes = [c_uint32, c_uint32, c_uint32, POINTER(VCI_CAN_OBJ), c_uint, c_int]
VCI_Receive.restype  = c_uint32

# ref. EXTERN_C DWORD  VCI_UsbDeviceReset(DWORD DevType,DWORD DevIndex,DWORD Reserved);
VCI_UsbDeviceReset = lib.VCI_UsbDeviceReset
VCI_UsbDeviceReset.argtypes = [c_uint32, c_uint32, c_uint32]
VCI_UsbDeviceReset.restype  = c_uint32

# ref. EXTERN_C DWORD  VCI_FindUsbDevice2(PVCI_BOARD_INFO pInfo);
VCI_FindUsbDevice2 = lib.VCI_FindUsbDevice2
VCI_FindUsbDevice2.argtypes = [POINTER(VCI_BOARD_INFO)]
VCI_FindUsbDevice2.restype  = c_uint32

