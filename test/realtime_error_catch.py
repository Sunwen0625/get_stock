import twstock

tickers = ['0050', '0052', '00561', '006208', '00679B', '00687B', '00690']

for stock in tickers:
    try:
        info = twstock.realtime.get(stock)      # 嘗試抓即時資料
        if not info['success']:                 # API 回傳 success=False 也算查無
            print(f'{stock}: 查無即時資料，跳過')
            continue
        print(f'{stock}:', info)                # 正常就印出來或做後續處理
    except KeyError as e:
        if e.args and e.args[0] == 'tlong':     # 專門攔 KeyError: 'tlong'
            print(f'{stock}: 找不到 tlong，跳過')
            continue
        else:
            raise                               # 其他 KeyError 交給上層
    except Exception as e:
        # 這裡可以視需要攔其他可能的例外
        print(f'{stock}: 其他錯誤 {e}，跳過')
