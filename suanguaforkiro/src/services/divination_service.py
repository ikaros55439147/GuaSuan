"""卜卦核心服務"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from ..models.hexagram import Hexagram
from ..models.yao import Yao
from ..data.hexagram_database import HexagramDatabase
from .hexagram_generator import HexagramGenerator
from src.exceptions import DivinationError, HexagramNotFoundError, InvalidInputError


@dataclass
class DivinationResult:
    """卜卦結果"""
    question: str
    timestamp: datetime
    original_hexagram: Hexagram
    changing_yaos: List[Yao]
    changed_hexagram: Optional[Hexagram]
    
    def has_changes(self) -> bool:
        """
        是否有變爻
        
        Returns:
            如果有變爻返回 True，否則返回 False
        """
        return len(self.changing_yaos) > 0


class DivinationService:
    """核心卜卦服務"""
    
    def __init__(self, database: HexagramDatabase, history_manager=None):
        """
        初始化卜卦服務
        
        Args:
            database: HexagramDatabase 實例
            history_manager: HistoryManager 實例（可選）
        """
        self.database = database
        self.generator = HexagramGenerator()
        self.history_manager = history_manager
    
    def perform_divination(self, question: str) -> DivinationResult:
        """
        執行完整的卜卦流程
        
        流程：
        1. 生成六個爻
        2. 查找對應的卦象資料
        3. 如有變爻，生成之卦
        4. 組合結果
        
        Args:
            question: 使用者的問題
        
        Returns:
            DivinationResult 物件，包含完整的卜卦結果
        
        Raises:
            InvalidInputError: 如果問題無效
            HexagramNotFoundError: 如果找不到對應的卦象
            DivinationError: 如果卜卦過程中發生其他錯誤
        """
        # 驗證輸入
        if not question or not question.strip():
            raise InvalidInputError("問題不能為空")
        
        if len(question) > 500:
            raise InvalidInputError("問題過長（最多 500 字）")
        
        try:
            # 1. 生成六個爻
            yaos = self.generator.generate_hexagram()
            
            if len(yaos) != 6:
                raise DivinationError(f"生成的爻數量不正確：{len(yaos)}（應為 6）")
            
            # 2. 查找對應的卦象資料
            binary = self._yaos_to_binary(yaos)
            hexagram_data = self.database.get_by_binary(binary)
            
            # 建立本卦 Hexagram 物件
            original_hexagram = Hexagram(
                yaos=yaos,
                name=hexagram_data.name,
                number=hexagram_data.number,
                upper_trigram=hexagram_data.upper_trigram,
                lower_trigram=hexagram_data.lower_trigram,
                description=hexagram_data.description,
                yao_texts=hexagram_data.yao_texts
            )
            
            # 3. 識別變爻
            changing_yaos = original_hexagram.get_changing_yaos()
            
            # 4. 如有變爻，生成之卦
            changed_hexagram = None
            if changing_yaos:
                try:
                    changed_hexagram = original_hexagram.get_changed_hexagram(self.database)
                except HexagramNotFoundError:
                    # 如果找不到之卦，記錄但不中斷流程
                    changed_hexagram = None
            
            # 5. 組合結果
            result = DivinationResult(
                question=question,
                timestamp=datetime.now(),
                original_hexagram=original_hexagram,
                changing_yaos=changing_yaos,
                changed_hexagram=changed_hexagram
            )
            
            return result
        
        except HexagramNotFoundError:
            raise
        except InvalidInputError:
            raise
        except Exception as e:
            raise DivinationError(f"卜卦過程中發生錯誤：{e}")
    
    def interpret_result(self, result: DivinationResult) -> str:
        """
        格式化卜卦結果為可讀文字
        
        Args:
            result: DivinationResult 物件
        
        Returns:
            格式化的結果文字
        """
        lines = []
        
        # 標題
        lines.append("=" * 50)
        lines.append(f"問題：{result.question}")
        lines.append(f"時間：{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 50)
        lines.append("")
        
        # 本卦資訊
        lines.append("【本卦】")
        lines.append(f"卦名：{result.original_hexagram.name}")
        lines.append(f"卦序：第 {result.original_hexagram.number} 卦")
        lines.append(f"組成：上卦 {result.original_hexagram.upper_trigram}，下卦 {result.original_hexagram.lower_trigram}")
        lines.append("")
        
        # 顯示卦象
        lines.append("卦象：")
        for i in range(5, -1, -1):  # 從上到下顯示
            yao = result.original_hexagram.yaos[i]
            symbol = yao.to_symbol()
            changing_mark = " ○" if yao.is_changing else ""
            lines.append(f"  {symbol}{changing_mark}")
        lines.append("")
        
        # 卦辭
        lines.append(f"卦辭：{result.original_hexagram.description}")
        lines.append("")
        
        # 變爻資訊
        if result.has_changes():
            lines.append("【變爻】")
            for yao in result.changing_yaos:
                yao_name = self._get_yao_name(yao.position)
                yao_text = result.original_hexagram.yao_texts[yao.position - 1]
                lines.append(f"{yao_name}：{yao_text}")
            lines.append("")
            
            # 之卦資訊
            if result.changed_hexagram:
                lines.append("【之卦】")
                lines.append(f"卦名：{result.changed_hexagram.name}")
                lines.append(f"卦序：第 {result.changed_hexagram.number} 卦")
                lines.append(f"組成：上卦 {result.changed_hexagram.upper_trigram}，下卦 {result.changed_hexagram.lower_trigram}")
                lines.append("")
                
                # 顯示之卦卦象
                lines.append("卦象：")
                for i in range(5, -1, -1):  # 從上到下顯示
                    yao = result.changed_hexagram.yaos[i]
                    symbol = yao.to_symbol()
                    lines.append(f"  {symbol}")
                lines.append("")
                
                # 之卦卦辭
                lines.append(f"卦辭：{result.changed_hexagram.description}")
                lines.append("")
        else:
            lines.append("【無變爻】")
            lines.append("本次卜卦沒有變爻，專注於本卦的卦辭即可。")
            lines.append("")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _yaos_to_binary(self, yaos: List[Yao]) -> str:
        """
        將爻列表轉換為二進制字串
        
        Args:
            yaos: 爻的列表
        
        Returns:
            二進制字串
        """
        binary = ""
        for yao in yaos:
            if yao.is_yang():
                binary += "1"
            else:
                binary += "0"
        return binary
    
    def _get_yao_name(self, position: int) -> str:
        """
        根據位置獲取爻的名稱
        
        Args:
            position: 爻的位置 (1-6)
        
        Returns:
            爻的名稱，例如 "初九"、"六二" 等
        """
        position_names = {
            1: "初",
            2: "二",
            3: "三",
            4: "四",
            5: "五",
            6: "上"
        }
        
        # 注意：實際的爻名需要根據陰陽來決定（九代表陽，六代表陰）
        # 這裡簡化處理，只返回位置名稱
        # 完整實現需要根據爻的陰陽屬性來決定
        return position_names.get(position, str(position))
