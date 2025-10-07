"""爻的資料模型"""
from enum import Enum
from typing import Optional


class YaoType(Enum):
    """爻的類型"""
    OLD_YIN = "老陰"      # 6, 變爻
    YOUNG_YANG = "少陽"   # 7
    YOUNG_YIN = "少陰"    # 8
    OLD_YANG = "老陽"     # 9, 變爻


class Yao:
    """代表一個爻"""
    
    def __init__(self, yao_type: YaoType, position: int):
        """
        初始化爻
        
        Args:
            yao_type: 爻的類型
            position: 位置 (1-6，從下到上)
        """
        self.type = yao_type
        self.position = position
        self.is_changing = yao_type in (YaoType.OLD_YIN, YaoType.OLD_YANG)
    
    def to_symbol(self) -> str:
        """
        返回爻的符號表示
        
        Returns:
            陽爻返回 "━━━━━━"，陰爻返回 "━━  ━━"
        """
        if self.type in (YaoType.YOUNG_YANG, YaoType.OLD_YANG):
            return "━━━━━━"
        else:
            return "━━  ━━"
    
    def is_yang(self) -> bool:
        """判斷是否為陽爻"""
        return self.type in (YaoType.YOUNG_YANG, YaoType.OLD_YANG)
    
    def is_yin(self) -> bool:
        """判斷是否為陰爻"""
        return self.type in (YaoType.YOUNG_YIN, YaoType.OLD_YIN)
    
    def get_changed(self) -> 'Yao':
        """
        如果是變爻，返回變化後的爻
        
        Returns:
            變化後的爻對象
        """
        if self.type == YaoType.OLD_YIN:
            return Yao(YaoType.YOUNG_YANG, self.position)
        elif self.type == YaoType.OLD_YANG:
            return Yao(YaoType.YOUNG_YIN, self.position)
        else:
            return Yao(self.type, self.position)
    
    def __repr__(self) -> str:
        return f"Yao(type={self.type.value}, position={self.position}, changing={self.is_changing})"
