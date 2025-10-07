"""卦象資料庫管理"""
import json
import os
from typing import Dict, Optional
from dataclasses import dataclass
from src.exceptions import DataLoadError, HexagramNotFoundError


@dataclass
class HexagramData:
    """卦象資料結構"""
    number: int
    name: str
    binary: str
    upper_trigram: str
    lower_trigram: str
    description: str
    yao_texts: list


class HexagramDatabase:
    """管理六十四卦的資料"""
    
    def __init__(self, data_file: str = None):
        """
        從 JSON 檔案載入卦象資料
        
        Args:
            data_file: JSON 資料檔案路徑，如果為 None 則使用預設路徑
        """
        if data_file is None:
            # 使用預設路徑：與此檔案同目錄下的 hexagrams.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(current_dir, 'hexagrams.json')
        
        self.data_file = data_file
        self._hexagrams_by_binary: Dict[str, HexagramData] = {}
        self._hexagrams_by_number: Dict[int, HexagramData] = {}
        self._hexagrams_by_name: Dict[str, HexagramData] = {}
        
        self._load_data()
    
    def _load_data(self) -> None:
        """從 JSON 檔案載入資料並建立索引"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise DataLoadError(f"找不到卦象資料檔案：{self.data_file}")
        except json.JSONDecodeError as e:
            raise DataLoadError(f"卦象資料檔案格式錯誤：{e}")
        except PermissionError:
            raise DataLoadError(f"沒有權限讀取卦象資料檔案：{self.data_file}")
        except Exception as e:
            raise DataLoadError(f"載入卦象資料時發生未預期的錯誤：{e}")
        
        try:
            hexagrams = data.get('hexagrams', [])
            
            if not hexagrams:
                raise DataLoadError("卦象資料檔案中沒有卦象資料")
            
            for hex_data in hexagrams:
                try:
                    hexagram = HexagramData(
                        number=hex_data['number'],
                        name=hex_data['name'],
                        binary=hex_data['binary'],
                        upper_trigram=hex_data['upper_trigram'],
                        lower_trigram=hex_data['lower_trigram'],
                        description=hex_data['description'],
                        yao_texts=hex_data['yao_texts']
                    )
                    
                    # 建立多個索引以支援不同的查找方式
                    self._hexagrams_by_binary[hexagram.binary] = hexagram
                    self._hexagrams_by_number[hexagram.number] = hexagram
                    self._hexagrams_by_name[hexagram.name] = hexagram
                except KeyError as e:
                    raise DataLoadError(f"卦象資料缺少必要欄位：{e}")
                except Exception as e:
                    raise DataLoadError(f"處理卦象資料時發生錯誤：{e}")
            
            # 驗證資料完整性
            if len(self._hexagrams_by_number) != 64:
                raise DataLoadError(f"卦象資料不完整，應有 64 卦，實際載入 {len(self._hexagrams_by_number)} 卦")
        
        except DataLoadError:
            raise
        except Exception as e:
            raise DataLoadError(f"處理卦象資料時發生未預期的錯誤：{e}")
    
    def get_by_binary(self, binary: str) -> HexagramData:
        """
        根據二進制編碼查找卦象
        
        Args:
            binary: 六位二進制字串，例如 "111111" 代表乾卦
        
        Returns:
            HexagramData 物件
        
        Raises:
            HexagramNotFoundError: 如果找不到對應的卦象
        """
        if not binary or len(binary) != 6:
            raise HexagramNotFoundError(f"無效的二進制編碼：{binary}（應為 6 位二進制字串）")
        
        hexagram = self._hexagrams_by_binary.get(binary)
        if hexagram is None:
            raise HexagramNotFoundError(f"找不到二進制編碼為 {binary} 的卦象")
        
        return hexagram
    
    def get_by_number(self, number: int) -> Optional[HexagramData]:
        """
        根據卦序查找卦象
        
        Args:
            number: 卦序 (1-64)
        
        Returns:
            HexagramData 物件，如果找不到則返回 None
        """
        return self._hexagrams_by_number.get(number)
    
    def get_by_name(self, name: str) -> Optional[HexagramData]:
        """
        根據卦名查找卦象
        
        Args:
            name: 卦名，例如 "乾"
        
        Returns:
            HexagramData 物件，如果找不到則返回 None
        """
        return self._hexagrams_by_name.get(name)
    
    def get_all_hexagrams(self) -> list:
        """
        獲取所有卦象資料
        
        Returns:
            所有 HexagramData 物件的列表，按卦序排序
        """
        return [self._hexagrams_by_number[i] for i in range(1, 65) if i in self._hexagrams_by_number]
    
    def __len__(self) -> int:
        """返回資料庫中的卦象數量"""
        return len(self._hexagrams_by_number)
    
    def __repr__(self) -> str:
        return f"HexagramDatabase(hexagrams={len(self)})"
