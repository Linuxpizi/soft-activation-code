# Python 生成硬件绑定激活码

下面是一个完整的Python实现，用于生成基于硬件信息的绑定激活码：

```python
import hashlib
import uuid
import platform
import subprocess
import socket
import json
import base64
from datetime import datetime, timedelta
import hmac

class HardwareLicenseGenerator:
    def __init__(self, secret_key):
        """
        初始化激活码生成器
        
        Args:
            secret_key (str): 用于签名的密钥
        """
        self.secret_key = secret_key.encode('utf-8')
    
    def get_hardware_info(self):
        """
        收集硬件信息
        
        Returns:
            dict: 包含硬件信息的字典
        """
        hardware_info = {}
        
        # 获取MAC地址
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 8*6, 8)][::-1])
            hardware_info['mac'] = mac
        except:
            hardware_info['mac'] = "unknown"
        
        # 获取主机名
        try:
            hardware_info['hostname'] = socket.gethostname()
        except:
            hardware_info['hostname'] = "unknown"
        
        # 获取处理器信息
        try:
            hardware_info['processor'] = platform.processor()
        except:
            hardware_info['processor'] = "unknown"
        
        # 获取系统信息
        try:
            hardware_info['system'] = platform.system()
            hardware_info['version'] = platform.version()
        except:
            hardware_info['system'] = "unknown"
            hardware_info['version'] = "unknown"
        
        # 获取硬盘序列号 (Windows)
        if platform.system() == "Windows":
            try:
                result = subprocess.check_output(
                    "wmic diskdrive get serialnumber", 
                    shell=True, 
                    stderr=subprocess.DEVNULL
                ).decode()
                lines = result.strip().split('\n')
                if len(lines) > 1:
                    hardware_info['disk_serial'] = lines[1].strip()
                else:
                    hardware_info['disk_serial'] = "unknown"
            except:
                hardware_info['disk_serial'] = "unknown"
        
        # 获取主板信息 (Linux/Unix)
        elif platform.system() in ["Linux", "Darwin"]:
            try:
                # 尝试获取主板序列号
                result = subprocess.check_output(
                    "sudo dmidecode -s baseboard-serial-number 2>/dev/null || echo unknown", 
                    shell=True
                ).decode().strip()
                hardware_info['board_serial'] = result
            except:
                hardware_info['board_serial'] = "unknown"
        
        return hardware_info
    
    def generate_hardware_fingerprint(self, hardware_info):
        """
        基于硬件信息生成指纹
        
        Args:
            hardware_info (dict): 硬件信息
            
        Returns:
            str: 硬件指纹
        """
        # 选择用于生成指纹的关键硬件信息
        fingerprint_data = ""
        for key in ['mac', 'disk_serial', 'board_serial', 'processor']:
            if hardware_info.get(key) and hardware_info[key] != "unknown":
                fingerprint_data += hardware_info[key]
        
        if not fingerprint_data:
            # 如果没有找到有效的硬件信息，使用主机名和系统信息
            fingerprint_data = hardware_info.get('hostname', '') + hardware_info.get('system', '')
        
        # 生成MD5哈希作为指纹
        fingerprint = hashlib.md5(fingerprint_data.encode('utf-8')).hexdigest()
        return fingerprint
    
    def generate_license(self, user_data=None, expiry_days=365):
        """
        生成激活码
        
        Args:
            user_data (dict, optional): 用户自定义数据
            expiry_days (int): 有效期天数
            
        Returns:
            str: 激活码
        """
        # 获取硬件信息
        hardware_info = self.get_hardware_info()
        
        # 生成硬件指纹
        hardware_fingerprint = self.generate_hardware_fingerprint(hardware_info)
        
        # 计算过期时间
        expiry_date = datetime.now() + timedelta(days=expiry_days)
        
        # 构建许可证数据
        license_data = {
            'hardware_fingerprint': hardware_fingerprint,
            'hardware_info': hardware_info,
            'expiry_date': expiry_date.isoformat(),
            'generated_at': datetime.now().isoformat()
        }
        
        # 添加用户数据
        if user_data:
            license_data['user_data'] = user_data
        
        # 转换为JSON字符串
        license_json = json.dumps(license_data, sort_keys=True)
        
        # 使用HMAC进行签名
        signature = hmac.new(
            self.secret_key, 
            license_json.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
        
        # 组合数据和签名
        signed_license = license_json + ":" + signature
        
        # Base64编码
        encoded_license = base64.b64encode(signed_license.encode('utf-8')).decode('utf-8')
        
        return encoded_license
    
    def validate_license(self, license_key, check_hardware=True):
        """
        验证激活码
        
        Args:
            license_key (str): 激活码
            check_hardware (bool): 是否检查硬件绑定
            
        Returns:
            dict: 验证结果
        """
        try:
            # Base64解码
            decoded_license = base64.b64decode(license_key.encode('utf-8')).decode('utf-8')
            
            # 分离数据和签名
            license_json, signature = decoded_license.split(':', 1)
            
            # 验证签名
            expected_signature = hmac.new(
                self.secret_key, 
                license_json.encode('utf-8'), 
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return {
                    'valid': False,
                    'message': '无效的签名'
                }
            
            # 解析许可证数据
            license_data = json.loads(license_json)
            
            # 检查过期时间
            expiry_date = datetime.fromisoformat(license_data['expiry_date'])
            if datetime.now() > expiry_date:
                return {
                    'valid': False,
                    'message': '许可证已过期'
                }
            
            # 检查硬件绑定
            if check_hardware:
                current_hardware_info = self.get_hardware_info()
                current_fingerprint = self.generate_hardware_fingerprint(current_hardware_info)
                
                if current_fingerprint != license_data['hardware_fingerprint']:
                    return {
                        'valid': False,
                        'message': '硬件不匹配，许可证已绑定到其他设备'
                    }
            
            return {
                'valid': True,
                'message': '许可证有效',
                'license_data': license_data
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': f'许可证验证失败: {str(e)}'
            }

def format_license_key(license_key, group_size=4, groups=4):
    """
    格式化激活码，使其更易读
    
    Args:
        license_key (str): 原始激活码
        group_size (int): 每组字符数
        groups (int): 组数
        
    Returns:
        str: 格式化后的激活码
    """
    # 移除可能的空格和连字符
    clean_key = license_key.replace(' ', '').replace('-', '')
    
    # 分组
    formatted = '-'.join([clean_key[i:i+group_size] for i in range(0, min(len(clean_key), group_size*groups), group_size)])
    
    return formatted

# 使用示例
if __name__ == "__main__":
    # 初始化生成器 (在生产环境中，这个密钥应该安全存储)
    SECRET_KEY = "your-secret-key-here"
    generator = HardwareLicenseGenerator(SECRET_KEY)
    
    # 用户数据
    user_data = {
        "user_id": "12345",
        "user_name": "张三",
        "product": "专业版软件"
    }
    
    # 生成激活码
    license_key = generator.generate_license(user_data=user_data, expiry_days=30)
    formatted_key = format_license_key(license_key)
    
    print("生成的激活码:")
    print(formatted_key)
    print("\n原始激活码:")
    print(license_key)
    
    # 验证激活码
    print("\n验证激活码:")
    result = generator.validate_license(license_key)
    print(f"有效: {result['valid']}")
    print(f"消息: {result['message']}")
    
    if result['valid']:
        print(f"过期时间: {result['license_data']['expiry_date']}")
        print(f"用户信息: {result['license_data'].get('user_data', {})}")
```

## 功能说明

这个实现提供了以下功能：

1. **硬件信息收集**：
   - MAC地址
   - 主机名
   - 处理器信息
   - 系统信息
   - 硬盘序列号 (Windows)
   - 主板序列号 (Linux/macOS)

2. **硬件指纹生成**：
   - 基于关键硬件信息生成唯一指纹
   - 使用MD5哈希算法

3. **激活码生成**：
   - 包含硬件指纹、过期时间和用户数据
   - 使用HMAC-SHA256进行数字签名
   - Base64编码输出

4. **激活码验证**：
   - 验证数字签名
   - 检查过期时间
   - 验证硬件绑定

5. **格式化输出**：
   - 将激活码格式化为易读的形式

## 使用建议

1. **密钥管理**：在生产环境中，密钥应该安全存储，不要硬编码在代码中
2. **硬件选择**：根据目标平台选择合适的硬件信息用于绑定
3. **容错处理**：考虑硬件信息可能无法获取的情况
4. **服务器验证**：对于重要应用，建议在服务器端进行验证

这个实现可以根据具体需求进行调整和扩展。