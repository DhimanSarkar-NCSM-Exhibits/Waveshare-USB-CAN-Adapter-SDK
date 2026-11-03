
#python3.8.0 64-bit (python 32-bit requires a 32-bit DLL)
#
from ctypes import *
 
VCI_USBCAN2 = 4
STATUS_OK = 1
class VCI_INIT_CONFIG(Structure):  
    _fields_ = [("AccCode", c_uint),
                ("AccMask", c_uint),
                ("Reserved", c_uint),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)
                ]  
class VCI_CAN_OBJ(Structure):  
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_ubyte),
                ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte),
                ("ExternFlag", c_ubyte),
                ("DataLen", c_ubyte),
                ("Data", c_ubyte*8),
                ("Reserved", c_ubyte*3)
                ] 
 
CanDLLName = './ControlCAN.dll' #Put the DLL into the corresponding directory
#canDLL = windll.LoadLibrary('./ControlCAN.dll')
#Use the following statement under Linux system to compile the command: python3 python3.8.0.py
canDLL = cdll.LoadLibrary('./libcontrolcan.so')


print(CanDLLName)
 
ret = canDLL.VCI_OpenDevice(VCI_USBCAN2, 0, 0)
if ret == STATUS_OK:
    print('调用 VCI_OpenDevice成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_OpenDevice出错\r\n')
 
#Initial 0 channel
vci_initconfig = VCI_INIT_CONFIG(0x80000008, 0xFFFFFFFF, 0,
                                 0, 0x03, 0x1C, 0)#Baud rate 125k, normal mode
ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 0, byref(vci_initconfig))
if ret == STATUS_OK:
    print('调用 VCI_InitCAN1成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_InitCAN1出错\r\n')
 
ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 0)
if ret == STATUS_OK:
    print('调用 VCI_StartCAN1成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_StartCAN1出错\r\n')
 
#Initial 1 channel
ret = canDLL.VCI_InitCAN(VCI_USBCAN2, 0, 1, byref(vci_initconfig))
if ret == STATUS_OK:
    print('调用 VCI_InitCAN2 成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_InitCAN2 出错\r\n')
 
ret = canDLL.VCI_StartCAN(VCI_USBCAN2, 0, 1)
if ret == STATUS_OK:
    print('调用 VCI_StartCAN2 成功\r\n')
if ret != STATUS_OK:
    print('调用 VCI_StartCAN2 出错\r\n')
 
#Channel 1 sends data
ubyte_array = c_ubyte*8
a = ubyte_array(1,2,3,4, 5, 6, 7, 8)
ubyte_3array = c_ubyte*3
b = ubyte_3array(0, 0 , 0)
vci_can_obj = VCI_CAN_OBJ(0x1, 0, 0, 1, 0, 0,  8, a, b)#Single send
 
ret = canDLL.VCI_Transmit(VCI_USBCAN2, 0, 0, byref(vci_can_obj), 1)
if ret == STATUS_OK:
    print('CAN1通道发送成功\r\n')
if ret != STATUS_OK:
    print('CAN1通道发送失败\r\n')
 
#Channel 2 receives data
a = ubyte_array(0, 0, 0, 0, 0, 0, 0, 0)
vci_can_obj = VCI_CAN_OBJ(0x0, 0, 0, 0, 0, 0,  0, a, b)#Reset receive buffer
ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, 1, byref(vci_can_obj), 2500, 0)
#print(right)
while ret <= 0:#If no data is received, keep looping to query and receive.
        ret = canDLL.VCI_Receive(VCI_USBCAN2, 0, 1, byref(vci_can_obj), 2500, 0)
if ret > 0:#Received a frame of data
    print('CAN2通道接收成功\r\n')
    print('ID：')
    print(vci_can_obj.ID)
    print('DataLen：')
    print(vci_can_obj.DataLen)
    print('Data：')
    print(list(vci_can_obj.Data))
 
#closure
canDLL.VCI_CloseDevice(VCI_USBCAN2, 0) 

