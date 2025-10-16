import sqlite3
import os
import sys
from typing import List
from dataclasses import dataclass, field
from .db_setup import license_table

def data_path(relative_path):
    """获取资源的绝对路径"""
    try:
        base_path = sys._MEIPASS  # PyInstaller创建的临时文件夹
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

@dataclass
class License:
    device_fingerprint: str = field(default='')
    unit: str = field(default='')
    period: int = field(default=0)
    gen_timestamp: float = field(default=.0)
    expire_timestamp: float = field(default=.0)
    license: str = field(default='')
    
    # def to_dict():
    #     pass

class SQLiteManager():
    def __init__(self):
        self.conn = sqlite3.connect(data_path(".license.db"))
    
    def setup(self):
        cursor = self.conn.cursor()
        cursor.executescript(license_table)
        self.conn.commit()
        cursor.close()
    
    def create_license(
            self,
            fingerprint: str,
            unit: str,
            period: int,
            gen_timestamp: float,
            expire_timestamp: float,
            license: str
        ):
        conn = self.conn
        cursor = conn.cursor()
        cursor = cursor.execute(
            '''
                INSERT
                    INTO license (fingerprint, unit, period, gen_timestamp, expire_timestamp, license)
                VALUES
                    (?, ?, ?, ?, ?, ?)
                ON CONFLICT(fingerprint)
                DO UPDATE
                SET
                    unit = ?,
                    period = ?,
                    gen_timestamp = ?,
                    expire_timestamp = ?,
                    license = ?
            ''', (fingerprint, unit, period, gen_timestamp, expire_timestamp, license,
                  unit, period, gen_timestamp, expire_timestamp, license)
        )
        conn.commit()
        cursor.close()
        
    def list_license(self) -> List[License]:
        cursor = self.conn.cursor()
        cursor = cursor.execute(
            f"""
            SELECT
                fingerprint,
                unit,
                period,
                gen_timestamp,
                expire_timestamp,
                license
            FROM
                license
            """
        )
        licenses = cursor.fetchall()
        out: List[License] = []
        for row in licenses:
            out.append(License(
                device_fingerprint=row[0],
                unit=row[1], 
                period=row[2], 
                gen_timestamp=row[3],
                expire_timestamp=row[4],
                license=row[5]
            ))
        return out
    
    
if __name__ == "__main__":
    lics = [License("x"), License("x")]
    print([xx.device_fingerprint for xx in lics] ) 