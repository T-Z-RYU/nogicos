# -*- coding: utf-8 -*-
"""
UIPI Checker - UI Permission隔离检测

Windows Vista+ 有 UI Permission隔离 (User Interface Privilege Isolation):
- LowPermissionProcess无法向HighPermissionProcessSendMessage
- 例如: 普通应用无法控制以AdminRunning的程序

完整性级别:
- UNTRUSTED: 0x0000 (最Low)
- LOW: 0x1000 (沙盒应用)
- MEDIUM: 0x2000 (标准User应用)
- MEDIUM_PLUS: 0x2100
- HIGH: 0x3000 (Admin)
- SYSTEM: 0x4000 (SystemService)

NOTE: UIPI check is DISABLED by default due to ctypes segfault issues.
Set NOGICOS_ENABLE_UIPI_CHECK=1 to enable (at your own risk).
"""

import ctypes
from ctypes import wintypes
import logging
import os
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

logger = logging.getLogger("nogicos.tools.uipi_checker")

# UIPI check disabled by default due to ctypes segfault on some Windows configurations
UIPI_CHECK_ENABLED = os.environ.get("NOGICOS_ENABLE_UIPI_CHECK", "0") == "1"


class IntegrityLevel(IntEnum):
    """Windows 完整性级别"""
    UNTRUSTED = 0x0000
    LOW = 0x1000
    MEDIUM = 0x2000
    MEDIUM_PLUS = 0x2100
    HIGH = 0x3000
    SYSTEM = 0x4000
    
    @classmethod
    def from_rid(cls, rid: int) -> 'IntegrityLevel':
        """从 RID 值Get完整性级别"""
        for level in cls:
            if rid >= level.value and rid < level.value + 0x1000:
                return level
        return cls.MEDIUM


@dataclass
class UIAccessibility:
    """UI 可visit性Result"""
    accessible: bool
    our_level: IntegrityLevel
    target_level: IntegrityLevel
    reason: str
    suggestion: str


class UIPIChecker:
    """UIPI PermissionCheck器"""
    
    def __init__(self):
        self.user32 = ctypes.WinDLL('user32', use_last_error=True)
        self.kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        self.advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
        self._setup_functions()
        
        # CachewhenBeforeProcess's Completepropertylevelother
        self._our_level: Optional[IntegrityLevel] = None
    
    def _setup_functions(self):
        """Set Windows API FunctionSignature"""
        # GetWindowThreadProcessId
        self.user32.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND, ctypes.POINTER(wintypes.DWORD)
        ]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        
        # GetCurrentProcessId
        self.kernel32.GetCurrentProcessId.argtypes = []
        self.kernel32.GetCurrentProcessId.restype = wintypes.DWORD
        
        # OpenProcess
        self.kernel32.OpenProcess.argtypes = [
            wintypes.DWORD, wintypes.BOOL, wintypes.DWORD
        ]
        self.kernel32.OpenProcess.restype = wintypes.HANDLE
        
        # CloseHandle
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        
        # OpenProcessToken
        self.advapi32.OpenProcessToken.argtypes = [
            wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)
        ]
        self.advapi32.OpenProcessToken.restype = wintypes.BOOL
        
        # GetTokenInformation
        self.advapi32.GetTokenInformation.argtypes = [
            wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
            wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)
        ]
        self.advapi32.GetTokenInformation.restype = wintypes.BOOL
    
    def check_window_accessibility(self, hwnd: int) -> UIAccessibility:
        """
        CheckWindowYesNo可被操作

        Args:
            hwnd: TargetWindow句柄

        Returns:
            UIAccessibility Package含可visit性Info
        """
        # Skip UIPI check if disabled (default) - prevents ctypes segfault
        if not UIPI_CHECK_ENABLED:
            return UIAccessibility(
                accessible=True,
                our_level=IntegrityLevel.MEDIUM,
                target_level=IntegrityLevel.MEDIUM,
                reason="UIPI check disabled",
                suggestion=""
            )

        # GetTargetWindow's Process ID
        process_id = wintypes.DWORD()
        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

        # Getwe's Completepropertylevelother
        our_level = self._get_current_integrity_level()

        # GetTargetProcess's Completepropertylevelother
        target_level = self._get_process_integrity_level(process_id.value)

        accessible = our_level >= target_level

        if accessible:
            return UIAccessibility(
                accessible=True,
                our_level=our_level,
                target_level=target_level,
                reason="",
                suggestion=""
            )
        else:
            return UIAccessibility(
                accessible=False,
                our_level=our_level,
                target_level=target_level,
                reason=f"UIPI: 我们的级别 ({our_level.name}) Low于Target ({target_level.name})",
                suggestion="需要以AdminPermissionRunning NogicOS，或降LowTarget应用的Permission级别"
            )
    
    def _get_current_integrity_level(self) -> IntegrityLevel:
        """Get当BeforeProcess的完整性级别"""
        if self._our_level is not None:
            return self._our_level
        
        self._our_level = self._get_process_integrity_level(
            self.kernel32.GetCurrentProcessId()
        )
        return self._our_level
    
    def _get_process_integrity_level(self, process_id: int) -> IntegrityLevel:
        """GetSpecifyProcess的完整性级别"""
        PROCESS_QUERY_INFORMATION = 0x0400
        TOKEN_QUERY = 0x0008
        TokenIntegrityLevel = 25
        
        try:
            # OpenProcess
            process = self.kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION, False, process_id
            )
            if not process:
                logger.debug(f"Cannot open process {process_id}, assuming MEDIUM")
                return IntegrityLevel.MEDIUM
            
            try:
                # OpenProcessToken
                token = wintypes.HANDLE()
                if not self.advapi32.OpenProcessToken(
                    process, TOKEN_QUERY, ctypes.byref(token)
                ):
                    logger.debug(f"Cannot open token for process {process_id}")
                    return IntegrityLevel.MEDIUM
                
                try:
                    # GetCompletepropertylevelotherplaceneed's BufferareaSize
                    info_size = wintypes.DWORD()
                    self.advapi32.GetTokenInformation(
                        token, TokenIntegrityLevel, None, 0, ctypes.byref(info_size)
                    )
                    
                    if info_size.value == 0:
                        return IntegrityLevel.MEDIUM
                    
                    # AllocateBufferareaandGetInfo
                    buffer = ctypes.create_string_buffer(info_size.value)
                    if self.advapi32.GetTokenInformation(
                        token, TokenIntegrityLevel, buffer, 
                        info_size, ctypes.byref(info_size)
                    ):
                        # Parse TOKEN_MANDATORY_LABEL structure
                        # structure's FirstaMemberYes SID_AND_ATTRIBUTES，its Sid PointerinOffset 0
                        sid_ptr = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p)).contents
                        
                        if sid_ptr:
                            # Get SID 's ChildPermissionCount
                            sub_auth_count_ptr = self.advapi32.GetSidSubAuthorityCount(sid_ptr)
                            if sub_auth_count_ptr:
                                count = ctypes.cast(
                                    sub_auth_count_ptr, 
                                    ctypes.POINTER(ctypes.c_ubyte)
                                ).contents.value
                                
                                if count > 0:
                                    # GetmostAfteroneaChildPermission (RID)
                                    rid_ptr = self.advapi32.GetSidSubAuthority(
                                        sid_ptr, count - 1
                                    )
                                    if rid_ptr:
                                        rid = ctypes.cast(
                                            rid_ptr, 
                                            ctypes.POINTER(wintypes.DWORD)
                                        ).contents.value
                                        return IntegrityLevel.from_rid(rid)
                    
                    return IntegrityLevel.MEDIUM
                    
                finally:
                    self.kernel32.CloseHandle(token)
            finally:
                self.kernel32.CloseHandle(process)
                
        except Exception as e:
            logger.debug(f"Error getting integrity level for process {process_id}: {e}")
            return IntegrityLevel.MEDIUM
    
    def is_elevated(self) -> bool:
        """Check当BeforeProcessYesNo以AdminPermissionRunning"""
        return self._get_current_integrity_level() >= IntegrityLevel.HIGH
    
    def can_control_window(self, hwnd: int) -> bool:
        """FastCheckYesNo可以控制SpecifyWindow"""
        return self.check_window_accessibility(hwnd).accessible


# GlobalSingleton
_global_uipi_checker: Optional[UIPIChecker] = None


def get_uipi_checker() -> UIPIChecker:
    """GetGlobal UIPI Check器"""
    global _global_uipi_checker
    if _global_uipi_checker is None:
        _global_uipi_checker = UIPIChecker()
    return _global_uipi_checker


# convenientFunction
def can_control_window(hwnd: int) -> bool:
    """FastCheckYesNo可以控制Window"""
    return get_uipi_checker().can_control_window(hwnd)


# Export
__all__ = [
    'IntegrityLevel',
    'UIAccessibility',
    'UIPIChecker',
    'get_uipi_checker',
    'can_control_window',
]
