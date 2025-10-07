"""自訂異常類別"""


class DivinationError(Exception):
    """卜卦系統基礎異常"""
    pass


class DataLoadError(DivinationError):
    """資料載入異常"""
    pass


class HexagramNotFoundError(DivinationError):
    """卦象未找到異常"""
    pass


class HistoryError(DivinationError):
    """歷史記錄相關異常"""
    pass


class InvalidInputError(DivinationError):
    """無效輸入異常"""
    pass
