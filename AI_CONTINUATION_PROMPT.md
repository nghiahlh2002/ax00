# 📋 AI CONTINUATION PROMPT - Vietnam Stock Screener

## 🎯 Mục đích file này
File này chứa thông tin để bất kỳ AI nào (ChatGPT, Gemini, Claude, etc.) có thể tiếp tục phát triển dự án.

---

## 📁 TỔNG QUAN DỰ ÁN

### Mô tả
Hệ thống lọc cổ phiếu Việt Nam tự động với 2 phong cách đầu tư:
- **Swing Trading**: Giao dịch ngắn hạn 2-8 tuần
- **Long-term Investment**: Đầu tư dài hạn >6 tháng

### Công nghệ
- Python 3.13
- vnstock3 (thư viện lấy dữ liệu chứng khoán VN)
- pandas, numpy (xử lý dữ liệu)

### Cấu trúc thư mục
```
VN30/
├── stock_screener.py    # Script chính (~1100 dòng)
├── watchlist.py         # Danh sách mã cố định (250 mã)
├── requirements.txt     # Dependencies
├── HUONG_DAN_KY_THUAT.md # Tài liệu kỹ thuật
├── README.md            # Hướng dẫn sử dụng
└── .venv/               # Virtual environment
```

---

## 📊 CÁC FILE CHÍNH

### 1. stock_screener.py
**Chức năng chính:**
- `get_stock_data()`: Lấy dữ liệu giá từ vnstock API
- `get_fundamental_data()`: Lấy dữ liệu cơ bản (P/E, ROE, etc.)
- `calculate_rsi()`: Tính chỉ báo RSI
- `calculate_macd()`: Tính chỉ báo MACD
- `calculate_bollinger_bands()`: Tính Bollinger Bands
- `detect_breakout()`: Phát hiện breakout
- `screen_swing_trading()`: Chấm điểm Swing Trading (0-100)
- `screen_long_term()`: Chấm điểm đầu tư dài hạn (0-100)
- `run_screener()`: Vòng lặp chính quét tất cả mã

**Tiêu chí Swing Trading:**
```python
SWING_CRITERIA = {
    'volume_ratio_min': 1.5,      # Volume > 1.5x trung bình 20 phiên
    'rsi_oversold': 30,           # RSI < 30 = quá bán
    'rsi_overbought': 70,         # RSI > 70 = quá mua
    'min_risk_reward': 2.0,       # Risk/Reward tối thiểu 1:2
    'max_stop_loss_pct': 7,       # Stop-loss tối đa 7%
    'min_score': 50               # Điểm tối thiểu để hiển thị
}
```

**Tiêu chí Long-term:**
```python
LONGTERM_CRITERIA = {
    'max_pe': 25,                 # P/E < 25
    'min_roe': 15,                # ROE > 15%
    'min_eps_growth': 10,         # EPS tăng trưởng > 10%
    'max_de': 1.5,                # D/E < 1.5
    'min_score': 50               # Điểm tối thiểu
}
```

### 2. watchlist.py
**Các danh sách có sẵn:**
- `VN30`: 30 mã bluechip
- `TOP_100_LIQUIDITY`: 100 mã thanh khoản cao
- `TOP_200`: 186 mã
- `TOP_250`: 233 mã
- `SWING_WATCHLIST`: 43 mã tốt cho swing
- `LONGTERM_WATCHLIST`: 43 mã tốt cho dài hạn

**Phân theo ngành:**
```python
BANKS = ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'ACB', ...]
SECURITIES = ['SSI', 'VND', 'HCM', 'VCI', 'SHS', ...]
REAL_ESTATE = ['VHM', 'VIC', 'NVL', 'DXG', 'KDH', ...]
# ... và nhiều ngành khác
```

---

## ⚠️ VẤN ĐỀ ĐANG GẶP

### 1. Rate Limit của vnstock API
- **Guest tier**: 20 requests/phút
- **Community tier**: 60 requests/phút (cần đăng ký miễn phí)
- Mỗi mã cần 2 API calls (price + fundamental)
- Quét 200 mã cần ~22 phút với delay 7s/mã

### 2. Giải pháp đã thử (KHÔNG thành công)
- TCBS API: Trả về 404 Not Found
- VNDirect API: ConnectionResetError
- Cafef/VietstockFinance: Cần scraping phức tạp

### 3. Giải pháp hiện tại
```python
RATE_LIMIT_CONFIG = {
    'delay_between_requests': 7,    # 7 giây/request
    'batch_size': 8,                # 8 mã/batch
    'batch_rest_time': 30,          # Nghỉ 30s sau mỗi batch
    'retry_wait': 65,               # Đợi 65s nếu bị rate limit
    'max_retries': 3                # Thử lại tối đa 3 lần
}
```

---

## 🚀 HƯỚNG PHÁT TRIỂN TIẾP THEO

### Priority 1: Cải thiện hiệu suất
- [ ] Implement caching để lưu dữ liệu đã fetch
- [ ] Sử dụng async/await để fetch song song
- [ ] Tìm API thay thế không rate limit

### Priority 2: Tính năng mới
- [ ] Thêm chỉ báo kỹ thuật: Stochastic, ADX, OBV
- [ ] Phân tích xu hướng ngành (sector analysis)
- [ ] Backtest chiến lược
- [ ] Gửi thông báo qua Telegram/Email

### Priority 3: UI/UX
- [ ] Tạo giao diện web (Flask/Streamlit)
- [ ] Dashboard với biểu đồ
- [ ] Lịch sử kết quả quét

---

## 📝 PROMPT MẪU ĐỂ SỬ DỤNG VỚI AI KHÁC

### Prompt ngắn gọn (Để bắt đầu)
```
Tôi có dự án Python lọc cổ phiếu Việt Nam. Dự án dùng vnstock3 để lấy dữ liệu, có 2 file chính:
- stock_screener.py: Tính các chỉ báo RSI, MACD, Bollinger và chấm điểm
- watchlist.py: Danh sách 250 mã cổ phiếu

Vấn đề: vnstock API giới hạn 20 req/phút. Quét 200 mã mất 22 phút.

Hãy giúp tôi [YÊU CẦU CỤ THỂ]
```

### Prompt chi tiết (Để tiếp tục phát triển)
```
# CONTEXT
Tôi đang phát triển hệ thống lọc cổ phiếu Việt Nam với Python.

# CURRENT STATE
## Files:
1. stock_screener.py (~1100 lines): 
   - Lấy dữ liệu từ vnstock3 API
   - Tính chỉ báo: RSI, MACD, Bollinger Bands, Volume Ratio
   - Phát hiện breakout, hỗ trợ/kháng cự
   - Chấm điểm Swing Trading (0-100) và Long-term (0-100)
   - Xuất CSV kết quả

2. watchlist.py: 
   - Danh sách cố định 250 mã cổ phiếu
   - Phân theo ngành: Banks, Securities, Real Estate, etc.

## Technical Stack:
- Python 3.13
- vnstock3 (data source)
- pandas, numpy

## Current Criteria:
Swing: Volume > 1.5x avg, RSI 30-70, R/R > 2:1, Stop-loss < 7%
Longterm: P/E < 25, ROE > 15%, EPS growth > 10%, D/E < 1.5

# PROBLEM
vnstock API rate limit: 20 req/min (Guest), 60 req/min (Community)
Each stock needs 2 API calls → 200 stocks = 400 calls = 20+ minutes

# REQUEST
[ĐIỀN YÊU CẦU CỤ THỂ CỦA BẠN]

Ví dụ:
- Thêm caching để lưu dữ liệu và giảm API calls
- Tạo giao diện web với Streamlit
- Thêm chỉ báo Stochastic RSI
- Backtest chiến lược 6 tháng gần nhất
- Gửi alert qua Telegram khi có mã mới
```

### Prompt để thêm tính năng cụ thể
```
# File: stock_screener.py
# Đã có: RSI, MACD, Bollinger Bands, Volume Ratio, Breakout detection

Thêm chức năng [TÊN TÍNH NĂNG] với yêu cầu:
1. [Yêu cầu 1]
2. [Yêu cầu 2]
3. Tích hợp vào hàm screen_swing_trading() hoặc screen_long_term()
4. Thêm điểm số vào scoring system hiện tại

Giữ nguyên code structure hiện tại. Output bằng tiếng Việt.
```

---

## 🤖 SO SÁNH CÁC AI

| Tiêu chí | ChatGPT-4 | Gemini 2.0 | Claude 3.5 |
|----------|-----------|------------|------------|
| **Code generation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Hiểu context dài** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Debug code** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Tiếng Việt** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Giá** | $20/tháng | Free/$20 | $20/tháng |

### Khuyến nghị:
- **ChatGPT-4**: Tốt cho refactoring lớn, viết code mới
- **Gemini 2.0 Flash**: Tốt cho context dài, phân tích file lớn, miễn phí
- **Claude 3.5 Sonnet**: Tốt cho code chính xác, ít lỗi

**Đề xuất**: Dùng **Gemini 2.0** (miễn phí, context window lớn) hoặc **Claude** (code quality cao)

---

## 📎 CÁCH SHARE CODE CHO AI

### Option 1: Copy trực tiếp
Copy nội dung file stock_screener.py và watchlist.py vào prompt

### Option 2: GitHub
1. Push code lên GitHub
2. Share link repo với AI

### Option 3: Tóm tắt
Chỉ share phần code liên quan đến yêu cầu cụ thể

---

## 💡 LƯU Ý KHI LÀM VIỆC VỚI AI

1. **Chia nhỏ yêu cầu**: Thay vì "thêm nhiều tính năng", hãy yêu cầu từng tính năng một
2. **Cung cấp context**: Share code hiện tại để AI hiểu structure
3. **Test từng bước**: Chạy thử sau mỗi thay đổi
4. **Backup code**: Lưu version trước khi sửa đổi lớn
5. **Review kỹ**: AI có thể đưa ra code không hoạt động, cần test

---

*File này được tạo bởi GitHub Copilot - 28/01/2026*
