#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易經卜卦系統 - 主程式入口

這是一個基於傳統易經六十四卦的數位卜卦系統。
使用三枚銅錢法進行卜卦，提供卦象解釋和歷史記錄功能。
"""
import sys
import os

# 設定 Windows 控制台的 UTF-8 編碼
if sys.platform == 'win32':
    try:
        # 嘗試設定控制台為 UTF-8
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        # 如果設定失敗，繼續執行（使用預設編碼）
        pass

# 確保可以導入 src 模組
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.hexagram_database import HexagramDatabase
from src.services.history_manager import HistoryManager
from src.services.divination_service import DivinationService
from src.cli.divination_cli import DivinationCLI
from src.exceptions import DataLoadError, DivinationError


def main():
    """主程式入口點"""
    try:
        # 1. 初始化 HexagramDatabase（載入 hexagrams.json）
        print("正在初始化系統...")
        
        # 使用預設路徑載入卦象資料
        database = HexagramDatabase()
        print(f"[OK] 已載入 {len(database)} 個卦象資料")
        
        # 2. 初始化 HistoryManager（指定歷史記錄檔案路徑）
        # 將歷史記錄儲存在 data 目錄下
        history_file = os.path.join("data", "history.json")
        history_manager = HistoryManager(storage_file=history_file)
        print(f"[OK] 歷史記錄管理器已初始化")
        
        # 3. 初始化 DivinationService
        service = DivinationService(
            database=database,
            history_manager=history_manager
        )
        print(f"[OK] 卜卦服務已初始化")
        
        # 4. 初始化並啟動 DivinationCLI
        cli = DivinationCLI(service=service)
        
        # 5. 啟動 CLI
        cli.run()
        
    except DataLoadError as e:
        # 資料載入錯誤 - 這是致命錯誤，無法繼續
        print(f"\n[ERROR] 資料載入失敗：{e}")
        print("\n請確認以下事項：")
        print("  1. src/data/hexagrams.json 檔案是否存在")
        print("  2. 檔案格式是否正確")
        print("  3. 檔案是否有讀取權限")
        print("\n程式無法繼續執行。")
        sys.exit(1)
        
    except KeyboardInterrupt:
        # 使用者中斷（Ctrl+C）
        print("\n\n程式已被使用者中斷。")
        print("感謝使用易經卜卦系統，再見！\n")
        sys.exit(0)
        
    except DivinationError as e:
        # 其他卜卦系統錯誤
        print(f"\n[ERROR] 系統錯誤：{e}")
        print("\n程式將退出。如果問題持續發生，請聯繫技術支援。")
        sys.exit(1)
        
    except Exception as e:
        # 未預期的錯誤
        print(f"\n[ERROR] 發生未預期的錯誤：{e}")
        print("\n錯誤類型：", type(e).__name__)
        
        # 在開發模式下顯示詳細錯誤資訊
        import traceback
        print("\n詳細錯誤資訊：")
        traceback.print_exc()
        
        print("\n程式將退出。請將錯誤資訊回報給開發者。")
        sys.exit(1)


if __name__ == "__main__":
    main()
