# 📈 股票資料更新腳本

本專案提供一套完整流程來處理 **台股個股與 ETF 的資料更新與分類**，依據 Excel 表格內的代碼，自動判斷是否為 ETF，並更新歷史指標與即時資訊。

---

## ✅ 功能說明

1. **讀取設定檔與 Excel**
   - 從 `setting.json` 讀取資料來源、目標工作表與股票代碼。
   - 從 `read_file` 對應的 Excel 檔案中擷取代碼欄（從 B2 開始，含 B2）。

2. **更新歷史財報與評估指標**
   - 使用 [HiStock](https://histock.tw/)、Yahoo Finance 等資料來源。
   - 根據個股 / ETF 自動抓取不同指標：
     - 個股：市盈率、市淨率、ROE、EPS、殖利率、流動比率等
     - ETF：管理費、現金股利、除息日、殖利率等

3. **即時資料更新與分類**
   - 執行收盤後的即時資料抓取。
   - 使用 `RealtimeMarket.run()` 對代碼進行分類更新。

4. **結果寫入 Excel**
   - 寫入 `write_file` 指定的檔案與工作表。
   - 自動儲存、欄位自動寬度調整。

---

## 🧩 依賴模組

- Python >= 3.11
- twstock
- pandas
- xlwings
- requests
- beautifulsoup4
- lxml
- openpyxl

> 建議使用 Poetry 管理套件與環境。

安裝方式：

```bash
pip install poetry
````

然後執行 `run.bat`，會自動安裝所需模組並執行更新流程。

---

## ⚙️ 設定檔格式（setting.json）

```jsonc
{
  "read_file": "原始資料.xlsx",        // 要讀取代碼的來源檔案
  "read_sheet": "原始資料.xlsx",              // 資料代碼所在的工作表

  "write_file": "結果輸出.xlsx",       // 寫入資料的目標檔案
  "write_sheet": "結果輸出.xlsx",           // 寫入目標的工作表

  "code": {
    "0050": true,     // ETF → true
    "2308": false     // 個股 → false
    // 可用 stock_cache.update_code_section() 自動補齊此區塊
  },

  "save": true,        // 是否在最後備份 read_file
  "ending_wait": true  // 流程結束時是否等待使用者按鍵
}
```

---

## 🖥️ 使用方式

```bash
python run.bat
```

執行流程：

1. 讀取 `setting.json` 與來源 Excel。
2. 若 `code` 區塊缺少對應代碼，會自動補齊（並更新 `setting.json`）。
3. 抓取歷史指標並寫入目標 Excel。
4. 抓取即時報價，進行分類整理。
5. 若設定中 `save: true`，會自動備份原始 Excel。
6. 若設定中 `ending_wait: true`，流程結束後會停等按鍵再關閉。

---

## 📌 版本特性

* ✅ 支援個股與 ETF 自動辨識（內建 Yahoo API 判斷）
* ⚡ 多執行緒加速資料抓取流程
* 📂 使用 `ExcelSession` 封裝 Excel 操作，自動開啟 / 儲存 / 關閉




