# 🇻🇳 STOCK SCREENER - LỌC MÃ CHỨNG KHOÁN VIỆT NAM

Công cụ tự động lọc mã chứng khoán theo tiêu chí **Swing Trading** và **Đầu tư Dài hạn**.

---

## 📋 Tính năng

### 🎯 Lọc Swing Trading (2-8 tuần)

- Phát hiện **Breakout** vượt đỉnh 20 phiên
- Volume đột biến (>150% TB 20 phiên)
- RSI thoát vùng quá bán (30-70)
- Tính toán **Stop-loss** và **Target**
- Risk/Reward tối thiểu 1:2

### 🏦 Lọc Đầu tư Dài hạn (>6 tháng)

- P/E hợp lý (<25x hoặc < TB ngành)
- ROE > 15%
- Tăng trưởng EPS > 10%/năm
- Đòn bẩy tài chính an toàn (D/E < 1.5)
- Cổ tức (nếu có)

---

## 🚀 Cài đặt

### 1. Cài thư viện

```bash
pip install -r requirements.txt
```

Hoặc cài từng thư viện:

```bash
pip install vnstock3 pandas numpy requests
```

### 2. Chạy script

```bash
python stock_screener.py
```

---

## 📊 Cách sử dụng

### Chạy mặc định (quét VN30 + mã phổ biến)

```python
from stock_screener import run_screener

# Quét tất cả
swing_results, longterm_results = run_screener()

# Chỉ quét Swing
swing_results, _ = run_screener(screen_type='SWING')

# Chỉ quét Dài hạn
_, longterm_results = run_screener(screen_type='LONGTERM')
```

### Quét danh sách mã cụ thể

```python
my_watchlist = ['FPT', 'VNM', 'MWG', 'HPG', 'TCB']
swing_results, longterm_results = run_screener(symbols=my_watchlist)
```

### Xuất kết quả ra CSV

```python
from stock_screener import export_to_csv

export_to_csv(swing_results, longterm_results, 'my_results.csv')
```

---

## ⚙️ Tùy chỉnh tiêu chí

Chỉnh sửa trong file `stock_screener.py`:

### Swing Trading

```python
SWING_CRITERIA = {
    'volume_ratio_min': 1.5,      # Volume > 150% TB 20 phiên
    'rsi_oversold': 30,            # RSI quá bán
    'rsi_overbought': 70,          # RSI quá mua
    'risk_reward_min': 2.0,        # R/R tối thiểu 1:2
    'max_stop_loss_pct': 7,        # Stop-loss max 7%
    'min_price': 5000,             # Giá tối thiểu
    'min_avg_volume': 100000,      # Volume TB tối thiểu
}
```

### Đầu tư Dài hạn

```python
LONGTERM_CRITERIA = {
    'pe_max': 25,                  # P/E tối đa
    'roe_min': 15,                 # ROE tối thiểu 15%
    'eps_growth_min': 10,          # EPS growth > 10%
    'debt_to_equity_max': 1.5,     # D/E tối đa
    'dividend_yield_min': 0,       # Cổ tức min
    'market_cap_min': 1000,        # Vốn hóa min (tỷ VND)
}
```

---

## 📈 Kết quả mẫu

### Swing Trading

```
🎯 FPT | Điểm: 85/100
   Giá: 95,000 | RSI: 45.2 | Vol Ratio: 2.3x
   Hỗ trợ: 88,000 | Kháng cự: 102,000
   Stop-loss: 86,240 (-9.2%)
   Target 1: 102,000 | Target 2: 109,250
   Risk/Reward: 1:2.8
   Tín hiệu:
      📊 Volume đột biến: 2.3x TB20
      📈 RSI = 45.2 (vùng trung tính)
      🚀 BREAKOUT - Vượt đỉnh 20 phiên
      ✅ Giá trên MA20
      ✅ R/R = 1:2.8
```

### Đầu tư Dài hạn

```
🎯 VNM | Điểm: 90/100
   Giá: 72,500
   P/E: 18.5 | ROE: 28.5% | EPS Growth: 12.3%
   D/E: 0.35 | Dividend: 5.2%
   Market Cap: 125,000 tỷ
   Tín hiệu:
      ✅ P/E = 18.5 (hấp dẫn)
      ✅ ROE = 28.5% (tốt)
      ✅ EPS Growth = 12.3%
      ✅ D/E = 0.35 (an toàn)
      💰 Dividend Yield = 5.2%
```

---

## 📁 Cấu trúc file

```
VN30/
├── stock_screener.py     # Script chính
├── requirements.txt      # Thư viện cần cài
├── README.md            # Hướng dẫn (file này)
└── screener_results_*.csv  # Kết quả xuất ra
```

---

## ⚠️ Lưu ý

1. **Dữ liệu**: Script sử dụng `vnstock3` để lấy dữ liệu từ VCI. Nếu chưa cài, sẽ chạy chế độ demo với dữ liệu mẫu.

2. **Thời gian**: Quét 60 mã mất khoảng 2-3 phút do giới hạn API.

3. **Disclaimer**:
   > Đây là công cụ tham khảo, không phải lời khuyên đầu tư.
   > Bạn cần tự đánh giá và chịu trách nhiệm với quyết định của mình.

---

## 🔄 Cập nhật

- **v1.0** (2026-01-28): Phiên bản đầu tiên
  - Lọc Swing Trading
  - Lọc Đầu tư Dài hạn
  - Xuất CSV
  - Chế độ demo

---

## 📞 Hỗ trợ

Nếu gặp lỗi, hãy kiểm tra:

1. Đã cài đầy đủ thư viện chưa?
2. Kết nối internet ổn định?
3. Mã chứng khoán hợp lệ?

---

**Made with ❤️ for Vietnamese Investors**
# ax00
# ax00
