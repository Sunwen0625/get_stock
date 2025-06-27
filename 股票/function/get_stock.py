import twstock
import time
import logging
from datetime import datetime
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
    def from_code(cls, code: str, row: int):
        """
        抓即時資料並回傳 RealtimeStockData 物件。
        無論成功與否都回傳物件；失敗時 data 會是「全欄位 _BLANK」，屬性 blank=True。
        """
        try:
            data = twstock.realtime.get(code)
            if not data.get("success"):            # API 回傳 success=False
                raise ValueError("success=False")  # 統一丟進 except 區

        except Exception as err:                   # 含 KeyError('tlong')、timeout…
            print(f"{code}: {err} → 以空白資料填入")
            data = cls._make_blank_payload(code)   # 產生全是 "-"
            blank = True
        else:
            blank = False

        obj = cls(data, row)
        obj.blank = blank                          # 標註是否為空白資料
        return obj

    # ========== 2. 產生空白 payload ==========
    @staticmethod
    def _make_blank_payload(code: str) -> dict:
        today = datetime.date.today().isoformat()
        return {
            "success": False,
            "info":  {"code": code, "name": _BLANK, "time": f"{today} 00:00:00"},
            "realtime": {k: _BLANK for k in _REALTIME_KEYS},
        }
    # ========= 盤中批次工具 ========= #
    @staticmethod
    def update_realtime_data(codes: List[str], session: ExcelSession) -> List[str]:
        """
        盤中批次抓即時資料並寫入 Excel。
        失敗的股票代碼會被收集後回傳，方便呼叫端做告警或重試。
        """
        row = 2                     # Excel 從第 2 列開始寫
        failed: List[str] = []

        for code in codes:
            try:
                stock = RealtimeStockData.from_code(code, row)
                stock.input_data(session.sh)
                if stock.blank:     # API 失敗但已以「-」填入
                    failed.append(code)
            except Exception as exc:
                logger.warning("處理 %s 發生錯誤：%s", code, exc,exc_info=True)
                failed.append(code)
            row += 1

        return failed

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
    #if get_realtime()["latest_trade_price"] != "-" -> 正常資料 else ->儲存格資料
    def _latest_trade_price(self, sheet):
        price = self._rt()["latest_trade_price"]
        return price if price != "-" else sheet.range(f"F{self.row}").value
    
    #昨收
    def _close_price(self, sheet):
        return sheet.range(f"P{self.row}").value
    
    #漲跌
    def _amplitude(self, sheet):
        return float(self._latest_trade_price(sheet)) - float(self._close_price(sheet))
    
    # 漲跌%
    def _amplitude_pct(self, sheet):
        pct = self._amplitude(sheet) / float(self._close_price(sheet)) * 100
        return round(pct, 2)
    
    #成交量
    def _trade_volume(self, sheet):
        vol = self._rt()["trade_volume"]
        return vol if vol != "-" else sheet.range(f"I{self.row}").value
        
    # ---------- Excel 操作 ---------- #

    def input_data(self, sheet):
        # 修改数据
        sheet.range(f"A{self.row}").api.NumberFormat = "yyyy/mm/dd" 
        sheet.range(f"A{self.row}").value = self.date()

        data = [
            self.name(),
            self._rt()["best_bid_price"][-1],
            self._rt()["best_ask_price"][-1],
            self._latest_trade_price(sheet),
            self._amplitude(sheet),
            self._amplitude_pct(sheet),
            self._trade_volume(sheet),
            self._rt()["best_bid_volume"][-1],
            self._rt()["best_ask_volume"][-1],
            self._rt()["accumulate_trade_volume"],
            self._rt()["high"],
            self._rt()["low"],
            self._rt()["open"],
        ]
        #設置c到o
        sheet.range(f"C{self.row}:O{self.row}").value = data
        sheet.autofit()
        

    
# --------------------------------------------------
""" 
#盤中抓即時資料
def update_realtime_data(codes: list[str], session:ExcelSession) -> None:
    "盤中抓即時資料並寫入 Excel。"
    row = 2
    for code in codes:
        RealtimeStockData.from_code(code, row).input_data(session.sh)
        row += 1
"""



if __name__ == "__main__":
    CODES = ["1232", "2105", "2308"]

    with ExcelSession("data.xlsx", sheet_name="new title") as xls:
        while True:
            RealtimeStockData.update_realtime_data(CODES, xls)
            time.sleep(3)
    
