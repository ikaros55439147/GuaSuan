"""卦象生成器"""
import random
from typing import List
from src.models.yao import Yao, YaoType


class HexagramGenerator:
    """負責生成卦象"""
    
    def generate_yao(self) -> Yao:
        """
        生成一個爻
        
        使用三枚銅錢法的模擬：
        - 每枚銅錢：正面(3) 或 反面(2)
        - 三枚總和決定爻的類型：
          6 = 老陰 (變)
          7 = 少陽
          8 = 少陰
          9 = 老陽 (變)
        
        Returns:
            生成的爻對象（位置暫時設為0，由 generate_hexagram 設定）
        """
        # 模擬三枚銅錢：每枚可能是 2 或 3
        coin1 = random.choice([2, 3])
        coin2 = random.choice([2, 3])
        coin3 = random.choice([2, 3])
        total = coin1 + coin2 + coin3
        
        # 根據總和決定爻的類型
        if total == 6:
            yao_type = YaoType.OLD_YIN
        elif total == 7:
            yao_type = YaoType.YOUNG_YANG
        elif total == 8:
            yao_type = YaoType.YOUNG_YIN
        elif total == 9:
            yao_type = YaoType.OLD_YANG
        else:
            # 理論上不會發生，但作為安全措施
            raise ValueError(f"Invalid coin total: {total}")
        
        return Yao(yao_type, 0)  # 位置將在 generate_hexagram 中設定
    
    def generate_hexagram(self) -> List[Yao]:
        """
        生成完整的六爻列表
        
        Returns:
            包含六個爻的列表，從下到上（位置 1-6）
        """
        yaos = []
        for position in range(1, 7):  # 位置 1 到 6
            yao = self.generate_yao()
            yao.position = position
            yaos.append(yao)
        
        return yaos
