# 📖 HƯỚNG DẪN KỸ THUẬT - STOCK SCREENER

## Tài liệu chi tiết về cách hoạt động và các thông số có thể chỉnh sửa

---

## 📁 MỤC LỤC

1. [Kiến trúc tổng quan](#1-kiến-trúc-tổng-quan)
2. [Các thông số có thể chỉnh sửa](#2-các-thông-số-có-thể-chỉnh-sửa)
3. [Giải thích các chỉ báo kỹ thuật](#3-giải-thích-các-chỉ-báo-kỹ-thuật)
4. [Giải thích các chỉ số cơ bản](#4-giải-thích-các-chỉ-số-cơ-bản)
5. [Hệ thống chấm điểm](#5-hệ-thống-chấm-điểm)
6. [Luồng xử lý dữ liệu](#6-luồng-xử-lý-dữ-liệu)
7. [Hướng dẫn nâng cấp](#7-hướng-dẫn-nâng-cấp)

---

## 1. KIẾN TRÚC TỔNG QUAN

### 1.1 Sơ đồ hoạt động

```
┌─────────────────────────────────────────────────────────────────┐
│                         STOCK SCREENER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  LẤY DANH    │───▶│  LẤY DỮ LIỆU │───▶│  TÍNH CHỈ    │       │
│  │  SÁCH MÃ     │    │  TỪNG MÃ     │    │  BÁO         │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ • HOSE       │    │ • Giá OHLCV  │    │ • RSI        │       │
│  │ • HNX        │    │ • Volume     │    │ • MACD       │       │
│  │ • UPCOM      │    │ • P/E, ROE   │    │ • Breakout   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │  LỌC THEO    │───▶│  CHẤM ĐIỂM   │───▶│  XUẤT KẾT    │       │
│  │  TIÊU CHÍ    │    │  0-100       │    │  QUẢ         │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │ • Swing      │    │ >= 50 điểm   │    │ • Console    │       │
│  │ • Dài hạn    │    │ = ĐẠT        │    │ • CSV file   │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Các file trong project

| File                     | Chức năng                         |
| ------------------------ | --------------------------------- |
| `stock_screener.py`      | Script chính - chứa toàn bộ logic |
| `requirements.txt`       | Danh sách thư viện cần cài        |
| `README.md`              | Hướng dẫn sử dụng cơ bản          |
| `HUONG_DAN_KY_THUAT.md`  | Tài liệu kỹ thuật (file này)      |
| `screener_results_*.csv` | File kết quả xuất ra              |

---

## 2. CÁC THÔNG SỐ CÓ THỂ CHỈNH SỬA

### 2.1 Tiêu chí Swing Trading (Dòng 24-32)

```python
SWING_CRITERIA = {
    'volume_ratio_min': 1.5,      # [1] Volume đột biến
    'rsi_oversold': 30,            # [2] Ngưỡng quá bán
    'rsi_overbought': 70,          # [3] Ngưỡng quá mua
    'risk_reward_min': 2.0,        # [4] Tỷ lệ Risk/Reward
    'max_stop_loss_pct': 7,        # [5] Stop-loss tối đa
    'min_price': 5000,             # [6] Giá tối thiểu
    'min_avg_volume': 100000,      # [7] Khối lượng tối thiểu
}
```

#### Chi tiết từng thông số:

| #   | Thông số            | Giá trị mặc định | Ý nghĩa                           | Gợi ý chỉnh                             |
| --- | ------------------- | ---------------- | --------------------------------- | --------------------------------------- |
| 1   | `volume_ratio_min`  | 1.5              | Volume hôm nay >= 150% TB 20 ngày | Tăng lên 2.0 nếu muốn tín hiệu mạnh hơn |
| 2   | `rsi_oversold`      | 30               | RSI < 30 = quá bán                | Giảm xuống 25 nếu muốn strict hơn       |
| 3   | `rsi_overbought`    | 70               | RSI > 70 = quá mua                | Tăng lên 75 nếu muốn bắt trend mạnh     |
| 4   | `risk_reward_min`   | 2.0              | Lãi tiềm năng / Lỗ >= 2           | Tăng lên 3.0 nếu muốn an toàn hơn       |
| 5   | `max_stop_loss_pct` | 7                | Stop-loss không quá 7%            | Giảm xuống 5 nếu muốn ít rủi ro         |
| 6   | `min_price`         | 5000             | Loại penny stock < 5,000đ         | Tăng lên 10000 để lọc mã lớn hơn        |
| 7   | `min_avg_volume`    | 100000           | Thanh khoản tối thiểu             | Tăng lên 500000 cho mã thanh khoản cao  |

### 2.2 Tiêu chí Đầu tư Dài hạn (Dòng 35-42)

```python
LONGTERM_CRITERIA = {
    'pe_max': 25,                  # [1] P/E tối đa
    'roe_min': 15,                 # [2] ROE tối thiểu
    'eps_growth_min': 10,          # [3] Tăng trưởng EPS
    'debt_to_equity_max': 1.5,     # [4] Đòn bẩy tối đa
    'dividend_yield_min': 0,       # [5] Cổ tức tối thiểu
    'market_cap_min': 1000,        # [6] Vốn hóa tối thiểu
}
```

#### Chi tiết từng thông số:

| #   | Thông số             | Giá trị mặc định | Ý nghĩa               | Gợi ý chỉnh                       |
| --- | -------------------- | ---------------- | --------------------- | --------------------------------- |
| 1   | `pe_max`             | 25               | P/E <= 25 là hợp lý   | Giảm xuống 15 cho value investing |
| 2   | `roe_min`            | 15               | ROE >= 15% là tốt     | Tăng lên 20 cho blue-chip         |
| 3   | `eps_growth_min`     | 10               | EPS tăng >= 10%/năm   | Tăng lên 20 cho growth stock      |
| 4   | `debt_to_equity_max` | 1.5              | Nợ/Vốn <= 1.5         | Giảm xuống 1.0 cho an toàn        |
| 5   | `dividend_yield_min` | 0                | Không bắt buộc cổ tức | Tăng lên 3 cho income investing   |
| 6   | `market_cap_min`     | 1000             | Vốn hóa >= 1,000 tỷ   | Tăng lên 5000 cho large-cap       |

### 2.3 Các thông số khác

#### Số ngày lấy dữ liệu (Dòng ~510)

```python
def get_stock_data(symbol, days=100):  # Mặc định 100 ngày
```

- **Tăng lên 200**: Phân tích trend dài hạn hơn
- **Giảm xuống 50**: Chạy nhanh hơn, focus ngắn hạn

#### Chu kỳ RSI (Dòng ~175)

```python
def calculate_rsi(prices, period=14):  # Mặc định 14 ngày
```

- **Tăng lên 21**: RSI ổn định hơn, ít tín hiệu hơn
- **Giảm xuống 7**: RSI nhạy hơn, nhiều tín hiệu hơn

#### Chu kỳ Breakout (Dòng ~210)

```python
def detect_breakout(df, period=20):  # Mặc định 20 ngày
```

- **Tăng lên 50**: Breakout khỏi range 50 ngày (mạnh hơn)
- **Giảm xuống 10**: Breakout ngắn hạn (nhạy hơn)

#### Điểm đạt ngưỡng (Dòng ~350, ~480)

```python
if score >= 50:  # Ngưỡng đạt
    return {...}
```

- **Tăng lên 70**: Chỉ lấy mã rất tốt
- **Giảm xuống 40**: Lấy nhiều mã hơn

---

## 3. GIẢI THÍCH CÁC CHỈ BÁO KỸ THUẬT

### 3.1 RSI (Relative Strength Index)

```
Công thức:
RSI = 100 - (100 / (1 + RS))

Trong đó:
RS = Trung bình tăng 14 ngày / Trung bình giảm 14 ngày
```

**Cách đọc:**
| Giá trị RSI | Ý nghĩa | Hành động |
|-------------|---------|-----------|
| < 30 | Quá bán | Xem xét MUA |
| 30-50 | Bearish | Chờ đợi |
| 50-70 | Bullish | Giữ/Mua |
| > 70 | Quá mua | Xem xét BÁN |

### 3.2 MACD (Moving Average Convergence Divergence)

```
Công thức:
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(MACD, 9)
Histogram = MACD Line - Signal Line
```

**Tín hiệu:**

- MACD cắt lên Signal → Bullish (Mua)
- MACD cắt xuống Signal → Bearish (Bán)
- Histogram dương và tăng → Momentum tăng

### 3.3 Volume Ratio

```
Volume Ratio = Volume hôm nay / Trung bình Volume 20 ngày
```

**Ý nghĩa:**
| Tỷ lệ | Ý nghĩa |
|-------|---------|
| < 0.5 | Rất thấp, ít quan tâm |
| 0.5-1.0 | Bình thường |
| 1.0-1.5 | Cao hơn bình thường |
| 1.5-2.0 | Đột biến, có tin tức |
| > 2.0 | Rất đột biến, cần chú ý |

### 3.4 Breakout Detection

```
Breakout UP = Giá đóng cửa hôm nay > Đỉnh cao nhất 20 ngày trước
Breakout DOWN = Giá đóng cửa hôm nay < Đáy thấp nhất 20 ngày trước
```

**Điều kiện breakout mạnh:**

1. Volume >= 1.5x TB
2. Giá đóng cửa gần đỉnh ngày (>80% biên độ)
3. RSI chưa quá mua (<70)

### 3.5 Support & Resistance

```
Resistance (Kháng cự) = Đỉnh cao nhất 20 ngày
Support (Hỗ trợ) = Đáy thấp nhất 20 ngày
```

**Cách tính Stop-loss và Target:**

```
Stop-loss = Support × 0.98  (Dưới hỗ trợ 2%)
Target 1 = Resistance       (Vùng kháng cự)
Target 2 = Giá hiện tại × 1.15  (Tăng 15%)
```

---

## 4. GIẢI THÍCH CÁC CHỈ SỐ CƠ BẢN

### 4.1 P/E (Price to Earnings)

```
P/E = Giá cổ phiếu / Lợi nhuận trên mỗi cổ phiếu (EPS)
```

| P/E   | Đánh giá                |
| ----- | ----------------------- |
| < 10  | Rất rẻ (hoặc có vấn đề) |
| 10-15 | Hấp dẫn                 |
| 15-25 | Hợp lý                  |
| 25-40 | Đắt                     |
| > 40  | Rất đắt (growth stock)  |

### 4.2 ROE (Return on Equity)

```
ROE = Lợi nhuận ròng / Vốn chủ sở hữu × 100%
```

| ROE    | Đánh giá   |
| ------ | ---------- |
| < 10%  | Kém        |
| 10-15% | Trung bình |
| 15-20% | Tốt        |
| 20-30% | Rất tốt    |
| > 30%  | Xuất sắc   |

### 4.3 EPS Growth (Tăng trưởng lợi nhuận)

```
EPS Growth = (EPS năm nay - EPS năm trước) / EPS năm trước × 100%
```

| Growth | Đánh giá            |
| ------ | ------------------- |
| < 0%   | Âm, đang giảm       |
| 0-10%  | Tăng trưởng thấp    |
| 10-20% | Tăng trưởng tốt     |
| 20-50% | Tăng trưởng cao     |
| > 50%  | Tăng trưởng rất cao |

### 4.4 Debt/Equity (Đòn bẩy tài chính)

```
D/E = Tổng nợ / Vốn chủ sở hữu
```

| D/E     | Đánh giá       |
| ------- | -------------- |
| < 0.5   | Rất an toàn    |
| 0.5-1.0 | An toàn        |
| 1.0-1.5 | Chấp nhận được |
| 1.5-2.0 | Rủi ro         |
| > 2.0   | Rủi ro cao     |

---

## 5. HỆ THỐNG CHẤM ĐIỂM

### 5.1 Swing Trading (Tổng 100 điểm)

| Tiêu chí        | Điểm | Điều kiện           |
| --------------- | ---- | ------------------- |
| Volume đột biến | +25  | Volume >= 1.5x TB20 |
| RSI trung tính  | +20  | 30 < RSI < 70       |
| RSI quá bán     | +15  | RSI <= 30           |
| Breakout UP     | +30  | Vượt đỉnh 20 ngày   |
| Giá trên MA20   | +15  | Close > SMA(20)     |
| MA20 > MA50     | +10  | Uptrend             |
| R/R >= 2        | +15  | Risk/Reward tốt     |
| Stop-loss > 7%  | -20  | Phạt nếu rủi ro cao |

**Ngưỡng đạt: >= 50 điểm**

### 5.2 Đầu tư Dài hạn (Tổng 100 điểm)

| Tiêu chí        | Điểm | Điều kiện             |
| --------------- | ---- | --------------------- |
| P/E hợp lý      | +20  | P/E <= 25             |
| ROE cao         | +25  | ROE >= 15%            |
| EPS tăng trưởng | +25  | EPS Growth >= 10%     |
| D/E an toàn     | +15  | D/E <= 1.5            |
| Có cổ tức       | +10  | Dividend > 0          |
| Vốn hóa lớn     | +5   | Market Cap >= 1000 tỷ |

**Ngưỡng đạt: >= 50 điểm**

---

## 6. LUỒNG XỬ LÝ DỮ LIỆU

### 6.1 Sơ đồ chi tiết

```
[BẮT ĐẦU]
     │
     ▼
┌────────────────────────────────────────┐
│ 1. get_all_stock_symbols()             │
│    ├── Thử vnstock3 API               │
│    ├── Thử TCBS API                   │
│    └── Fallback: danh sách cứng 244 mã │
│    Kết quả: List[str] symbols          │
└────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────┐
│ 2. FOR symbol IN symbols:              │
│    │                                   │
│    ├── get_stock_data(symbol)          │
│    │   └── DataFrame: OHLCV 100 ngày   │
│    │                                   │
│    ├── get_fundamental_data(symbol)    │
│    │   └── Dict: PE, ROE, EPS...       │
│    │                                   │
│    ├── screen_swing_trading()          │
│    │   ├── Tính RSI, Volume Ratio      │
│    │   ├── Detect Breakout             │
│    │   ├── Tính Support/Resistance     │
│    │   ├── Chấm điểm 0-100            │
│    │   └── Return result nếu >= 50    │
│    │                                   │
│    └── screen_long_term()              │
│        ├── Đọc PE, ROE, EPS, D/E      │
│        ├── Chấm điểm 0-100            │
│        └── Return result nếu >= 50    │
└────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────┐
│ 3. Tổng hợp kết quả                    │
│    ├── swing_results.sort(by=score)    │
│    └── longterm_results.sort(by=score) │
└────────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────────┐
│ 4. Xuất kết quả                        │
│    ├── print_swing_results() → Console │
│    ├── print_longterm_results()        │
│    └── export_to_csv() → File CSV      │
└────────────────────────────────────────┘
     │
     ▼
[KẾT THÚC]
```

### 6.2 Cấu trúc dữ liệu

#### DataFrame giá (OHLCV)

```
| time       | open   | high   | low    | close  | volume   |
|------------|--------|--------|--------|--------|----------|
| 2026-01-01 | 95000  | 96500  | 94000  | 96000  | 1500000  |
| 2026-01-02 | 96000  | 97000  | 95500  | 96500  | 1200000  |
| ...        | ...    | ...    | ...    | ...    | ...      |
```

#### Dict fundamental

```python
{
    'pe': 18.5,
    'roe': 22.3,
    'eps_growth': 15.2,
    'debt_to_equity': 0.8,
    'dividend_yield': 3.5,
    'market_cap': 125000  # tỷ VND
}
```

#### Dict kết quả Swing

```python
{
    'symbol': 'FPT',
    'type': 'SWING',
    'score': 85,
    'price': 95000,
    'volume_ratio': 2.3,
    'rsi': 45.2,
    'support': 88000,
    'resistance': 102000,
    'stop_loss': 86240,
    'stop_loss_pct': 9.2,
    'target_1': 102000,
    'target_2': 109250,
    'risk_reward': 2.8,
    'signals': ['📊 Volume đột biến', '🚀 BREAKOUT'],
    'breakout': True
}
```

---

## 7. HƯỚNG DẪN NÂNG CẤP

### 7.1 Thêm chỉ báo kỹ thuật mới

**Ví dụ: Thêm Stochastic Oscillator**

```python
# Thêm vào phần "HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT"

def calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3):
    """
    Tính Stochastic Oscillator
    %K = (Close - Low14) / (High14 - Low14) × 100
    %D = SMA(%K, 3)
    """
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()

    stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min)
    stoch_k = stoch_k.rolling(window=smooth_k).mean()  # Smooth
    stoch_d = stoch_k.rolling(window=smooth_d).mean()

    return stoch_k, stoch_d
```

**Sử dụng trong screen_swing_trading():**

```python
# Thêm vào hàm screen_swing_trading()
stoch_k, stoch_d = calculate_stochastic(df)
current_stoch_k = stoch_k.iloc[-1]

# Stochastic thoát vùng quá bán
if current_stoch_k > 20 and stoch_k.iloc[-2] <= 20:
    score += 15
    signals.append(f"📈 Stochastic thoát quá bán: {current_stoch_k:.1f}")
```

### 7.2 Thêm nguồn dữ liệu mới

**Ví dụ: Thêm API từ VNDirect**

```python
# Thêm vào hàm get_stock_data_alternative()

def get_stock_data_vndirect(symbol, days=100):
    """Lấy dữ liệu từ VNDirect API"""
    import requests

    url = f"https://finfo-api.vndirect.com.vn/v4/stock_prices"
    params = {
        'code': symbol,
        'size': days,
        'sort': 'date'
    }
    headers = {'User-Agent': 'Mozilla/5.0'}

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()['data']
        df = pd.DataFrame(data)
        # Xử lý và trả về DataFrame
        return df

    return None
```

### 7.3 Thêm bộ lọc ngành

**Ví dụ: Lọc theo ngành**

```python
# Thêm cấu hình ngành
INDUSTRY_FILTER = {
    'include': ['Ngân hàng', 'Công nghệ', 'Bất động sản'],  # Chỉ lọc các ngành này
    'exclude': ['Dầu khí'],  # Loại trừ ngành này
}

# Thêm vào run_screener()
def run_screener(symbols=None, screen_type='ALL', industry_filter=None):
    # ... existing code ...

    if industry_filter:
        # Lọc theo ngành
        filtered_symbols = []
        for symbol in symbols:
            industry = get_stock_industry(symbol)  # Cần viết hàm này
            if industry in industry_filter.get('include', []):
                if industry not in industry_filter.get('exclude', []):
                    filtered_symbols.append(symbol)
        symbols = filtered_symbols
```

### 7.4 Thêm thông báo Telegram

```python
# Thêm vào cuối file

def send_telegram_alert(message, bot_token, chat_id):
    """Gửi thông báo qua Telegram"""
    import requests

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    response = requests.post(url, json=payload)
    return response.status_code == 200


# Sử dụng sau khi có kết quả
if swing_results:
    message = "🚀 *SWING TRADING ALERTS*\n\n"
    for r in swing_results[:5]:
        message += f"• *{r['symbol']}* - Điểm: {r['score']}\n"

    send_telegram_alert(
        message,
        bot_token="YOUR_BOT_TOKEN",
        chat_id="YOUR_CHAT_ID"
    )
```

### 7.5 Chạy tự động hàng ngày

**Sử dụng Task Scheduler (Windows):**

1. Tạo file `run_daily.bat`:

```batch
@echo off
cd /d C:\lhuynh\VN30
C:\lhuynh\VN30\.venv\Scripts\python.exe stock_screener.py
```

2. Mở Task Scheduler → Create Basic Task
3. Đặt lịch chạy lúc 15:30 mỗi ngày (sau khi đóng cửa)

---

## 📝 GHI CHÚ QUAN TRỌNG

### Khi chỉnh sửa tiêu chí:

1. **Backup file gốc** trước khi sửa
2. **Test với dữ liệu demo** trước (chọn option 4)
3. **Ghi chú các thay đổi** để theo dõi

### Các lỗi thường gặp:

| Lỗi                     | Nguyên nhân           | Cách sửa               |
| ----------------------- | --------------------- | ---------------------- |
| `ImportError: vnstock3` | Chưa cài thư viện     | `pip install vnstock3` |
| `Connection timeout`    | Mạng chậm/API quá tải | Thử lại sau            |
| `KeyError`              | Cột dữ liệu thay đổi  | Kiểm tra tên cột API   |
| Kết quả trống           | Tiêu chí quá strict   | Giảm ngưỡng điểm       |

---

## 📞 LIÊN HỆ HỖ TRỢ

Nếu cần hỗ trợ thêm, hãy cung cấp:

1. Lỗi cụ thể (copy toàn bộ error message)
2. Phiên bản Python (`python --version`)
3. Các thay đổi đã thực hiện

---

**Cập nhật lần cuối:** 28/01/2026  
**Version:** 1.0
