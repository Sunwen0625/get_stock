import twstock
import time
import logging
from datetime import date
from typing import List


from .excel_utils import ExcelSession

_BLANK = "-"                     # 全程使用同一個佔位符，方便改動

_REALTIME_KEYS = [               # 可能用到的即時欄位 (可依實際需求增減)
    "best_bid_price", "best_ask_price", "best_bid_volume", "best_ask_volume",
    "latest_trade_price", "trade_volume", "accumulate_trade_volume",
    "high", "low", "open"
]

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
    )
logger = logging.getLogger(__name__)

class RealtimeStockData:
    
    """單檔個股即時資料處理 (Null-Object Pattern)."""
    # ========== 1. 建立物件：正常 or 空白 ==========
    @classmethod
    def from_code(cls, code: str, row: int, retry: int = 3, retry_interval: float = 5.0):
        """
        抓即時資料並回傳 RealtimeStockData 物件。
        失敗時最多重試 retry 次，每次間隔 retry_interval 秒。
        失敗時 data 會是「全欄位 _BLANK」，屬性 blank=True。
        """
        last_err = None
        for attempt in range(1, retry + 1):
            try:
                data = twstock.realtime.get(code)
                if not data.get("success"):
                    raise ValueError("success=False")  # API 回傳 success=False
                obj = cls(data, row)
                obj.blank = False
                return obj
            except Exception as err: # 含 KeyError('tlong')、timeout…
                last_err = err
                logger.warning(f"{code}: 第{attempt}次抓取失敗（{err}）")
                if attempt < retry:
                    time.sleep(retry_interval)
        
        logger.error(f"{code}: 重試{retry}次皆失敗，將以空白填入（最後錯誤：{last_err}）")
        # 最後都失敗才回傳空白資料
        logger.error(f"{code}: 重試{retry}次皆失敗，將以空白填入")
        data = cls._make_blank_payload(code) # 產生全是 "-"
        obj = cls(data, row)
        obj.blank = True # 標註是否為空白資料
        return obj


    # ========== 2. 產生空白 payload ==========
    @staticmethod
    def _make_blank_payload(code: str) -> dict:
        today = date.today().isoformat()
        return {
            "success": False,
            "info":  {"code": code, "name": _BLANK, "time": f"{today} 00:00:00"},
            "realtime": {k: _BLANK for k in _REALTIME_KEYS},
        }
    # ========= 盤中批次工具 ========= #
    @staticmethod
    def update_realtime_data(
        codes: List[str],
        session: ExcelSession,
        row_map: dict[str, int] | None = None
        ) -> List[str]:
        """
        盤中批次抓即時資料並寫入 Excel。
        - codes: 股票代碼清單，順序與 row_map 對應。
        - session: ExcelSession
        - row_map: {代碼: 寫入行號}，若為 None 則自動用 enumerate(row=2)
        失敗的股票代碼會被收集後回傳，方便呼叫端做告警或重試。
        """
        failed: List[str] = []

        for idx, code in enumerate(codes):
            if row_map is not None:
                row = row_map[code] #dict 格式 裡面有code的話就回傳對應的row
            else:
                row = idx + 2  #list 格式 +2用來對應excel的位置 idx 從0開始 1是標題 所以+2
            try:
                stock = RealtimeStockData.from_code(code, row)
                stock.input_data(session.sh)
                if stock.blank:
                    failed.append(code)
            except Exception as exc:
                logger.warning("處理 %s 發生錯誤：%s", code, exc, exc_info=True)
                failed.append(code)
        return failed
    
    @staticmethod
    def _blank_or_value(blank, value, fallback="-"):
        return fallback if blank or value == "-" else value

    """單檔個股即時資料處理。"""
    def __init__(self, code_data:dict , row:int,*, blank: bool = False) -> None:
        self.code_data  = code_data
        self.row = row
        self.blank = blank   
    # ---------- twstock 字典拆裝 ---------- #
    #獲得info裡面個別資料
    def _info(self) -> dict:     return self.code_data["info"]

    #獲得realtime裡面個別資料
    def _rt(self) -> dict:       return self.code_data["realtime"]
    
    #獲得時間
    def date(self) -> str:
        #回傳格式  ('2023-06-14', '14:30:00')
        return self._info()["time"].split(" ")[0]
    
    #獲得代號
    def code(self) -> str:       return self._info()["code"]
    
    #獲得名稱
    def name(self) -> str:       return self._info()["name"]
    
    # ---------- 即時欄位 ---------- #
    
    #成交價
    def _latest_trade_price(self, sheet):
        return self._blank_or_value(self.blank, self._rt()["latest_trade_price"])
    
    #昨收
    def _close_price(self, sheet):
        return sheet.range(f"P{self.row}").value
    
    #漲跌
    def _amplitude(self, sheet):
        latest = self._latest_trade_price(sheet)
        close = self._close_price(sheet)
        try:
            latest_f = float(latest)
            close_f = float(close)
            return round(latest_f - close_f, 2)
        except (TypeError, ValueError):
            return "-"
    
    # 漲跌%
    def _amplitude_pct(self, sheet):
        amplitude = self._amplitude(sheet)
        close = self._close_price(sheet)
        try:
            amplitude_f = float(amplitude)
            close_f = float(close)
            if close_f == 0:
                return "-"
            return round(amplitude_f / close_f * 100, 2)
        except (TypeError, ValueError):
            return "-"
    
    #成交量
    def _trade_volume(self, sheet):
        return self._blank_or_value(self.blank, self._rt()["trade_volume"])

        
    # ---------- Excel 操作 ---------- #

    def input_data(self, sheet):
        # 修改数据
        sheet.range(f"A{self.row}").api.NumberFormat = "yyyy/mm/dd" 
        sheet.range(f"A{self.row}").value = self.date()

        data = [
            self.name(),
            self._rt()["best_bid_price"][0],
            self._rt()["best_ask_price"][0],
            self._latest_trade_price(sheet),
            self._amplitude(sheet),
            self._amplitude_pct(sheet),
            self._trade_volume(sheet),
            self._rt()["best_bid_volume"][0],
            self._rt()["best_ask_volume"][0],
            self._rt()["accumulate_trade_volume"],
            self._rt()["high"],
            self._rt()["low"],
            self._rt()["open"],
        ]
        #設置c到o
        sheet.range(f"C{self.row}:O{self.row}").value = data
        sheet.autofit()
        

    
# --------------------------------------------------



if __name__ == "__main__":
    CODES = ["1232", "2105", "2308"]

    with ExcelSession("data.xlsx", sheet_name="new title") as xls:
        while True:
            #RealtimeStockData.update_realtime_data(CODES, xls)
            time.sleep(3)
    
