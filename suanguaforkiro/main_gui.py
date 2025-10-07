"""
GUI entry point for the I Ching divination system.

This script initializes all necessary services and starts the GUI application.
"""

import tkinter as tk
import sys
import os

# Add src to path if needed
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

from src.gui.main_window import MainWindow
from src.data.hexagram_database import HexagramDatabase
from src.services.divination_service import DivinationService
from src.services.history_manager import HistoryManager
from src.gui.utils import show_error


def main():
    """Main entry point for the GUI application."""
    root = None
    
    try:
        # Initialize database
        print("Loading hexagram database...")
        try:
            database = HexagramDatabase()
            print(f"Loaded {len(database)} hexagrams")
        except FileNotFoundError as e:
            raise Exception(
                f"找不到卦象資料檔案：{e}\n\n"
                "請確認 src/data/hexagrams.json 檔案存在。"
            )
        except PermissionError as e:
            raise Exception(
                f"無法讀取卦象資料檔案：權限不足\n\n{e}\n\n"
                "請檢查檔案權限設定。"
            )
        except Exception as e:
            raise Exception(
                f"載入卦象資料時發生錯誤：\n\n{e}\n\n"
                "請檢查 src/data/hexagrams.json 檔案格式是否正確。"
            )
        
        # Initialize history manager
        print("Initializing history manager...")
        try:
            history_manager = HistoryManager("data/history.json")
        except PermissionError as e:
            # Show warning but continue - history is not critical
            print(f"Warning: Cannot access history file: {e}")
            print("Continuing without history functionality...")
            history_manager = HistoryManager("data/history.json")
        except Exception as e:
            # Show warning but continue
            print(f"Warning: History manager initialization issue: {e}")
            print("Continuing with limited history functionality...")
            history_manager = HistoryManager("data/history.json")
        
        # Initialize divination service
        print("Initializing divination service...")
        divination_service = DivinationService(database, history_manager)
        
        # Create root window
        print("Creating GUI window...")
        root = tk.Tk()
        
        # Set up global exception handler for tkinter
        def handle_tk_exception(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions in tkinter."""
            import traceback
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            print(f"Uncaught exception:\n{error_msg}")
            
            try:
                from src.gui.utils import show_error
                show_error(
                    "程式錯誤",
                    f"發生未預期的錯誤：\n\n{exc_value}\n\n"
                    "程式可能無法正常運作，建議重新啟動。"
                )
            except:
                pass
        
        # Set the exception handler
        sys.excepthook = handle_tk_exception
        
        # Create main window
        main_window = MainWindow(
            root,
            database,
            divination_service,
            history_manager
        )
        
        print("Starting application...")
        print("=" * 50)
        
        # Start the application
        main_window.run()
        
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        import traceback
        traceback.print_exc()
        
        # Show critical error dialog
        try:
            if root is None:
                root = tk.Tk()
            root.withdraw()
            show_error(
                "啟動失敗 - 檔案遺失",
                f"找不到必要的資料檔案：\n\n{str(e)}\n\n"
                "請確認程式檔案完整，特別是 src/data/hexagrams.json 檔案。"
            )
            if root:
                root.destroy()
        except:
            pass
        
        sys.exit(1)
    
    except PermissionError as e:
        print(f"Permission error: {e}")
        import traceback
        traceback.print_exc()
        
        # Show critical error dialog
        try:
            if root is None:
                root = tk.Tk()
            root.withdraw()
            show_error(
                "啟動失敗 - 權限不足",
                f"無法存取必要的檔案：\n\n{str(e)}\n\n"
                "請檢查檔案權限設定，確保程式有讀取權限。"
            )
            if root:
                root.destroy()
        except:
            pass
        
        sys.exit(1)
    
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to show error dialog if possible
        try:
            if root is None:
                root = tk.Tk()
            root.withdraw()
            show_error(
                "啟動錯誤",
                f"無法啟動應用程式：\n\n{str(e)}\n\n"
                "請檢查：\n"
                "1. 資料檔案是否存在且格式正確\n"
                "2. 程式是否有足夠的檔案存取權限\n"
                "3. Python 環境是否正確安裝"
            )
            if root:
                root.destroy()
        except:
            pass
        
        sys.exit(1)


if __name__ == "__main__":
    main()
