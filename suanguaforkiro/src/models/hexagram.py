"""卦象的資料模型"""
from typing import List, Optional, TYPE_CHECKING
from .yao import Yao

if TYPE_CHECKING:
    from ..data.hexagram_database import HexagramDatabase


class Hexagram:
    """代表一個完整的卦象"""
    
    def __init__(
        self,
        yaos: List[Yao],
        name: str = "",
        number: int = 0,
        upper_trigram: str = "",
        lower_trigram: str = "",
        description: str = "",
        yao_texts: Optional[List[str]] = None
    ):
        """
        初始化卦象
        
        Args:
            yaos: 六個爻的列表，從下到上
            name: 卦名
            number: 卦序 (1-64)
            upper_trigram: 上卦
            lower_trigram: 下卦
            description: 卦辭
            yao_texts: 六個爻辭的列表
        """
        if len(yaos) != 6:
            raise ValueError("卦象必須包含六個爻")
        
        self.yaos = yaos
        self.name = name
        self.number = number
        self.upper_trigram = upper_trigram
        self.lower_trigram = lower_trigram
        self.description = description
        self.yao_texts = yao_texts or []
    
    def to_binary(self) -> str:
        """
        返回卦象的二進制表示
        
        陽爻為 1，陰爻為 0，從下到上排列
        
        Returns:
            六位二進制字串，例如 "111111" 代表乾卦
        """
        binary = ""
        for yao in self.yaos:
            if yao.is_yang():
                binary += "1"
            else:
                binary += "0"
        return binary
    
    def get_changing_yaos(self) -> List[Yao]:
        """
        獲取所有變爻
        
        Returns:
            變爻的列表
        """
        return [yao for yao in self.yaos if yao.is_changing]
    
    def get_changed_hexagram(self, database: Optional['HexagramDatabase'] = None) -> Optional['Hexagram']:
        """
        如果有變爻，生成之卦
        
        Args:
            database: HexagramDatabase 實例，用於查找之卦的完整資料
        
        Returns:
            之卦的 Hexagram 對象，如果沒有變爻則返回 None
        """
        changing_yaos = self.get_changing_yaos()
        if not changing_yaos:
            return None
        
        # 生成變化後的爻列表（老陰變少陽，老陽變少陰）
        changed_yaos = []
        for yao in self.yaos:
            if yao.is_changing:
                changed_yaos.append(yao.get_changed())
            else:
                # 保持原有的爻不變
                changed_yaos.append(Yao(yao.type, yao.position))
        
        # 如果沒有提供資料庫，返回基本的卦象
        if database is None:
            return Hexagram(changed_yaos)
        
        # 計算變化後的二進制編碼
        changed_binary = ""
        for yao in changed_yaos:
            if yao.is_yang():
                changed_binary += "1"
            else:
                changed_binary += "0"
        
        # 從資料庫查找對應的之卦資料
        hexagram_data = database.get_by_binary(changed_binary)
        
        if hexagram_data is None:
            # 如果找不到對應的卦象，返回基本的卦象
            return Hexagram(changed_yaos)
        
        # 返回完整的之卦 Hexagram 物件
        return Hexagram(
            yaos=changed_yaos,
            name=hexagram_data.name,
            number=hexagram_data.number,
            upper_trigram=hexagram_data.upper_trigram,
            lower_trigram=hexagram_data.lower_trigram,
            description=hexagram_data.description,
            yao_texts=hexagram_data.yao_texts
        )
    
    def __repr__(self) -> str:
        return f"Hexagram(name={self.name}, number={self.number}, binary={self.to_binary()})"
