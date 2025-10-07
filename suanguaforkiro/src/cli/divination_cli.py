"""命令列介面模組"""
from typing import Optional
from datetime import datetime
from src.services.divination_service import DivinationService, DivinationResult
from src.models.hexagram import Hexagram
from src.models.yao import Yao
from src.exceptions import DivinationError, DataLoadError, HexagramNotFoundError, HistoryError, InvalidInputError


class DivinationCLI:
    """卜卦系統的命令列介面"""
    
    def __init__(self, service: DivinationService):
        """
        初始化 CLI
        
        Args:
            service: 卜卦服務實例
        """
        self.service = service
        self.running = False
    
    def show_welcome(self) -> None:
        """顯示歡迎訊息和程式說明"""
        print("\n" + "=" * 50)
        print("╔" + "=" * 48 + "╗")
        print("║" + " " * 12 + "易經卜卦系統 v1.0" + " " * 12 + "║")
        print("╚" + "=" * 48 + "╝")
        print("=" * 50)
        print("\n歡迎使用易經卜卦系統！")
        print("\n本系統使用傳統三枚銅錢法進行卜卦，")
        print("您可以輸入問題，系統將為您生成卦象並提供解釋。")
        print("\n" + "=" * 50 + "\n")
    
    def show_menu(self) -> None:
        """顯示主選單"""
        print("\n請選擇功能：\n")
        print("  1. 開始卜卦")
        print("  2. 查看歷史記錄")
        print("  3. 關於本程式")
        print("  4. 退出")
        print()
    
    def show_about(self) -> None:
        """顯示關於資訊"""
        print("\n" + "=" * 50)
        print("關於易經卜卦系統")
        print("=" * 50)
        print("\n版本：1.0")
        print("卜卦方法：三枚銅錢法")
        print("\n三枚銅錢法說明：")
        print("  - 系統模擬擲三枚銅錢")
        print("  - 根據正反面組合決定爻的陰陽")
        print("  - 六次擲錢形成完整卦象")
        print("  - 老陰、老陽為變爻，會產生之卦")
        print("\n" + "=" * 50 + "\n")
    
    def get_user_choice(self) -> Optional[str]:
        """
        獲取使用者選擇並進行驗證
        
        Returns:
            使用者輸入的選項，如果輸入無效則返回 None
        """
        try:
            choice = input("請輸入選項 (1-4)：").strip()
            
            # 驗證輸入
            if not choice:
                print("\n[ERROR] 請輸入選項。")
                return None
            
            if choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("\n[ERROR] 無效的選項，請輸入 1-4 之間的數字。")
                return None
        except (EOFError, KeyboardInterrupt):
            print("\n\n程式已中斷。")
            return '4'
        except Exception as e:
            print(f"\n[ERROR] 輸入錯誤：{e}")
            print("請重試。")
            return None
    
    def run(self) -> None:
        """主程式迴圈"""
        self.running = True
        self.show_welcome()
        
        while self.running:
            try:
                self.show_menu()
                choice = self.get_user_choice()
                
                if choice is None:
                    continue
                
                if choice == '1':
                    self.handle_divination()
                elif choice == '2':
                    self.handle_history()
                elif choice == '3':
                    self.show_about()
                elif choice == '4':
                    self.handle_exit()
                    
            except KeyboardInterrupt:
                print("\n\n程式已中斷。")
                self.handle_exit()
            except DataLoadError as e:
                print(f"\n[ERROR] 資料載入錯誤：{e}")
                print("請檢查資料檔案是否存在且格式正確。")
                print("程式將退出。\n")
                self.running = False
            except HistoryError as e:
                print(f"\n[ERROR] 歷史記錄錯誤：{e}")
                print("歷史記錄功能可能暫時無法使用，但不影響卜卦功能。")
                print("您可以繼續使用其他功能。\n")
            except DivinationError as e:
                print(f"\n[ERROR] 卜卦系統錯誤：{e}")
                print("請重試或聯繫技術支援。\n")
            except Exception as e:
                print(f"\n[ERROR] 發生未預期的錯誤：{e}")
                print("程式將繼續運行，請重試。\n")
    
    def perform_divination_flow(self) -> None:
        """
        執行卜卦流程
        
        流程：
        1. 提示使用者輸入問題
        2. 呼叫 DivinationService 執行卜卦
        3. 顯示生成過程（可選：顯示每個爻的生成）
        4. 使用 display_result() 顯示完整結果
        5. 詢問是否儲存到歷史記錄
        """
        print("\n" + "=" * 60)
        print(" " * 20 + "【開始卜卦】")
        print("=" * 60)
        
        # 1. 提示使用者輸入問題
        print("\n請輸入您的問題（或輸入 'q' 返回主選單）：")
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n已取消卜卦。")
            return
        except Exception as e:
            print(f"\n[ERROR] 輸入錯誤：{e}")
            return
        
        # 檢查是否取消
        if question.lower() == 'q':
            print("\n已取消卜卦。")
            return
        
        # 驗證問題不為空
        if not question:
            print("\n[ERROR] 問題不能為空，請重新開始。")
            return
        
        # 驗證問題長度
        if len(question) > 200:
            print("\n[ERROR] 問題過長（最多 200 字），請簡化您的問題。")
            return
        
        # 2. 執行卜卦
        print("\n正在為您卜卦，請稍候...")
        print("擲錢中...\n")
        
        try:
            # 呼叫 DivinationService 執行卜卦
            result = self.service.perform_divination(question)
            
            # 3. 可選：顯示每個爻的生成過程
            print("生成六爻：")
            for i, yao in enumerate(result.original_hexagram.yaos, 1):
                yao_type = yao.type.value  # YaoType.value 已經是中文字串
                changing_mark = " (變爻)" if yao.is_changing else ""
                print(f"  第 {i} 爻：{yao.to_symbol()} - {yao_type}{changing_mark}")
            
            print("\n卜卦完成！\n")
            
            # 4. 使用 display_result() 顯示完整結果
            self.display_result(result)
            
            # 5. 詢問是否儲存到歷史記錄
            print("是否將此次卜卦結果儲存到歷史記錄？(y/n)")
            try:
                save_choice = input("> ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n未儲存記錄。")
                return
            except Exception as e:
                print(f"\n[ERROR] 輸入錯誤：{e}")
                print("未儲存記錄。")
                return
            
            if save_choice in ['y', 'yes', '是', 'Y']:
                try:
                    self.service.history_manager.save_record(result)
                    print("\n[OK] 記錄已成功儲存！")
                except HistoryError as e:
                    print(f"\n[WARNING] 儲存記錄時發生錯誤：{e}")
                    print("但卜卦結果已顯示，您可以手動記錄。")
                except Exception as e:
                    print(f"\n[WARNING] 儲存記錄時發生未預期的錯誤：{e}")
                    print("但卜卦結果已顯示，您可以手動記錄。")
            else:
                print("\n未儲存記錄。")
        
        except HexagramNotFoundError as e:
            print(f"\n[ERROR] 卦象查找錯誤：{e}")
            print("這可能是資料檔案的問題，請聯繫技術支援。")
        except DivinationError as e:
            print(f"\n[ERROR] 卜卦錯誤：{e}")
            print("請重試。")
        except Exception as e:
            print(f"\n[ERROR] 卜卦過程中發生未預期的錯誤：{e}")
            print("請重試或聯繫技術支援。")
    
    def handle_divination(self) -> None:
        """處理卜卦選項"""
        self.perform_divination_flow()
    
    def handle_history(self) -> None:
        """處理歷史記錄選項"""
        self.show_history_flow()
    
    def handle_exit(self) -> None:
        """處理退出選項"""
        print("\n感謝使用易經卜卦系統，再見！\n")
        self.running = False
    
    def display_hexagram(self, hexagram: Hexagram, show_changing: bool = True) -> None:
        """
        視覺化顯示單個卦象
        
        Args:
            hexagram: 要顯示的卦象
            show_changing: 是否標記變爻位置
        """
        print(f"\n卦名：{hexagram.name}")
        
        if hexagram.number > 0:
            print(f"卦序：第 {hexagram.number} 卦")
        
        if hexagram.upper_trigram and hexagram.lower_trigram:
            print(f"組成：上卦 {hexagram.upper_trigram}，下卦 {hexagram.lower_trigram}")
        
        print("\n卦象：")
        
        # 從上到下顯示六爻（位置 6 到 1）
        for i in range(5, -1, -1):
            yao = hexagram.yaos[i]
            symbol = yao.to_symbol()
            
            # 獲取爻名
            yao_name = self._get_yao_name(yao, hexagram.yaos[i])
            
            # 標記變爻
            changing_mark = ""
            if show_changing and yao.is_changing:
                changing_mark = " ○"
            
            print(f"  {yao_name}  {symbol}{changing_mark}")
        
        # 顯示卦辭
        if hexagram.description:
            print(f"\n卦辭：{hexagram.description}")
    
    def display_result(self, result: DivinationResult) -> None:
        """
        顯示完整卜卦結果（本卦 + 變爻 + 之卦）
        
        Args:
            result: 卜卦結果
        """
        # 頂部分隔線
        print("\n" + "=" * 60)
        print(f"問題：{result.question}")
        print(f"時間：{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 顯示本卦
        print("\n" + "─" * 60)
        print(" " * 20 + "【本卦】")
        print("─" * 60)
        self.display_hexagram(result.original_hexagram, show_changing=True)
        
        # 如果有變爻，顯示變爻資訊和之卦
        if result.has_changes():
            print("\n" + "─" * 60)
            print(" " * 20 + "【變爻】")
            print("─" * 60)
            
            # 顯示每個變爻的爻辭
            for yao in result.changing_yaos:
                yao_name = self._get_yao_name(yao, result.original_hexagram.yaos[yao.position - 1])
                
                # 獲取對應的爻辭
                if yao.position - 1 < len(result.original_hexagram.yao_texts):
                    yao_text = result.original_hexagram.yao_texts[yao.position - 1]
                    print(f"\n{yao_name}（第 {yao.position} 爻）：{yao_text}")
                else:
                    print(f"\n{yao_name}（第 {yao.position} 爻）")
            
            # 顯示之卦
            if result.changed_hexagram:
                print("\n" + "─" * 60)
                print(" " * 20 + "【之卦】")
                print("─" * 60)
                self.display_hexagram(result.changed_hexagram, show_changing=False)
        else:
            print("\n" + "─" * 60)
            print(" " * 20 + "【無變爻】")
            print("─" * 60)
            print("\n本次卜卦沒有變爻，專注於本卦的卦辭即可。")
        
        # 底部分隔線
        print("\n" + "=" * 60 + "\n")
    
    def show_history_flow(self) -> None:
        """
        顯示歷史記錄流程
        
        流程：
        1. 顯示歷史記錄列表（日期、問題摘要、卦名）
        2. 提供選項：查看詳細記錄、搜尋、返回主選單
        3. 實作查看特定記錄的詳細資訊功能
        4. 實作搜尋功能，根據關鍵字過濾記錄
        """
        while True:
            print("\n" + "=" * 60)
            print(" " * 20 + "【歷史記錄】")
            print("=" * 60)
            
            # 獲取所有記錄
            try:
                records = self.service.history_manager.get_all_records()
            except HistoryError as e:
                print(f"\n[ERROR] 讀取歷史記錄時發生錯誤：{e}")
                print("歷史記錄功能暫時無法使用。")
                print("\n按 Enter 鍵返回主選單...")
                try:
                    input()
                except:
                    pass
                return
            except Exception as e:
                print(f"\n[ERROR] 讀取歷史記錄時發生未預期的錯誤：{e}")
                print("\n按 Enter 鍵返回主選單...")
                try:
                    input()
                except:
                    pass
                return
            
            # 顯示記錄列表
            if not records:
                print("\n目前沒有歷史記錄。")
                print("\n按 Enter 鍵返回主選單...")
                try:
                    input()
                except (EOFError, KeyboardInterrupt):
                    pass
                return
            
            print(f"\n共有 {len(records)} 筆記錄：\n")
            
            # 顯示記錄列表（最多顯示前 20 筆）
            display_count = min(len(records), 20)
            for i, record in enumerate(records[:display_count], 1):
                # 格式化時間
                try:
                    timestamp = datetime.fromisoformat(record.timestamp)
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M")
                except:
                    time_str = record.timestamp[:16]
                
                # 截斷問題（最多顯示 30 個字元）
                question_display = record.question[:30]
                if len(record.question) > 30:
                    question_display += "..."
                
                # 顯示記錄
                print(f"  {i:2d}. [{time_str}] {question_display}")
                print(f"      {record.result_summary}")
            
            if len(records) > display_count:
                print(f"\n  ... 還有 {len(records) - display_count} 筆記錄")
            
            # 顯示選項
            print("\n" + "-" * 60)
            print("請選擇操作：")
            print("  1. 查看詳細記錄（輸入編號）")
            print("  2. 搜尋記錄")
            print("  3. 返回主選單")
            print()
            
            try:
                choice = input("請輸入選項 (1-3)：").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                return
            
            if choice == '1':
                # 查看詳細記錄
                self._view_record_detail(records[:display_count])
            elif choice == '2':
                # 搜尋記錄
                self._search_records()
            elif choice == '3':
                # 返回主選單
                return
            else:
                print("\n[ERROR] 無效的選項，請輸入 1-3 之間的數字。")
    
    def _view_record_detail(self, records: list) -> None:
        """
        查看特定記錄的詳細資訊
        
        Args:
            records: 當前顯示的記錄列表
        """
        print()
        try:
            index_input = input("請輸入要查看的記錄編號（或按 Enter 取消）：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            return
        
        if not index_input:
            return
        
        try:
            index = int(index_input)
            if index < 1 or index > len(records):
                print(f"\n[ERROR] 無效的編號，請輸入 1-{len(records)} 之間的數字。")
                return
        except ValueError:
            print("\n[ERROR] 請輸入有效的數字。")
            return
        except Exception as e:
            print(f"\n[ERROR] 輸入錯誤：{e}")
            return
        
        # 獲取選中的記錄
        record = records[index - 1]
        
        # 顯示詳細資訊
        print("\n" + "=" * 60)
        print(" " * 20 + "【記錄詳情】")
        print("=" * 60)
        
        # 格式化時間
        try:
            timestamp = datetime.fromisoformat(record.timestamp)
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = record.timestamp
        
        print(f"\n記錄 ID：{record.id}")
        print(f"時間：{time_str}")
        print(f"問題：{record.question}")
        print(f"\n本卦：{record.original_hexagram_name}（第 {record.original_hexagram_number} 卦）")
        
        if record.has_changes and record.changed_hexagram_name:
            print(f"之卦：{record.changed_hexagram_name}（第 {record.changed_hexagram_number} 卦）")
            print(f"\n結果摘要：{record.result_summary}")
        else:
            print("\n無變爻")
        
        print("\n" + "=" * 60)
        
        # 等待使用者按鍵
        print("\n按 Enter 鍵繼續...")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            print("\n")
    
    def _search_records(self) -> None:
        """
        搜尋記錄功能
        """
        print()
        try:
            keyword = input("請輸入搜尋關鍵字（或按 Enter 取消）：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            return
        
        if not keyword:
            return
        
        # 執行搜尋
        try:
            results = self.service.history_manager.search_records(keyword)
        except HistoryError as e:
            print(f"\n[ERROR] 搜尋時發生錯誤：{e}")
            print("\n按 Enter 鍵繼續...")
            try:
                input()
            except:
                pass
            return
        except Exception as e:
            print(f"\n[ERROR] 搜尋時發生未預期的錯誤：{e}")
            print("\n按 Enter 鍵繼續...")
            try:
                input()
            except:
                pass
            return
        
        # 顯示搜尋結果
        print("\n" + "=" * 60)
        print(f" " * 15 + f"【搜尋結果：{keyword}】")
        print("=" * 60)
        
        if not results:
            print(f"\n未找到包含「{keyword}」的記錄。")
            print("\n按 Enter 鍵繼續...")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                print("\n")
            return
        
        print(f"\n找到 {len(results)} 筆符合的記錄：\n")
        
        # 顯示搜尋結果
        for i, record in enumerate(results, 1):
            # 格式化時間
            try:
                timestamp = datetime.fromisoformat(record.timestamp)
                time_str = timestamp.strftime("%Y-%m-%d %H:%M")
            except:
                time_str = record.timestamp[:16]
            
            # 截斷問題（最多顯示 30 個字元）
            question_display = record.question[:30]
            if len(record.question) > 30:
                question_display += "..."
            
            # 顯示記錄
            print(f"  {i:2d}. [{time_str}] {question_display}")
            print(f"      {record.result_summary}")
        
        print("\n" + "-" * 60)
        print("請選擇操作：")
        print("  1. 查看詳細記錄（輸入編號）")
        print("  2. 返回")
        print()
        
        try:
            choice = input("請輸入選項 (1-2)：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            return
        
        if choice == '1':
            # 查看詳細記錄
            self._view_record_detail(results)
        # 其他選項或無效輸入都返回
    
    def _get_yao_name(self, yao: Yao, actual_yao: Yao) -> str:
        """
        根據爻的位置和陰陽屬性獲取爻名
        
        Args:
            yao: 爻對象
            actual_yao: 實際的爻對象（用於判斷陰陽）
        
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
        
        position_name = position_names.get(yao.position, str(yao.position))
        
        # 根據陰陽決定數字：陽爻用九，陰爻用六
        if actual_yao.is_yang():
            number = "九"
        else:
            number = "六"
        
        return f"{position_name}{number}"
