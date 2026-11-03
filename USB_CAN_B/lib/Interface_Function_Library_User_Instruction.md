# USB-CAN-B Interface Function Library User Instruction

# Table of Contents

1. [OVERVIEW](#1-overview)

2. [COMPATIBLE FUNCTION LIBRARY AND DATA STRUCTURES](#2-compatible-function-library-and-data-structures)
   - [2.1. Type Definitions](#21-type-definitions)
     - [2.1.1. Device Type](#211-device-type)
     - [2.1.2. VCI_BOARD_INFO – Device Information Structure](#212-vci_board_info)
     - [2.1.3. VCI_CAN_OBJ – CAN Message Frame Structure](#213-vci_can_obj)
     - [2.1.4. VCI_INIT_CONFIG – CAN Initialization Configuration Structure](#214-vci_init_config)
     - [2.1.5. CAN Baud Rate Reference Table](#conventional-baud-reference-table)
   - [2.2. Function Descriptions](#22-function-description)
     - [2.2.1. VCI_OpenDevice – Open Device](#221-vci_opendevice)
     - [2.2.2. VCI_CloseDevice – Close Device](#222-vci_closedevice)
     - [2.2.3. VCI_InitCAN – Initialize CAN Channel](#223-vci_initcan)
     - [2.2.4. VCI_ReadBoardInfo – Read Device Information](#224-vci_readboardinfo)
     - [2.2.5. VCI_GetReceiveNum – Get Pending Receive Frame Count](#225-vci_getreceivenum)
     - [2.2.6. VCI_ClearBuffer – Clear CAN Buffers](#226-vci_clearbuffer)
     - [2.2.7. VCI_StartCAN – Start CAN Channel](#227-vci_startcan)
     - [2.2.8. VCI_ResetCAN – Reset CAN Controller](#228-vci_resetcan)
     - [2.2.9. VCI_Transmit – Transmit CAN Frames](#229-vci_transmit)
     - [2.2.10. VCI_Receive – Receive CAN Frames](#2210-vci_receive)

3. [ADDITIONAL FUNCTIONS AND DATA STRUCTURES](#3-other-functions-and-data-structure-description)
   - [3.1. Function Descriptions](#31-function-description)
     - [3.1.1. VCI_UsbDeviceReset – Reset USB-CAN Adapter](#311-vci_usbdevicereset)
     - [3.1.2. VCI_FindUsbDevice2 – Enumerate Connected USB-CAN Adapters](#312-vci_findusbdevice2)

4. [INTERFACE LIBRARY USAGE AND CALL SEQUENCE](#4-interface-library-functions-using-process)
   - [4.1. Function Flow Diagram](#function-flow-diagram)
   - [4.2. Typical Function Call Order](#typical-call-order)

## 1. OVERVIEW

If the user just uses the USB-CAN bus interface adapter to carry out CAN bus communication tests, the supplied USB-CAN Tool software can be used directly to send and receive test data.

If the user intends to write software for their own products, carefully read the following instructions and refer to the sample code provided.

Supported development environments: C++Builder, C#, VC, VB, VB.NET, Delphi, LabVIEW, LabWindows/CVI, Matlab, QT, and Python/Python-can.

- Development library files: `ControlCAN.lib`, `ControlCAN.DLL`
- VC function declaration file: `ControlCAN.h`
- VB function declaration file: `ControlCAN.bas`
- LabVIEW function library package: `ControlCAN.llb`
- Delphi function declaration file: `ControlCAN.pas`

## 2. COMPATIBLE FUNCTION LIBRARY AND DATA STRUCTURE

### 2.1. TYPE DEFINITION

#### 2.1.1. Device Type

| Type definition | Type value | Description |
|---|---:|---|
| `DEV_USBCAN2` | 4 | USBCAN-2A/USBCAN-2C/CANalyst-II, MiniPCIe-CAN |

#### 2.1.2. `VCI_BOARD_INFO`

`VCI_BOARD_INFO` structure contains USB-CAN Series interface card device information. The structure will be filled in `VCI_ReadBoardInfo` function.

```c
typedef struct _VCI_BOARD_INFO {
    USHORT hw_Version;
    USHORT fw_Version;
    USHORT dr_Version;
    USHORT in_Version;
    USHORT irq_Num;
    BYTE can_Num;
    CHAR str_Serial_Num[20];
    CHAR str_hw_Type[40];
    USHORT Reserved[4];
} VCI_BOARD_INFO, *PVCI_BOARD_INFO;
```

**Member**

**`hw_Version`**
Hardware version number, hexadecimal notation. E.g. 0x0100 represents V1.00.

**`fw_Version`**
Hardware version number, hexadecimal notation. E.g. 0x0100 represents V1.00.

**`dr_Version`**
Driver version number, hexadecimal notation. E.g. 0x0100 represents V1.00.

**`in_Version`**
Interface library version number, hexadecimal notation. E.g. 0x0100 represents V1.00.

**`irq_Num`**
System reserved.

**`can_Num`**
Represents the total number of CAN channel.

**`str_Serial_Num`**
This board card's serial number.

**`str_hw_Type`**
Hardware type, such as “USBCAN V1.00” (Note: Includes string terminator ’\0’).

**`Reserved`**
System reserved.

#### 2.1.3. VCI_CAN_OBJ

In the functions VCI_Transmit and VCI_Receive, VCI_CAN_OBJ structure is used to transmit CAN message frame.

```c
typedef struct _VCI_CAN_OBJ {
    UINT ID;
    UINT TimeStamp;
    BYTE TimeFlag;
    BYTE SendType;
    BYTE RemoteFlag;
    BYTE ExternFlag;
    BYTE DataLen;
    BYTE Data[8];
    BYTE Reserved[3];
} VCI_CAN_OBJ, *PVCI_CAN_OBJ;
```

**Member**

**ID**
Message identifier. Direct ID format, right-aligned, please refer to: Annex One: ID Alignment Details.

**TimeStamp**
Receiving the stamp information of the time frame, start timing when the CAN controller is initialized, the unit is 0. 1ms.

**TimeFlag**
In terms of whether to use the time stamp, 1is the effective TimeStamp. TimeFlag and TimeStamp are only meaningful when the frame is received .

**SendType**
Sending type. = 0 indicates Normal type, = 1 indicates Single Send.

**RemoteFlag**
Whether it is a remote flag. = 1 indicates remote flag, = 0 indicates data flag.

**ExternFlag**
Whether it is a extern flag. = 1 indicates extern flag, = 0 indicates standard flag.

**DataLen**
Data length(<=8) ，that is, the length of data.

**Data**
Packet data.

**Reserved**
System reserved.

#### 2.1.4. VCI_INIT_CONFIG

VCI_INIT_CONFIG structure defines the initialization configuration of the CAN. The structure will be filled in VCI_InitCan function.

```c
typedef struct _INIT_CONFIG {
    DWORD AccCode;
    DWORD AccMask;
    DWORD Reserved;
    UCHAR Filter;   // 0/1: receive all frames; 2: standard-frame filtering; 3: extended-frame filtering.
    UCHAR Timing0;  // SJA1000 baud-rate parameter, BTR0.
    UCHAR Timing1;  // SJA1000 baud-rate parameter, BTR1.
    UCHAR Mode;     // 0: normal;1: listen-only;2: self-test mode.
} VCI_INIT_CONFIG, *PVCI_INIT_CONFIG;
```

**Member**

**AccCode**
Receive filtered acceptance code.

**AccMask**
Receive filter mask.

**Reserved**
Reserved.

**Filter**
Filtering method, allowing setting range 0-3, refer to section 2.2.3 of the filter mode table for details.

**Timing0**
SJA1000 Baud rate parameter, Timing0 (BTR0) .

**Timing1**
SJA1000 Baud rate parameter, Timing1 (BTR1) .

**Mode**
Operating mode, 0 = normal operation, 1 = Listen-only mode, 2 = spontaneous admission and sending test mode.

**Remarks**

About the filter settings please refer to: Annex II: CANparameter setup instructions. CAN Timing0 and Timing1 are used to set baud rate, these two parameters are only used at the initialization stage.

**Conventional Baud reference table**

| CAN baud rate | Timing0 (BTR0) | Timing1 (BTR1) |
|---:|---:|---:|
| 10k bps | `0x31` | `0x1C` |
| 20k bps | `0x18` | `0x1C` |
| 40k bps | `0x87` | `0xFF` |
| 50k bps | `0x09` | `0x1C` |
| 80k bps | `0x83` | `0xFF` |
| 100k bps | `0x04` | `0x1C` |
| 125k bps | `0x03` | `0x1C` |
| 200k bps | `0x81` | `0xFA` |
| 250k bps | `0x01` | `0x1C` |
| 400k bps | `0x80` | `0xFA` |
| 500k bps | `0x00` | `0x1C` |
| 666k bps | `0x80` | `0xB6` |
| 800k bps | `0x00` | `0x16` |
| 1000k bps | `0x00` | `0x14` |
| 33.33 Kbps | `0x09` | `0x6F` |
| 66.66 Kbps | `0x04` | `0x6F` |
| 83.33 Kbps | `0x03` | `0x6F` |

**Note**

1. Users only need to follow SJA1000 (16MHz) to set the baud rate parameter.
2. The adapter does not support temporarily baud rate below 10K.

### 2.2. FUNCTION DESCRIPTION

#### 2.2.1. VCI_OpenDevice

This function is used to connect devices.

```c
DWORD __stdcall VCI_OpenDevice(DWORD DevType, DWORD DevIndex, DWORD Reserved);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**Reserved**
Retention parameters, fill in 0.

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4;  /* USB-CAN2.0 */
int nDeviceInd = 0;  /* zeroth device */

DWORD dwRel;
dwRel = VCI_OpenDevice(nDeviceType, nDeviceInd, 0);

if (dwRel != 1) {
    MessageBox(_T("Fail to open the device!"), _T("warning"), MB_OK|MB_ICONQUESTION);
    return FALSE;
}
```

#### 2.2.2. VCI_CloseDevice

This function is used to close the connection.

```c
DWORD __stdcall VCI_CloseDevice(DWORD DevType, DWORD DevIndex);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4;  /* USB-CAN2.0 */
int nDeviceInd = 0;  /* zeroth device */

DWORD dwRel;
dwRel = VCI_CloseDevice(nDeviceType, nDeviceInd);

if (dwRel != 1) {
    MessageBox(_T("Fail to close the device!"), _T("warning"), MB_OK|MB_ICONQUESTION);
    return FALSE;
}
```

#### 2.2.3. VCI_InitCan

This function is used to initialize the specified CAN.

```c
DWORD __stdcall VCI_InitCAN(DWORD DevType, DWORD DevIndex, DWORD CANIndex, PVCI_INIT_CONFIG pInitConfig);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**CANIndex**
CAN channel index, such as when there is only one CAN channel, the index number is 0, if there are two, the index number can be 0 or 1.

**pInitConfig**

Initialization parameter structure. The members are used as follows:

**AccCode and AccMask**

AccCode and AccMask work together to determine which packets can be accepted. These registers set the ID left-aligned: the highest bit (Bit31) of AccCode and AccMask is aligned with the highest bit of the ID value. For ID alignment, refer to Annex I: ID alignment details.

For example, if AccCode is set to `0x24600000` (that is, `0x123` shifted left by 21 bits) and AccMask is set to `0x00000000`, only packets with CAN message frame ID `0x123` can be accepted. An AccMask value of `0x00000000` indicates that all bits are relevant.

If AccCode is set to `0x24600000` and AccMask is set to `0x600000` (`0x03` shifted left by 21 bits), packets with CAN message frame IDs from `0x120` to `0x123` can be accepted. An AccMask value of `0x600000` indicates that, apart from bits 0–1, the other bits (bits 2–10) are relevant.

This filter-setting example applies to standard frames, where the high 11 bits are the valid bits. For extended frames, the valid ID is 29 bits; AccCode and AccMask use the high 29 bits as the valid bits.

**Reserved**

Reserved.

**Filter**

Filtering mode settings. Refer to the filter mode table.

**Timing0**

Baud rate T0 setting.

**Timing1**

Baud rate T1 setting.

**Mode**

Operating mode:
- `0` — normal operation
- `1` — listen-only mode
- `2` — spontaneous admission and sending test mode (this value is excluded from the ZLG function library).

**Filter mode table**

| Value | Name | Description |
|---:|---|---|
| 1 | Receive all types | Suitable for both standard and extended frames. |
| 2 | Only receive standard frame | Suitable for standard frames; extended frames are removed by filtration. |
| 3 | Only receive extended frame | Suitable for extended frames; standard frames are removed by filtration. |

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4; /*USB-CAN2.0 */
int nDeviceInd = 0;  /*zeroth device */
int nCANInd = 0;     /*zeroth channel */

DWORD dwRel;
dwRel = VCI_OpenDevice(nDeviceType, nDeviceInd, 0);

if (dwRel != 1)
{
    MessageBox(_T("Fail to open the device!"), _T("warning"), MB_OK | MB_ICONQUESTION);
    return FALSE;
}

VCI_INIT_CONFIG vic;

vic.AccCode = 0x80000008;
vic.AccMask = 0xFFFFFFFF;
vic.Filter = 1;
vic.Timing0 = 0x00;
vic.Timing1 = 0x14;
vic.Mode = 0;

dwRel = VCI_InitCAN(nDeviceType, nDeviceInd, nCANInd, &vic);

if (dwRel != 1)
{
    VCI_CloseDevice(nDeviceType, nDeviceInd);
    MessageBox(_T("fail to initialize the device!"), _T("warning"), MB_OK | MB_ICONQUESTION);
    return FALSE;
}
```

#### 2.2.4. VCI_ReadBoardInfo

This function is used to read the adapter hardware information. Generally speaking, it can be ignored.

```c
DWORD __stdcall VCI_ReadBoardInfo(DWORD DevType, DWORD DevIndex, PVCI_BOARD_INFO pInfo);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB- CAN adapters, the index numbers in an ascending order starting from 0.

**pInfo**
VCI_BOARD_INFO is used to store device information structure pointer.

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4; /*USB-CAN2.0 */
int nDeviceInd = 0;  /*zeroth device */
int nCANInd = 0;     /*zeroth channel */

VCI_BOARD_INFO vbi;

DWORD dwRel;
dwRel = VCI_ReadBoardInfo(nDeviceType, nDeviceInd, &vbi);

if (dwRel != 1)
{
    MessageBox(_T("Fail to obtain device information!"), _T("warning"), MB_OK | MB_ICONQUESTION);
    return FALSE;
}
```

#### 2.2.5. VCI_GetReceiveNum

This function is used to specify the received but has not been read frames in the designated receiving buffer.

```c
DWORD __stdcall VCI_GetReceiveNum(DWORD DevType, DWORD DevIndex, DWORD CANIndex);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB- CAN adapters, the index numbers in an ascending order starting from 0.

**CANIndex**
CAN channel index.

**Returns**

Return frames that have not been read yet.

Example:

```c
#include "ControlCan.h"

int ret = VCI_GetReceiveNum(2, 0, 0);
```

#### 2.2.6. VCI_ClearBuffer

This function is used to clear the receive and send buffer of the designated channel specified by USB-CAN adapter.

```c
DWORD __stdcall VCI_ClearBuffer(DWORD DevType, DWORD DevIndex, DWORD CANIndex);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB- CAN adapters, the index numbers in an ascending order starting from 0.

**CANIndex**
CAN channel index.

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

#### 2.2.7. VCI_StartCAN

This function is used to start the CAN controller and the internal interrupt reception function of the adapter.

```c
DWORD __stdcall VCI_StartCAN(DWORD DevType, DWORD DevIndex, DWORD CANIndex);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**CANIndex**
CAN channel index.

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4; /*USB-CAN2.0 */
int nDeviceInd = 0;  /*zeroth device */
int nCANInd = 0;     /*zeroth channel */

DWORD dwRel;
VCI_INIT_CONFIG vic;

if (VCI_OpenDevice(nDeviceType, nDeviceInd, 0) != 1)
{
    MessageBox(_T("Fail to open the device!"), _T("warning"), MB_OK | MB_ICONQUESTION);
    return FALSE;
}

if (VCI_InitCAN(nDeviceType, nDeviceInd, nCANInd, &vic) != 1)
{
    VCI_CloseDevice(nDeviceType, nDeviceInd);
    MessageBox(_T("Fail to initialize the device!"), _T("warning"), MB_OK | MB_ICONQUESTION);
    return FALSE;
}

if (VCI_StartCAN(nDeviceType, nDeviceInd, nCANInd) != 1)
{
    VCI_CloseDevice(nDeviceType, nDeviceInd);
    MessageBox(_T("Fail to start the device!"), _T("warning"), MB_OK | MB_ICONQUESTION);
    return FALSE;
}
```

#### 2.2.8. VCI_ResetCAN

This function is used to reset the CAN controller.

```c
DWORD __stdcall VCI_ResetCAN(DWORD DevType, DWORD DevIndex, DWORD CANIndex);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**CANIndex**
CAN channel index.

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4; /*USB-CAN2.0 */
int nDeviceInd = 0;  /*zeroth device */
int nCANInd = 0;     /*zeroth channel */

DWORD dwRel;
dwRel = VCI_ResetCAN(nDeviceType, nDeviceInd, nCANInd);

if (dwRel != 1)
{
    MessageBox(_T("Fail to reset!"), _T("warning"), MB_OK | MB_ICONQUESTION);
    return FALSE;
}
```

#### 2.2.9. VCI_Transmit

This function is used to send CAN message frame.

```c
DWORD __stdcall VCI_Transmit(DWORD DeviceType, DWORD DeviceInd, DWORD CANInd, PVCI_CAN_OBJ pSend, DWORD Length);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**CANIndex**
CAN channel index.

**pSend**
The first address of the data frame arrays that have to be sent.

**Length**
The number of the data frames that have to be sent, the maximum number is 1000, the recommended value is 48 under high speed.

**Returns**

Return the actual number of frames already sent, the return value = -1 indicates a device error.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4; /*USB-CAN2.0 */
int nDeviceInd = 0;  /*zeroth device */
int nCANInd = 0;     /*zeroth channel */

DWORD dwRel;
VCI_CAN_OBJ vco[48];
ZeroMemory(vco, sizeof(VCI_CAN_OBJ) *48);

for (int i = 0; i < 48; i++)
{
	vco[i].ID = i;
	vco[i].RemoteFlag = 0;
	vco[i].ExternFlag = 0;
	vco[i].DataLen = 8;
	for (int j = 0; j < 8; j++)
	{
		vco[i].Data[j] = j;
	}
}

dwRel = VCI_Transmit(nDeviceType, nDeviceInd, nCANInd, vco, 48);
```

#### 2.2.10. VCI_Receive

This function is used to request reception.

```c
DWORD __stdcall VCI_Receive(DWORD DevType, DWORD DevIndex, DWORD CANIndex, PVCI_CAN_OBJ pReceive, ULONG Len, INT WaitTime);
```

**Parameters**

**DevType**
Device type. See: Adapter device type definition.

**DevIndex**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**CANIndex**
CAN channel index. pReceive To receive the first set pointer of the data frames.

**Len**
The array length of the data frame must be more than 2500 to return normal message. Otherwise, the return length will be zero whether the message is received or not. the adapter set a 2000-frame buffer for every channel. Based on his own system and working environment, the user can choose an appropriate array length from 2500.

**WaitTime**
Reserved.

**Returns**

Return the number of frames that actually have been read, -1 indicates device errors.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4; /*USB-CAN2.0 */
int nDeviceInd = 0;  /*zeroth device */
int nCANInd = 0;     /*zeroth channel */

long lRel;
VCI_CAN_OBJ vco[2500];
lRel = VCI_Receive(nDeviceType, nDeviceInd, nCANInd, vco, 2500, 0);

if (lRel > 0)
{… /*data processing */ }

else if (lRel == -1)
{… /*receive error treatment */ }
```

## 3. OTHER FUNCTIONS AND DATA STRUCTURE DESCRIPTION

This chapter describes other data types and functions of the incompatible ZLG interface library contained in USB-CAN adapter interface library ControlCAN.dll. Please do not call these functions if use a compatible ZLG model for secondary development so as not to affect compatibility.

### 3.1 FUNCTION DESCRIPTION

#### 3.1.1. `VCI_UsbDeviceReset`

Reset USB-CAN adapter, need to re-open the device after reset by using `VCI_OpenDevice`.

```c
DWORD __stdcall VCI_UsbDeviceReset(DWORD DevType, DWORD DevIndex, DWORD Reserved);
```

**Parameters**

**`DevType`**
Device type. See: Adapter device type definition.

**`DevIndex`**
Device Index, for example, when there is only one USB-CAN adapter, the index number is 0, when there are multiple USB-CAN adapters, the index numbers in an ascending order starting from 0.

**`Reserved`**
Reserved.

**Returns**

Return value = 1, which means that the operation is successful; = 0 indicates that the operation failed; = -1 indicates that the device does not exist.

Example:

```c
#include "ControlCan.h"

int nDeviceType = 4; /* USB-CAN2.0 */
int nDeviceInd = 0;  /* zeroth device */
int nCANInd = 0;     /* zeroth channel */

DWORD dwRel;
dwRel = VCI_UsbDeviceReset(nDeviceType, nDeviceInd, 0);
```

#### 3.1.2. `VCI_FindUsbDevice2`

When the same PC using multiple USB-CAN, user can use this function to find the current device.

```c
DWORD __stdcall VCI_FindUsbDevice2(PVCI_BOARD_INFO pInfo);
```

**Parameters**

**`pInfo`**
pInfo is used to store the parameters of the first data buffer address pointer.

**`Returns`**

Return the number of the USB-CAN adapter plugged into the computer.

Example:

```c
#include "ControlCan.h"

CString ProductSn[50];
VCI_BOARD_INFO pInfo[50];

int num = VCI_FindUsbDevice2(pInfo);

CString strtemp, str;

for (int i = 0; i < num; i++) {
    str = "";

    for (int j = 0; j < 20; j++) {
        strtemp.Format("%c", pInfo[i].str_Serial_Num[j]);
        str += strtemp;
    }

    ProductSn[i] = "USBCAN-" + str;
}
```

## 4. INTERFACE LIBRARY FUNCTIONS USING PROCESS
In order to multiply device function, we provided additional functions( functions
presented with    a     green   background),   these     functions   include:     `VCI_FindUsbDevice2`
`VCI_UsbDeviceReset`. During the second development, these functions are not necessarily to be
invoked. Even these functions are ignored, all USB-CAN adapter functions can be achieved.

### Function flow diagram

The diagram below represents the USB-CAN adapter's typical initialization, operation, and shutdown sequence. The two green functions are additional functions; the manual says they are not required for normal CAN communication.

<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   width="75%"
   height="auto"
   viewBox="0 0 197.48103 276.68219"
   version="1.1"
   id="svg1"
   xml:space="preserve"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:author="dhiman.sarkar.ncsm@gmail.com"><title
     id="title9">Waveshare USB-CAN-B Function flow diagram</title><defs
     id="defs1"><marker
       style="overflow:visible"
       id="Triangle"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135" /></marker><marker
       style="overflow:visible"
       id="Triangle-3"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-9"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-6" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-9-1"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-6-5" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-7-1"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-63-7" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-7-1-9"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-63-7-6" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-7-1-6"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-63-7-0" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-7-1-7"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-63-7-7" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-7-1-6-7"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-63-7-0-5" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-7-1-6-7-0"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-63-7-0-5-8" /></marker><marker
       style="overflow:visible"
       id="Triangle-3-7-1-6-7-0-2"
       refX="0"
       refY="0"
       orient="auto-start-reverse"
       markerWidth="1"
       markerHeight="1"
       viewBox="0 0 1 1"
       preserveAspectRatio="xMidYMid"><path
         transform="scale(0.5)"
         style="fill:context-stroke;fill-rule:evenodd;stroke:context-stroke;stroke-width:1pt"
         d="M 5.77,0 -2.88,5 V -5 Z"
         id="path135-9-63-7-0-5-8-5" /></marker></defs><g
     id="layer1"
     transform="translate(-6.2594835,-10.158911)"><g
       id="g9"
       transform="translate(2.4765174)"><g
         id="g17"
         transform="translate(-1.2479434,10.748387)"><g
           id="g8"
           transform="translate(0.60547595,-4.7688592)"><rect
             style="fill:none;stroke:#000000;stroke-width:0.803612;stroke-dasharray:none;stroke-opacity:1"
             id="rect1-3"
             width="39.196388"
             height="11.584205"
             x="86.044273"
             y="196.72882" /><text
             xml:space="preserve"
             style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
             x="90.435143"
             y="203.5927"
             id="text4-22"><tspan
               id="tspan4-61"
               style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
               x="90.435143"
               y="203.5927">VCI_StartCAN</tspan></text></g><g
           id="g4"
           transform="translate(-3.4695553,3.7614952)"><rect
             style="fill:none;stroke:#000000;stroke-width:0.895872;stroke-dasharray:none;stroke-opacity:1"
             id="rect1-06"
             width="49.104126"
             height="11.491944"
             x="85.165436"
             y="260.39133" /><text
             xml:space="preserve"
             style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
             x="90.668549"
             y="267.25763"
             id="text4-94"><tspan
               id="tspan4-81"
               style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
               x="90.668549"
               y="267.25763">VCI_CloseDevice</tspan></text></g><g
           id="g16"
           transform="translate(0,-5.2721111)"><g
             id="g14"
             transform="translate(4.175365,-17.258762)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.895873;stroke-dasharray:none;stroke-opacity:1"
               id="rect1"
               width="49.104126"
               height="11.491944"
               x="77.520515"
               y="49.325844" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="84.297966"
               y="56.18079"
               id="text4"><tspan
                 id="tspan4"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="84.297966"
                 y="56.18079">VCI_OpenDevice</tspan></text></g><g
             id="g15"
             transform="translate(1.3177505,-22.939954)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.938274;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-15"
               width="54.061726"
               height="11.449543"
               x="77.89933"
               y="28.091726" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="83.332565"
               y="34.925472"
               id="text4-5"><tspan
                 id="tspan4-2"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="83.332565"
                 y="34.925472">VCI_FindUsbDevice</tspan></text></g><g
             id="g13"
             transform="translate(2.1572643,-12.196583)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.803612;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-2"
               width="39.196388"
               height="11.584205"
               x="84.492485"
               y="71.154045" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="90.157692"
               y="78.055122"
               id="text4-4"><tspan
                 id="tspan4-3"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="90.157692"
                 y="78.055122">VCI_InitCAN</tspan></text></g><path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.79375;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle)"
             d="M 106.24794,17.070981 V 29.862102"
             id="path15" /><path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.79375;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3)"
             d="M 106.24794,44.007492 V 56.798613"
             id="path15-8" /></g><path
           style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.79375;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-9)"
           d="M 106.24794,65.671891 V 188.73896"
           id="path15-8-5" /><path
           style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.79375;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-9-1)"
           d="m 106.24794,203.9465 v 56.93919"
           id="path15-8-5-4" /></g><g
         id="g32"><g
           id="g26"
           transform="translate(-4.7625002)"><g
             id="g12"
             transform="translate(-26.732425,25.508597)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.938274;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-6"
               width="54.061726"
               height="11.449542"
               x="35.74704"
               y="117.62909" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="41.156502"
               y="124.46284"
               id="text4-2"><tspan
                 id="tspan4-0"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="41.156502"
                 y="124.46284">VCI_GetReceiveNum</tspan></text></g><g
             id="g22"
             transform="translate(3.03075,0.60664738)"><g
               id="g21"><path
                 style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.961483;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-7-1-9)"
                 d="M 106.68285,148.25581 H 63.929555"
                 id="path15-8-59-7-3" /></g></g></g><g
           id="g10"
           transform="translate(-23.736045,27.743436)"><rect
             style="fill:none;stroke:#000000;stroke-width:0.938273;stroke-dasharray:none;stroke-opacity:1"
             id="rect1-7"
             width="54.061726"
             height="11.449543"
             x="27.988148"
             y="137.53145" /><text
             xml:space="preserve"
             style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
             x="33.437916"
             y="144.36519"
             id="text4-6"><tspan
               id="tspan4-6"
               style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
               x="33.437916"
               y="144.36519">VCI_ReadBoardInfo</tspan></text></g><path
           style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.961483;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-7-1-6)"
           d="M 104.9511,170.99966 H 62.197793"
           id="path15-8-59-7-8" /><g
           id="g25"
           transform="translate(-1.5875)"><g
             id="g19"
             transform="translate(3.6366258)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.895872;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-0"
               width="49.104126"
               height="11.491944"
               x="149.66281"
               y="143.11649" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="155.12148"
               y="149.9828"
               id="text4-48"><tspan
                 id="tspan4-7"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="155.12148"
                 y="149.9828">VCI_ClearBuffer</tspan></text></g><path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.961483;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-7-1-7)"
             d="m 106.68338,148.86247 42.75329,-1e-5"
             id="path15-8-59-7-30" /></g></g><g
         id="g3"><g
           id="g28"
           transform="translate(-4.7625002,0.65405818)"><g
             id="g11"
             transform="translate(-10.357689,5.9456445)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.938273;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-5"
               width="54.061726"
               height="11.449543"
               x="19.372297"
               y="93.257065" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="23.613873"
               y="100.09081"
               id="text4-8"><tspan
                 id="tspan4-8"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="23.613873"
                 y="100.09081">VCI_UsbDeviceReset</tspan></text></g><path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.961483;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-7-1)"
             d="M 109.7136,104.92748 H 66.960297"
             id="path15-8-59-7" /></g><path
           style="fill:none;fill-opacity:1;stroke:#000000;stroke-width:0.79375;stroke-linecap:butt;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle)"
           d="m 31.933091,99.38763 -0.0046,-70.913 69.862479,10e-7"
           id="path30" /></g><g
         id="g2"><g
           id="g33"><g
             id="g7"
             transform="translate(11.952912,12.55344)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.803612;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-1"
               width="39.196388"
               height="11.584205"
               x="139.75902"
               y="231.74747" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="146.67996"
               y="238.64854"
               id="text4-7"><tspan
                 id="tspan4-71"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="146.67996"
                 y="238.64854">VCI_Recive</tspan></text></g><g
             id="g5"
             transform="translate(-9.8471698,13.522358)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.803612;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-9"
               width="39.196388"
               height="11.584205"
               x="29.03194"
               y="230.77855" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="33.486885"
               y="237.67963"
               id="text4-76"><tspan
                 id="tspan4-73"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="33.486885"
                 y="237.67963">VCI_Transmit</tspan></text></g><path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.961483;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-7-1-6-7)"
             d="M 104.9511,250.09303 H 62.197792"
             id="path15-8-59-7-8-1" /><path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.961483;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-7-1-6-7-0-2)"
             d="m 105.14254,250.09305 42.75329,-2e-5"
             id="path15-8-59-7-8-1-6-2" /></g><g
           id="g1"><g
             id="g6"
             transform="translate(23.074883,7.0287769)"><rect
               style="fill:none;stroke:#000000;stroke-width:0.803612;stroke-dasharray:none;stroke-opacity:1"
               id="rect1-28"
               width="39.196388"
               height="11.584205"
               x="-167.83344"
               y="213.19635"
               transform="scale(-1,1)" /><text
               xml:space="preserve"
               style="font-size:4.23333px;writing-mode:lr-tb;direction:ltr;fill:#000000;fill-opacity:1;stroke:none;stroke-width:2.64583;stroke-dasharray:none;stroke-opacity:1"
               x="133.02791"
               y="220.06023"
               id="text4-9"><tspan
                 id="tspan4-4"
                 style="font-style:normal;font-variant:normal;font-weight:normal;font-stretch:normal;font-size:4.23333px;font-family:Monospace;-inkscape-font-specification:Monospace;stroke-width:2.64583"
                 x="133.02791"
                 y="220.06023">VCI_ResetCAN</tspan></text></g><path
             style="fill:#000000;fill-opacity:1;stroke:#000000;stroke-width:0.961483;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle-3-7-1-6-7-0)"
             d="m 105.09588,226.01726 42.75329,-2e-5"
             id="path15-8-59-7-8-1-6" /><path
             style="fill:none;fill-opacity:1;stroke:#000000;stroke-width:0.79375;stroke-linecap:butt;stroke-dasharray:none;stroke-opacity:1;marker-end:url(#Triangle)"
             d="m 171.31013,220.22513 v -33.0073 h -63.11934"
             id="path33" /></g></g></g></g></svg>


### Typical call order

1. Optionally enumerate connected adapters with `VCI_FindUsbDevice2`.
2. Open the adapter with `VCI_OpenDevice`.
3. Configure and initialize the CAN channel with `VCI_InitCAN`.
4. Optionally query adapter information or inspect/clear the receive buffer.
5. Start the CAN channel with `VCI_StartCAN`.
6. Exchange frames using `VCI_Transmit` and `VCI_Receive`.
7. If required, reset the CAN controller with `VCI_ResetCAN`.
8. Close the adapter with `VCI_CloseDevice`.

`VCI_UsbDeviceReset` is a separate USB-adapter recovery operation. The manual notes that the device must be opened again after this reset.
