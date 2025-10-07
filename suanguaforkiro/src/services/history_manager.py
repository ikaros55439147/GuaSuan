"""歷史記錄管理"""
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
from .divination_service import DivinationResult
from src.exceptions import HistoryError


@dataclass
class DivinationRecord:
    """卜卦記錄"""
    id: str
    timestamp: str
    question: str
    original_hexagram_name: str
    original_hexagram_number: int
    has_changes: bool
    changed_hexagram_name: Optional[str]
    changed_hexagram_number: Optional[int]
    result_summary: str
    
    @classmethod
    def from_divination_result(cls, result: DivinationResult) -> 'DivinationRecord':
        """
        從 DivinationResult 建立記錄
        
        Args:
            result: DivinationResult 物件
        
        Returns:
            DivinationRecord 物件
        """
        # 生成唯一 ID（使用時間戳）
        record_id = result.timestamp.strftime("%Y%m%d%H%M%S%f")
        
        # 建立結果摘要
        summary = f"{result.original_hexagram.name}卦"
        if result.has_changes() and result.changed_hexagram:
            summary += f" → {result.changed_hexagram.name}卦"
        
        return cls(
            id=record_id,
            timestamp=result.timestamp.isoformat(),
            question=result.question,
            original_hexagram_name=result.original_hexagram.name,
            original_hexagram_number=result.original_hexagram.number,
            has_changes=result.has_changes(),
            changed_hexagram_name=result.changed_hexagram.name if result.changed_hexagram else None,
            changed_hexagram_number=result.changed_hexagram.number if result.changed_hexagram else None,
            result_summary=summary
        )


class HistoryManager:
    """管理卜卦歷史記錄"""
    
    def __init__(self, storage_file: str = "divination_history.json"):
        """
        初始化歷史記錄管理器
        
        Args:
            storage_file: 儲存檔案的路徑
        """
        self.storage_file = storage_file
        self._ensure_storage_file()
    
    def _ensure_storage_file(self) -> None:
        """
        確保儲存檔案存在，如果不存在則建立
        
        Raises:
            HistoryError: 如果無法建立儲存檔案
        """
        if not os.path.exists(self.storage_file):
            try:
                # 確保目錄存在
                storage_dir = os.path.dirname(self.storage_file)
                if storage_dir and not os.path.exists(storage_dir):
                    os.makedirs(storage_dir, exist_ok=True)
                
                # 建立空的記錄檔案
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump({"records": []}, f, ensure_ascii=False, indent=2)
            except PermissionError:
                raise HistoryError(f"沒有權限建立歷史記錄檔案：{self.storage_file}")
            except OSError as e:
                raise HistoryError(f"建立歷史記錄檔案時發生錯誤：{e}")
            except Exception as e:
                raise HistoryError(f"建立歷史記錄檔案時發生未預期的錯誤：{e}")
    
    def save_record(self, result: DivinationResult) -> None:
        """
        儲存一筆卜卦記錄
        
        Args:
            result: DivinationResult 物件
        
        Raises:
            HistoryError: 如果儲存記錄時發生錯誤
        """
        try:
            # 建立記錄
            record = DivinationRecord.from_divination_result(result)
            
            # 讀取現有記錄
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                # 檔案不存在，建立新的
                data = {"records": []}
            except json.JSONDecodeError:
                # 檔案損壞，備份並建立新的
                backup_file = f"{self.storage_file}.backup"
                try:
                    if os.path.exists(self.storage_file):
                        os.rename(self.storage_file, backup_file)
                except:
                    pass
                data = {"records": []}
            
            # 添加新記錄
            data["records"].append(asdict(record))
            
            # 寫回檔案
            try:
                with open(self.storage_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except PermissionError:
                raise HistoryError(f"沒有權限寫入歷史記錄檔案：{self.storage_file}")
            except OSError as e:
                raise HistoryError(f"寫入歷史記錄檔案時發生錯誤：{e}")
        
        except HistoryError:
            raise
        except Exception as e:
            raise HistoryError(f"儲存記錄時發生未預期的錯誤：{e}")
    
    def get_all_records(self) -> List[DivinationRecord]:
        """
        獲取所有歷史記錄
        
        Returns:
            DivinationRecord 物件的列表，按時間倒序排列（最新的在前）
        
        Raises:
            HistoryError: 如果讀取記錄時發生嚴重錯誤
        """
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            # 檔案不存在，返回空列表
            return []
        except json.JSONDecodeError:
            # 檔案損壞，嘗試恢復或返回空列表
            raise HistoryError(f"歷史記錄檔案損壞，無法讀取：{self.storage_file}")
        except PermissionError:
            raise HistoryError(f"沒有權限讀取歷史記錄檔案：{self.storage_file}")
        except Exception as e:
            raise HistoryError(f"讀取歷史記錄時發生未預期的錯誤：{e}")
        
        try:
            records = []
            for record_data in data.get("records", []):
                try:
                    record = DivinationRecord(**record_data)
                    records.append(record)
                except Exception as e:
                    # 跳過損壞的記錄，繼續處理其他記錄
                    continue
            
            # 按時間倒序排列
            records.sort(key=lambda r: r.timestamp, reverse=True)
            
            return records
        
        except Exception as e:
            raise HistoryError(f"處理歷史記錄時發生錯誤：{e}")
    
    def get_record_by_id(self, record_id: str) -> Optional[DivinationRecord]:
        """
        根據 ID 獲取特定記錄
        
        Args:
            record_id: 記錄的 ID
        
        Returns:
            DivinationRecord 物件，如果找不到則返回 None
        """
        all_records = self.get_all_records()
        
        for record in all_records:
            if record.id == record_id:
                return record
        
        return None
    
    def search_records(self, keyword: str) -> List[DivinationRecord]:
        """
        搜尋包含關鍵字的記錄
        
        Args:
            keyword: 搜尋關鍵字
        
        Returns:
            符合條件的 DivinationRecord 物件列表
        
        Raises:
            HistoryError: 如果搜尋時發生錯誤
        """
        if not keyword or not keyword.strip():
            return []
        
        try:
            all_records = self.get_all_records()
            
            # 在問題內容中搜尋關鍵字
            matching_records = []
            keyword_lower = keyword.lower()
            
            for record in all_records:
                try:
                    if keyword_lower in record.question.lower():
                        matching_records.append(record)
                except Exception:
                    # 跳過有問題的記錄
                    continue
            
            return matching_records
        
        except HistoryError:
            raise
        except Exception as e:
            raise HistoryError(f"搜尋記錄時發生錯誤：{e}")
