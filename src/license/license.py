import json
import base64
import hashlib
import uuid
import platform
import socket
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Tuple
from dataclasses import dataclass, field, asdict
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

@dataclass
class Fingerprint:
    device_fingerprint: str = field(default='')
    unit: str = field(default='')
    period: int = field(default=0)
    gen_timestamp: float = field(default=.0)
    expire_timestamp: float = field(default=.0)
    
class LicenseManager:
    def __init__(self, key: int | str = None):
        # 使用提供的密钥或生成新密钥
        if (key or len(key)) in AES.key_size:
            self.key: bytes = key.encode() if isinstance(key, str) else get_random_bytes(key)
        else:
            self.key: bytes = get_random_bytes(32)  # 默认使用 256 位密钥
        
        # 确保密钥长度是 16, 24 或 32 字节
        if len(self.key) not in AES.key_size:
            raise ValueError("密钥长度必须是 16, 24 或 32 字节")
    
    def encrypt_data(self, data: str):
        """使用 AES 加密数据"""
        # 生成随机 IV
        iv = get_random_bytes(AES.block_size)
        
        # 创建加密器
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # 加密数据
        encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
        
        # 返回IV + 加密数据（Base64编码）
        return base64.urlsafe_b64encode(iv + encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> Fingerprint:
        """使用 AES 解密数据"""
        # 解码 Base64 数据
        decoded_data = base64.urlsafe_b64decode(encrypted_data)
        
        # 提取 IV 和加密数据
        iv = decoded_data[:AES.block_size]
        encrypted_data = decoded_data[AES.block_size:]
        
        # 创建解密器
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        
        # 解密数据
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        return json.loads(decrypted_data.decode()) 
    
    def generate_license(self, device_fingerprint: str, unit: str = "month", period: int = 1) -> str:
        """生成许可证"""
        # 计算到期日期
        if unit == "month":
            expire_timestamp = (datetime.now() + timedelta(days=30 * period)).timestamp()
        elif unit == "year":
            expire_timestamp = (datetime.now() + timedelta(days=365 * period)).timestamp()
        else:
            raise ValueError("unit 必须是 'month' 或 'year'")
        
        # 创建许可证数据
        license_data = Fingerprint(
            device_fingerprint=device_fingerprint,
            unit=unit,
            period=period,
            gen_timestamp=datetime.now().timestamp(),
            expire_timestamp=expire_timestamp,
        )
        
        # 加密许可证数据
        return self.encrypt_data(json.dumps(asdict(license_data)))
    
    def validate_license(self, license_key: str, current_device_fingerprint: str) -> Tuple[bool, str]:
        """验证许可证"""
        try:
            # 解密许可证数据
            decrypted_data = self.decrypt_data(license_key)
            license_data = json.loads(decrypted_data)
            
            # 检查设备指纹是否匹配
            if license_data["device_fingerprint"] != current_device_fingerprint:
                return False, "许可证与当前设备不匹配"
            
            # 检查是否过期
            expire_timestamp = datetime.fromtimestamp(license_data["expire_timestamp"])
            if datetime.now().timestamp() > expire_timestamp:
                return False, f"许可证已于 {expire_timestamp} 过期"
            
            # 计算剩余天数
            remaining_days = datetime.fromtimestamp(expire_timestamp - datetime.now().timestamp())
            return True, f"许可证有效，剩余 {remaining_days} 天"
            
        except Exception as e:
            return False, f"许可证验证失败: {str(e)}"
    
    def get_license_info(self, license_key: str) -> Optional[Fingerprint]:
        """获取许可证信息（不验证设备）"""
        try:
            decrypted_data = self.decrypt_data(license_key)
            license_data = json.loads(decrypted_data)
            
            expire_timestamp = datetime.fromtimestamp(license_data["expire_timestamp"])
            gen_timestamp = datetime.fromtimestamp(license_data["gen_timestamp"])
            
            return Fingerprint(
                device_fingerprint=license_data["device_fingerprint"],
                unit=license_data["unit"],
                period=license_data["period"],
                gen_timestamp=gen_timestamp,
                expire_timestamp=expire_timestamp,
            )
        except Exception as e:
            {"error": f"获取许可证信息失败: {str(e)}"}
            return None
    
    def dev_fingerprint(self) -> Optional[str]:
        """生成设备指纹"""
        try:
            # 获取 MAC 地址
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                        for elements in range(0, 2*6, 2)][::-1])
            
            # 获取处理器信息
            processor = platform.processor()
            if not processor:
                processor = "Unknown Processor"
            
            # 获取机器架构
            machine = platform.machine()
            
            # 获取主机名
            hostname = socket.gethostname()
            
            # 获取磁盘序列号（跨平台方法）
            disk_serial = self.get_disk_serial()
            
            # 组合信息并生成哈希
            device_info = f"{mac}{processor}{machine}{hostname}{disk_serial}"
            fingerprint = hashlib.sha256(device_info.encode()).hexdigest()
            return fingerprint
        except Exception as e:
            raise ValueError(f"生成设备指纹时出错: {e}")

    def get_disk_serial(self) -> Optional[str]:
        """获取磁盘序列号（跨平台）"""
        try:
            if platform.system() == "Windows":
                # Windows 系统
                import winreg
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                    product_id = winreg.QueryValueEx(key, "ProductId")[0]
                    winreg.CloseKey(key)
                    return product_id
                except Exception as e:
                    return None
            elif platform.system() == "Darwin":
                # macOS 系统
                command = "system_profiler SPHardwareDataType | grep Serial"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip().split()[-1]
                return None
            else:
                # Linux 系统
                command = "sudo dmidecode -s system-serial-number"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip() != "":
                    return result.stdout.strip()
                # 尝试其他方法
                command = "cat /var/lib/dbus/machine-id 2>/dev/null || cat /etc/machine-id 2>/dev/null"
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
                return None
        except Exception as e:
            print(f"获取磁盘序列号时出错: {e}")
            return None


if __name__ == "__main__":
    lm = LicenseManager(key=24)
    print(lm.dev_fingerprint())
    lic = lm.generate_license(lm.dev_fingerprint())
    print(lic)
    print(lm.decrypt_data(lic))