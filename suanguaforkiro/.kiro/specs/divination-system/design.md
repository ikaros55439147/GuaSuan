# 設計文件

## 概述

本卜卦系統是一個命令列應用程式，實現傳統易經六十四卦的數位化卜卦功能。系統採用模組化設計，將卦象生成、資料管理、解釋呈現和歷史記錄等功能分離，確保代碼的可維護性和可擴展性。

核心設計理念：
- 使用物件導向設計來表示卦象和爻的概念
- 採用資料驅動的方式管理六十四卦的資訊
- 提供清晰的命令列介面供使用者互動
- 支援本地檔案系統進行歷史記錄的持久化

## 架構

系統採用分層架構設計：

```
┌─────────────────────────────────────┐
│      使用者介面層 (CLI)              │
│  - 命令列互動                        │
│  - 結果顯示格式化                    │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      業務邏輯層                      │
│  - 卜卦服務 (DivinationService)     │
│  - 卦象生成器 (HexagramGenerator)   │
│  - 卦象解釋器 (HexagramInterpreter) │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      資料層                          │
│  - 卦象資料庫 (HexagramDatabase)    │
│  - 歷史記錄管理 (HistoryManager)    │
└─────────────────────────────────────┘
```

### 技術選型

- **程式語言**: Python 3.8+
  - 理由：易於開發、豐富的標準庫、良好的中文支援
- **資料儲存**: JSON 檔案
  - 卦象資料：靜態 JSON 檔案
  - 歷史記錄：JSON 檔案（可擴展為 SQLite）
- **介面**: 命令列介面 (CLI)
  - 使用 Python 內建的 input/print
  - 可選：使用 rich 或 colorama 增強視覺效果

## 元件和介面

### 1. 核心資料模型

#### Yao (爻)
```python
class Yao:
    """代表一個爻"""
    type: YaoType  # 老陰、少陰、老陽、少陽
    is_changing: bool  # 是否為變爻
    position: int  # 位置 (1-6，從下到上)
    
    def to_symbol(self) -> str:
        """返回爻的符號表示 (⚋ 或 ⚊)"""
    
    def get_changed(self) -> 'Yao':
        """如果是變爻，返回變化後的爻"""
```

#### Hexagram (卦)
```python
class Hexagram:
    """代表一個完整的卦象"""
    yaos: List[Yao]  # 六個爻，從下到上
    name: str  # 卦名
    number: int  # 卦序 (1-64)
    upper_trigram: str  # 上卦
    lower_trigram: str  # 下卦
    description: str  # 卦辭
    yao_texts: List[str]  # 六個爻辭
    
    def get_changing_yaos(self) -> List[Yao]:
        """獲取所有變爻"""
    
    def get_changed_hexagram(self) -> Optional['Hexagram']:
        """如果有變爻，生成之卦"""
    
    def to_binary(self) -> str:
        """返回二進制表示 (例如: "111000")"""
```

### 2. 卦象生成器

#### HexagramGenerator
```python
class HexagramGenerator:
    """負責生成卦象"""
    
    def generate_yao(self) -> Yao:
        """
        生成一個爻
        使用三枚銅錢法的模擬：
        - 生成三個隨機數 (2或3)
        - 總和決定爻的類型：
          6 = 老陰 (變)
          7 = 少陽
          8 = 少陰
          9 = 老陽 (變)
        """
    
    def generate_hexagram(self) -> List[Yao]:
        """生成完整的六爻"""
```

### 3. 卦象資料庫

#### HexagramDatabase
```python
class HexagramDatabase:
    """管理六十四卦的資料"""
    
    def __init__(self, data_file: str):
        """從 JSON 檔案載入卦象資料"""
    
    def get_by_binary(self, binary: str) -> HexagramData:
        """根據二進制編碼查找卦象"""
    
    def get_by_number(self, number: int) -> HexagramData:
        """根據卦序查找卦象"""
    
    def get_by_name(self, name: str) -> HexagramData:
        """根據卦名查找卦象"""
```

#### 資料結構 (JSON)
```json
{
  "hexagrams": [
    {
      "number": 1,
      "name": "乾",
      "binary": "111111",
      "upper_trigram": "乾",
      "lower_trigram": "乾",
      "description": "乾：元亨利貞。",
      "interpretation": "乾卦象徵天，代表剛健、創造...",
      "yao_texts": [
        "初九：潛龍勿用。",
        "九二：見龍在田，利見大人。",
        "九三：君子終日乾乾，夕惕若厲，無咎。",
        "九四：或躍在淵，無咎。",
        "九五：飛龍在天，利見大人。",
        "上九：亢龍有悔。"
      ]
    }
  ]
}
```

### 4. 卜卦服務

#### DivinationService
```python
class DivinationService:
    """核心卜卦服務"""
    
    def __init__(self, database: HexagramDatabase, 
                 history_manager: HistoryManager):
        self.generator = HexagramGenerator()
        self.database = database
        self.history = history_manager
    
    def perform_divination(self, question: str) -> DivinationResult:
        """
        執行完整的卜卦流程：
        1. 生成六個爻
        2. 查找對應的卦象資料
        3. 如有變爻，生成之卦
        4. 組合結果
        5. 儲存歷史記錄
        """
    
    def interpret_result(self, result: DivinationResult) -> str:
        """格式化卜卦結果為可讀文字"""
```

#### DivinationResult
```python
@dataclass
class DivinationResult:
    """卜卦結果"""
    question: str
    timestamp: datetime
    original_hexagram: Hexagram
    changing_yaos: List[Yao]
    changed_hexagram: Optional[Hexagram]
    
    def has_changes(self) -> bool:
        """是否有變爻"""
```

### 5. 歷史記錄管理

#### HistoryManager
```python
class HistoryManager:
    """管理卜卦歷史記錄"""
    
    def __init__(self, storage_file: str):
        """初始化，指定儲存檔案路徑"""
    
    def save_record(self, result: DivinationResult) -> None:
        """儲存一筆卜卦記錄"""
    
    def get_all_records(self) -> List[DivinationRecord]:
        """獲取所有歷史記錄"""
    
    def get_record_by_id(self, record_id: str) -> DivinationRecord:
        """根據 ID 獲取特定記錄"""
    
    def search_records(self, keyword: str) -> List[DivinationRecord]:
        """搜尋包含關鍵字的記錄"""
```

### 6. 命令列介面

#### CLI
```python
class DivinationCLI:
    """命令列介面"""
    
    def __init__(self, service: DivinationService):
        self.service = service
    
    def run(self) -> None:
        """主程式迴圈"""
    
    def show_welcome(self) -> None:
        """顯示歡迎訊息"""
    
    def show_menu(self) -> None:
        """顯示主選單"""
    
    def perform_divination_flow(self) -> None:
        """執行卜卦流程"""
    
    def show_history_flow(self) -> None:
        """顯示歷史記錄流程"""
    
    def display_hexagram(self, hexagram: Hexagram) -> None:
        """視覺化顯示卦象"""
    
    def display_result(self, result: DivinationResult) -> None:
        """顯示完整的卜卦結果"""
```

## 資料模型

### 八卦（三爻）對照表

| 卦名 | 符號 | 二進制 | 屬性 |
|------|------|--------|------|
| 乾 ☰ | ≡ | 111 | 天 |
| 兌 ☱ | ≡ | 110 | 澤 |
| 離 ☲ | ≡ | 101 | 火 |
| 震 ☳ | ≡ | 100 | 雷 |
| 巽 ☴ | ≡ | 011 | 風 |
| 坎 ☵ | ≡ | 010 | 水 |
| 艮 ☶ | ≡ | 001 | 山 |
| 坤 ☷ | ≡ | 000 | 地 |

### 爻的類型與生成機率

使用三枚銅錢法：
- 每枚銅錢：正面(3) 或 反面(2)
- 三枚總和：6, 7, 8, 9

| 總和 | 爻類型 | 符號 | 是否變爻 | 機率 |
|------|--------|------|----------|------|
| 6 | 老陰 | ⚋ → ⚊ | 是 | 1/8 |
| 7 | 少陽 | ⚊ | 否 | 3/8 |
| 8 | 少陰 | ⚋ | 否 | 3/8 |
| 9 | 老陽 | ⚊ → ⚋ | 是 | 1/8 |

## 錯誤處理

### 錯誤類型

1. **資料載入錯誤**
   - 卦象資料檔案不存在或格式錯誤
   - 處理：顯示錯誤訊息，提供預設資料或終止程式

2. **歷史記錄錯誤**
   - 無法寫入歷史記錄檔案
   - 處理：警告使用者但繼續執行，不影響卜卦功能

3. **輸入驗證錯誤**
   - 使用者輸入無效的選項
   - 處理：顯示錯誤提示，重新要求輸入

4. **卦象查找錯誤**
   - 根據二進制編碼找不到對應的卦
   - 處理：記錄錯誤，顯示通用錯誤訊息

### 錯誤處理策略

```python
class DivinationError(Exception):
    """卜卦系統基礎異常"""
    pass

class DataLoadError(DivinationError):
    """資料載入異常"""
    pass

class HexagramNotFoundError(DivinationError):
    """卦象未找到異常"""
    pass

# 使用範例
try:
    database = HexagramDatabase("hexagrams.json")
except DataLoadError as e:
    print(f"錯誤：無法載入卦象資料 - {e}")
    sys.exit(1)
```

## 測試策略

### 單元測試

1. **HexagramGenerator 測試**
   - 測試生成的爻類型分佈是否符合機率
   - 測試生成六爻的完整性
   - 測試變爻的正確標記

2. **HexagramDatabase 測試**
   - 測試根據不同條件查找卦象
   - 測試資料完整性（確保有 64 卦）
   - 測試二進制編碼的正確性

3. **Hexagram 模型測試**
   - 測試變爻識別
   - 測試之卦生成
   - 測試二進制轉換

4. **HistoryManager 測試**
   - 測試記錄的儲存和讀取
   - 測試搜尋功能
   - 測試檔案不存在時的處理

### 整合測試

1. **完整卜卦流程測試**
   - 模擬使用者輸入問題
   - 驗證生成的結果包含所有必要資訊
   - 驗證歷史記錄正確儲存

2. **變爻場景測試**
   - 測試有變爻時的完整流程
   - 驗證之卦的正確生成和顯示

### 測試資料

- 準備簡化版的卦象資料（包含 2-3 個卦）用於測試
- 使用固定的隨機種子確保測試可重現
- 準備各種邊界情況的測試案例

## 視覺化設計

### 卦象顯示範例

```
════════════════════════════════════════
           本卦：乾為天
════════════════════════════════════════

上卦：乾 ☰ (天)
下卦：乾 ☰ (天)

    上九  ━━━━━━  (老陽，變爻)
    九五  ━━━━━━
    九四  ━━━━━━
    九三  ━━━━━━
    九二  ━━━━━━
    初九  ━━━━━━

卦辭：乾：元亨利貞。

變爻：上九
爻辭：亢龍有悔。

════════════════════════════════════════
           之卦：天風姤
════════════════════════════════════════

上卦：乾 ☰ (天)
下卦：巽 ☴ (風)

    上九  ━━━━━━
    九五  ━━━━━━
    九四  ━━━━━━
    九三  ━━━━━━
    九二  ━━━━━━
    初六  ━━  ━━

卦辭：姤：女壯，勿用取女。

════════════════════════════════════════
```

### 選單設計

```
╔════════════════════════════════════════╗
║        易經卜卦系統 v1.0               ║
╚════════════════════════════════════════╝

請選擇功能：

  1. 開始卜卦
  2. 查看歷史記錄
  3. 關於本程式
  4. 退出

請輸入選項 (1-4)：
```

## 擴展性考量

### 未來可能的擴展

1. **多種卜卦方法**
   - 目前：三枚銅錢法
   - 可擴展：蓍草法、梅花易數、時間起卦等

2. **更豐富的解釋**
   - 加入卦象的詳細解釋
   - 提供不同流派的解讀
   - 加入現代應用建議

3. **圖形介面**
   - 開發 GUI 版本（使用 Tkinter 或 PyQt）
   - Web 版本（使用 Flask/Django）

4. **資料庫升級**
   - 從 JSON 遷移到 SQLite
   - 支援更複雜的查詢和統計

5. **多語言支援**
   - 提供簡體中文、英文版本
   - 國際化 (i18n) 支援

### 設計模式應用

- **工廠模式**：用於創建不同類型的卦象生成器
- **策略模式**：用於不同的卜卦方法
- **單例模式**：用於資料庫連接管理
- **觀察者模式**：用於歷史記錄的事件通知
