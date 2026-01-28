# -*- coding: utf-8 -*-
"""
STOCK SCREENER - LỌC MÃ CHỨNG KHOÁN VIỆT NAM
=============================================
Tự động lọc mã theo tiêu chí Swing Trading và Đầu tư Dài hạn
Sử dụng thư viện vnstock để lấy dữ liệu

Author: VN Stock Advisor
Version: 1.0
"""

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import time

# Import danh sách mã từ watchlist
try:
    from watchlist import (
        VN30, TOP_100_LIQUIDITY, TOP_200, TOP_250,
        SWING_WATCHLIST, LONGTERM_WATCHLIST, get_watchlist
    )
    WATCHLIST_AVAILABLE = True
except ImportError:
    WATCHLIST_AVAILABLE = False
    print("⚠️ Không tìm thấy file watchlist.py, sử dụng danh sách mặc định")

# ============================================================================
# CẤU HÌNH RATE LIMIT (Guest: 20 req/phút, mỗi mã = 2 req)
# ============================================================================

RATE_LIMIT_CONFIG = {
    'delay_between_requests': 7.0,    # 7 giây/mã (2 req × 3s + buffer)
    'retry_wait_time': 65,            # Chờ 65 giây khi bị rate limit
    'max_retries': 5,                 # Số lần thử lại tối đa
    'batch_size': 8,                  # Số mã trước khi nghỉ (8 mã × 2 = 16 req)
    'batch_rest_time': 15,            # Nghỉ 15 giây sau mỗi batch
}

# Nguồn dữ liệu: 'VNSTOCK' (có rate limit nhưng ổn định)
DATA_SOURCE = 'VNSTOCK'

# Đăng ký API key miễn phí tại https://vnstocks.com/login để tăng limit lên 60 req/phút

# ============================================================================
# CẤU HÌNH TIÊU CHÍ LỌC
# ============================================================================

# Tiêu chí Swing Trading (2-8 tuần)
SWING_CRITERIA = {
    'volume_ratio_min': 1.5,      # Volume > 150% TB 20 phiên
    'rsi_oversold': 30,            # RSI thoát vùng quá bán
    'rsi_overbought': 70,          # RSI chưa quá mua
    'risk_reward_min': 2.0,        # Risk/Reward tối thiểu 1:2
    'max_stop_loss_pct': 7,        # Stop-loss không quá 7%
    'min_price': 5000,             # Giá tối thiểu (tránh penny stock)
    'min_avg_volume': 100000,      # Khối lượng TB tối thiểu
}

# Tiêu chí Đầu tư Dài hạn (>6 tháng)
LONGTERM_CRITERIA = {
    'pe_max': 25,                  # P/E tối đa
    'roe_min': 15,                 # ROE tối thiểu 15%
    'eps_growth_min': 10,          # Tăng trưởng EPS > 10%
    'debt_to_equity_max': 1.5,     # Nợ/Vốn chủ sở hữu tối đa
    'dividend_yield_min': 0,       # Cổ tức (0 = không bắt buộc)
    'market_cap_min': 1000,        # Vốn hóa tối thiểu (tỷ VND)
}

# Danh sách mã VN30 (backup khi không lấy được từ API)
VN30_SYMBOLS = [
    'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
    'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
    'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE'
]

# Cấu hình sàn giao dịch
EXCHANGES = ['HOSE', 'HNX', 'UPCOM']  # Tất cả các sàn


def get_all_stock_symbols(exchanges=None, min_volume=50000, min_price=5000):
    """
    Lấy TOÀN BỘ mã cổ phiếu từ các sàn HOSE, HNX, UPCOM
    
    Args:
        exchanges: List sàn ['HOSE', 'HNX', 'UPCOM'] hoặc None = tất cả
        min_volume: Khối lượng TB tối thiểu để lọc mã "sống"
        min_price: Giá tối thiểu
    
    Returns:
        List mã cổ phiếu
    """
    if exchanges is None:
        exchanges = EXCHANGES
    
    all_symbols = []
    
    # Phương pháp 1: Sử dụng vnstock3
    try:
        from vnstock import Vnstock
        
        stock = Vnstock()
        
        for exchange in exchanges:
            try:
                # Lấy danh sách mã từ sàn
                listing = stock.stock(symbol='ACB', source='VCI').listing.all_symbols()
                
                if listing is not None and len(listing) > 0:
                    # Lọc theo sàn
                    if 'exchange' in listing.columns:
                        exchange_stocks = listing[listing['exchange'] == exchange]['symbol'].tolist()
                    elif 'organ_short_name' in listing.columns:
                        exchange_stocks = listing['symbol'].tolist()
                    else:
                        exchange_stocks = listing.iloc[:, 0].tolist()
                    
                    all_symbols.extend(exchange_stocks)
                    print(f"   ✅ {exchange}: {len(exchange_stocks)} mã")
                    
            except Exception as e:
                print(f"   ⚠️ Lỗi lấy mã từ {exchange}: {e}")
        
        if all_symbols:
            # Loại bỏ trùng lặp
            all_symbols = list(set(all_symbols))
            return all_symbols
            
    except ImportError:
        print("   ⚠️ vnstock3 chưa cài đặt")
    except Exception as e:
        print(f"   ⚠️ Lỗi vnstock3: {e}")
    
    # Phương pháp 2: Sử dụng API SSI/TCBS
    try:
        import requests
        
        print("   📡 Đang lấy danh sách mã từ API...")
        
        # API từ TCBS
        url = "https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/getAll"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                for item in data['data']:
                    symbol = item.get('ticker', item.get('symbol', ''))
                    exchange = item.get('exchange', '')
                    
                    if symbol and (not exchanges or exchange in exchanges):
                        all_symbols.append(symbol)
                
                print(f"   ✅ Lấy được {len(all_symbols)} mã từ TCBS API")
                return list(set(all_symbols))
        
    except Exception as e:
        print(f"   ⚠️ Lỗi TCBS API: {e}")
    
    # Phương pháp 3: Sử dụng API SSI
    try:
        import requests
        
        url = "https://iboard.ssi.com.vn/dchart/api/1.1/defaultAllStocks"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                for item in data['data']:
                    symbol = item.get('code', item.get('symbol', ''))
                    if symbol:
                        all_symbols.append(symbol)
                
                print(f"   ✅ Lấy được {len(all_symbols)} mã từ SSI API")
                return list(set(all_symbols))
                
    except Exception as e:
        print(f"   ⚠️ Lỗi SSI API: {e}")
    
    # Phương pháp 4: File CSV/JSON local hoặc danh sách cứng
    print("   ⚠️ Không lấy được từ API, sử dụng danh sách mở rộng...")
    return get_extended_symbol_list()


def get_extended_symbol_list():
    """
    Danh sách mã mở rộng khi không có API
    Bao gồm ~200 mã phổ biến nhất
    """
    return [
        # VN30
        'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
        'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
        'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE',
        # Ngân hàng
        'EIB', 'LPB', 'OCB', 'MSB', 'NAB', 'ABB', 'BAB', 'BVB', 'KLB', 'NVB',
        'PGB', 'SGB', 'VAB', 'VBB', 'VIB',
        # Chứng khoán
        'VND', 'VCI', 'HCM', 'SHS', 'VDS', 'BSI', 'CTS', 'FTS', 'ORS', 'TVS',
        'AGR', 'APG', 'ART', 'BMS', 'BVS', 'CSI', 'DSC', 'EVS', 'HAC', 'HBS',
        # Bất động sản
        'VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'DIG', 'HDG', 'NLG', 'PDR', 'TCH',
        'IJC', 'KBC', 'LDG', 'NBB', 'NTL', 'QCG', 'SCR', 'SJS', 'SZC', 'TDC',
        'CEO', 'CII', 'D2D', 'DPG', 'DRH', 'HAR', 'HDC', 'HQC', 'HUT', 'IDC',
        # Thép & Vật liệu
        'HPG', 'HSG', 'NKG', 'POM', 'SMC', 'TLH', 'VGS', 'DTL', 'HMC', 'VIS',
        # Dầu khí
        'GAS', 'PVD', 'PVS', 'OIL', 'PLX', 'BSR', 'PVC', 'PVB', 'PVT', 'PGS',
        # Điện
        'POW', 'PPC', 'NT2', 'REE', 'PC1', 'GEG', 'BCG', 'HND', 'VSH', 'SBA',
        'CHP', 'HJS', 'SHP', 'TBC', 'TMP', 'VPH',
        # Thực phẩm & Đồ uống
        'VNM', 'SAB', 'MSN', 'MCH', 'QNS', 'KDC', 'SBT', 'LSS', 'TAC', 'BBC',
        'HAT', 'HNG', 'VLC', 'ASM',
        # Công nghệ
        'FPT', 'CMG', 'FOX', 'ELC', 'ITD', 'SAM', 'SGT', 'TSC', 'VGI', 'ONE',
        # Bán lẻ
        'MWG', 'PNJ', 'DGW', 'FRT', 'PET', 'PLT', 'AMV',
        # Dệt may
        'TCM', 'VGT', 'MSH', 'TNG', 'GMC', 'GIL', 'STK', 'TVT', 'VGG',
        # Hóa chất & Phân bón
        'DGC', 'DPM', 'DCM', 'CSV', 'LAS', 'BFC', 'SFG', 'DDV', 'PHR',
        # Cao su
        'GVR', 'PHR', 'DPR', 'TRC', 'HRC', 'TNC', 'BRR',
        # Vận tải & Logistics
        'GMD', 'VOS', 'HAH', 'VTP', 'MVN', 'PAN', 'TCL', 'VNA', 'VTO', 'SCS',
        # Xây dựng
        'CTD', 'HBC', 'HUT', 'VCG', 'FCN', 'LCG', 'C4G', 'C47', 'CIG', 'CTI',
        'HHV', 'HTN', 'LM8', 'ROS', 'SC5', 'VC3', 'VC7', 'VCS',
        # Hàng không
        'VJC', 'HVN', 'ACV', 'SAS', 'AST',
        # Du lịch & Khách sạn  
        'VTR', 'DAH', 'DSN', 'VNG', 'HOT',
        # Y tế & Dược phẩm
        'DHG', 'DMC', 'IMP', 'DBD', 'DBT', 'DCL', 'DHT', 'PME', 'TRA', 'VMD',
        # Bảo hiểm
        'BVH', 'BMI', 'BIC', 'MIG', 'PGI', 'PRE', 'PTI', 'VNR',
        # Thủy sản
        'VHC', 'ANV', 'IDI', 'CMX', 'FMC', 'MPC', 'ACL', 'ABT', 'BLF', 'ICF',
        # Khác
        'REE', 'SIP', 'GEX', 'DBC', 'HAG', 'EVE', 'PAN', 'TNH', 'JVC', 'AAA',
    ]


# ============================================================================
# HÀM TÍNH TOÁN CHỈ BÁO KỸ THUẬT
# ============================================================================

def calculate_rsi(prices, period=14):
    """Tính RSI (Relative Strength Index)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Tính MACD"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Tính Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band


def calculate_support_resistance(df, window=20):
    """Tính vùng hỗ trợ và kháng cự"""
    high_max = df['high'].rolling(window=window).max()
    low_min = df['low'].rolling(window=window).min()
    return high_max.iloc[-1], low_min.iloc[-1]


def detect_breakout(df, period=20):
    """Phát hiện breakout"""
    if len(df) < period + 1:
        return False, None
    
    current_close = df['close'].iloc[-1]
    prev_high = df['high'].iloc[-period-1:-1].max()
    prev_low = df['low'].iloc[-period-1:-1].min()
    
    # Breakout lên
    if current_close > prev_high:
        return True, 'UP'
    # Breakout xuống
    elif current_close < prev_low:
        return True, 'DOWN'
    
    return False, None


def calculate_volume_ratio(df, period=20):
    """Tính tỷ lệ volume so với trung bình"""
    if len(df) < period:
        return 0
    
    current_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].iloc[-period:].mean()
    
    if avg_volume == 0:
        return 0
    
    return current_volume / avg_volume


# ============================================================================
# HÀM LỌC MÃ CHỨNG KHOÁN
# ============================================================================

def screen_swing_trading(symbol, df, fundamental_data=None):
    """
    Lọc mã theo tiêu chí Swing Trading
    
    Returns:
        dict: Kết quả phân tích hoặc None nếu không đạt
    """
    if df is None or len(df) < 30:
        return None
    
    try:
        # Tính các chỉ báo
        df['rsi'] = calculate_rsi(df['close'])
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        volume_ratio = calculate_volume_ratio(df)
        is_breakout, breakout_direction = detect_breakout(df)
        resistance, support = calculate_support_resistance(df)
        
        current_price = df['close'].iloc[-1]
        current_rsi = df['rsi'].iloc[-1]
        avg_volume = df['volume'].iloc[-20:].mean()
        
        # Điểm số
        score = 0
        signals = []
        
        # Kiểm tra giá tối thiểu
        if current_price < SWING_CRITERIA['min_price']:
            return None
        
        # Kiểm tra khối lượng TB
        if avg_volume < SWING_CRITERIA['min_avg_volume']:
            return None
        
        # 1. Volume đột biến
        if volume_ratio >= SWING_CRITERIA['volume_ratio_min']:
            score += 25
            signals.append(f"📊 Volume đột biến: {volume_ratio:.1f}x TB20")
        
        # 2. RSI thoát quá bán hoặc trong vùng tốt
        if SWING_CRITERIA['rsi_oversold'] < current_rsi < SWING_CRITERIA['rsi_overbought']:
            score += 20
            signals.append(f"📈 RSI = {current_rsi:.1f} (vùng trung tính)")
        elif current_rsi <= SWING_CRITERIA['rsi_oversold']:
            score += 15
            signals.append(f"⚠️ RSI = {current_rsi:.1f} (quá bán - chờ tín hiệu)")
        
        # 3. Breakout
        if is_breakout and breakout_direction == 'UP':
            score += 30
            signals.append("🚀 BREAKOUT - Vượt đỉnh 20 phiên")
        
        # 4. Giá trên MA20
        if current_price > df['sma_20'].iloc[-1]:
            score += 15
            signals.append("✅ Giá trên MA20")
        
        # 5. MA20 > MA50 (xu hướng tăng)
        if len(df) >= 50 and df['sma_20'].iloc[-1] > df['sma_50'].iloc[-1]:
            score += 10
            signals.append("📈 MA20 > MA50 (uptrend)")
        
        # Tính Stop-loss và Target
        stop_loss = support * 0.98  # Dưới hỗ trợ 2%
        stop_loss_pct = (current_price - stop_loss) / current_price * 100
        
        target_1 = resistance
        target_2 = current_price * 1.15  # +15%
        
        potential_gain = (target_1 - current_price) / current_price * 100
        risk_reward = potential_gain / stop_loss_pct if stop_loss_pct > 0 else 0
        
        # Kiểm tra Risk/Reward
        if risk_reward >= SWING_CRITERIA['risk_reward_min']:
            score += 15
            signals.append(f"✅ R/R = 1:{risk_reward:.1f}")
        
        # Kiểm tra stop-loss không quá lớn
        if stop_loss_pct > SWING_CRITERIA['max_stop_loss_pct']:
            score -= 20
            signals.append(f"⚠️ Stop-loss {stop_loss_pct:.1f}% > 7%")
        
        # Kết quả
        if score >= 50:  # Ngưỡng tối thiểu
            return {
                'symbol': symbol,
                'type': 'SWING',
                'score': score,
                'price': current_price,
                'volume_ratio': volume_ratio,
                'rsi': current_rsi,
                'support': support,
                'resistance': resistance,
                'stop_loss': stop_loss,
                'stop_loss_pct': stop_loss_pct,
                'target_1': target_1,
                'target_2': target_2,
                'risk_reward': risk_reward,
                'signals': signals,
                'breakout': is_breakout,
            }
        
        return None
        
    except Exception as e:
        print(f"Lỗi phân tích {symbol}: {e}")
        return None


def screen_long_term(symbol, df, fundamental_data):
    """
    Lọc mã theo tiêu chí Đầu tư Dài hạn
    
    Args:
        symbol: Mã chứng khoán
        df: DataFrame giá lịch sử
        fundamental_data: Dict chứa dữ liệu cơ bản (PE, ROE, EPS, ...)
    
    Returns:
        dict: Kết quả phân tích hoặc None nếu không đạt
    """
    if fundamental_data is None:
        return None
    
    try:
        score = 0
        signals = []
        
        pe = fundamental_data.get('pe', 999)
        roe = fundamental_data.get('roe', 0)
        eps_growth = fundamental_data.get('eps_growth', 0)
        debt_to_equity = fundamental_data.get('debt_to_equity', 999)
        dividend_yield = fundamental_data.get('dividend_yield', 0)
        market_cap = fundamental_data.get('market_cap', 0)
        
        current_price = df['close'].iloc[-1] if df is not None and len(df) > 0 else 0
        
        # 1. P/E hợp lý
        if 0 < pe <= LONGTERM_CRITERIA['pe_max']:
            score += 20
            signals.append(f"✅ P/E = {pe:.1f} (hấp dẫn)")
        elif pe > LONGTERM_CRITERIA['pe_max']:
            signals.append(f"⚠️ P/E = {pe:.1f} (cao)")
        
        # 2. ROE cao
        if roe >= LONGTERM_CRITERIA['roe_min']:
            score += 25
            signals.append(f"✅ ROE = {roe:.1f}% (tốt)")
        else:
            signals.append(f"⚠️ ROE = {roe:.1f}% (thấp)")
        
        # 3. Tăng trưởng EPS
        if eps_growth >= LONGTERM_CRITERIA['eps_growth_min']:
            score += 25
            signals.append(f"✅ EPS Growth = {eps_growth:.1f}%")
        
        # 4. Đòn bẩy tài chính
        if debt_to_equity <= LONGTERM_CRITERIA['debt_to_equity_max']:
            score += 15
            signals.append(f"✅ D/E = {debt_to_equity:.2f} (an toàn)")
        else:
            signals.append(f"⚠️ D/E = {debt_to_equity:.2f} (rủi ro)")
        
        # 5. Cổ tức
        if dividend_yield >= LONGTERM_CRITERIA['dividend_yield_min']:
            score += 10
            signals.append(f"💰 Dividend Yield = {dividend_yield:.1f}%")
        
        # 6. Vốn hóa
        if market_cap >= LONGTERM_CRITERIA['market_cap_min']:
            score += 5
            signals.append(f"🏢 Market Cap = {market_cap:,.0f} tỷ")
        
        # Kết quả
        if score >= 50:
            return {
                'symbol': symbol,
                'type': 'LONG_TERM',
                'score': score,
                'price': current_price,
                'pe': pe,
                'roe': roe,
                'eps_growth': eps_growth,
                'debt_to_equity': debt_to_equity,
                'dividend_yield': dividend_yield,
                'market_cap': market_cap,
                'signals': signals,
            }
        
        return None
        
    except Exception as e:
        print(f"Lỗi phân tích dài hạn {symbol}: {e}")
        return None


# ============================================================================
# HÀM LẤY DỮ LIỆU (HỖ TRỢ NHIỀU NGUỒN)
# ============================================================================

def get_stock_data(symbol, days=100, retry_count=0):
    """
    Lấy dữ liệu giá lịch sử - tự động chọn nguồn phù hợp
    """
    # Ưu tiên TCBS (không rate limit)
    if DATA_SOURCE == 'TCBS':
        df = get_stock_data_tcbs(symbol, days)
        if df is not None:
            return df
    
    # Fallback về vnstock
    return get_stock_data_vnstock(symbol, days, retry_count)


def get_stock_data_tcbs(symbol, days=100):
    """
    Lấy dữ liệu từ TCBS API - KHÔNG BỊ RATE LIMIT
    """
    try:
        import requests
        
        url = f"https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term"
        params = {
            'ticker': symbol,
            'type': 'stock',
            'resolution': 'D',
            'countBack': days
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                df = pd.DataFrame(data['data'])
                
                # Chuẩn hóa tên cột
                column_map = {
                    'tradingDate': 'time',
                    'open': 'open',
                    'high': 'high',
                    'low': 'low',
                    'close': 'close',
                    'volume': 'volume'
                }
                
                df = df.rename(columns=column_map)
                
                # Chuyển đổi giá (TCBS trả về đơn vị 1000 VND)
                for col in ['open', 'high', 'low', 'close']:
                    if col in df.columns:
                        df[col] = df[col] * 1000
                
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time').reset_index(drop=True)
                
                return df
        
        return None
        
    except Exception as e:
        return None


def get_stock_data_vnstock(symbol, days=100, retry_count=0):
    """
    Lấy dữ liệu từ vnstock (có rate limit)
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        df = stock.quote.history(start=start_date, end=end_date)
        
        if df is not None and len(df) > 0:
            df.columns = df.columns.str.lower()
            return df
        
        return None
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if 'rate limit' in error_msg or 'limit exceeded' in error_msg:
            if retry_count < RATE_LIMIT_CONFIG['max_retries']:
                wait_time = RATE_LIMIT_CONFIG['retry_wait_time']
                print(f"\n⏳ Rate limit! Chờ {wait_time}s...")
                time.sleep(wait_time)
                return get_stock_data_vnstock(symbol, days, retry_count + 1)
        
        return None


def get_fundamental_data_tcbs(symbol):
    """
    Lấy dữ liệu cơ bản từ TCBS API - KHÔNG RATE LIMIT
    """
    try:
        import requests
        
        # API lấy thông tin cơ bản
        url = f"https://apipubaws.tcbs.com.vn/tcanalysis/v1/ticker/{symbol}/overview"
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'pe': data.get('pe', 0) or 0,
                'roe': (data.get('roe', 0) or 0) * 100,
                'eps_growth': (data.get('growthRateEPS', 0) or 0) * 100,
                'debt_to_equity': data.get('debtToEquity', 0) or 0,
                'dividend_yield': (data.get('dividend', 0) or 0) * 100,
                'market_cap': (data.get('marketCap', 0) or 0) / 1e9,
            }
        
        return None
        
    except Exception as e:
        return None


def get_stock_data_alternative(symbol, days=100):
    """
    Phương án thay thế lấy dữ liệu bằng API
    """
    try:
        import requests
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Sử dụng API từ cafef hoặc vndirect
        url = f"https://api.vietstock.vn/ta/history"
        params = {
            'symbol': symbol,
            'resolution': 'D',
            'from': int(start_date.timestamp()),
            'to': int(end_date.timestamp())
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame({
                'time': pd.to_datetime(data['t'], unit='s'),
                'open': data['o'],
                'high': data['h'],
                'low': data['l'],
                'close': data['c'],
                'volume': data['v']
            })
            return df
        
        return None
        
    except Exception as e:
        print(f"Lỗi API {symbol}: {e}")
        return None


def get_fundamental_data(symbol):
    """
    Lấy dữ liệu cơ bản - tự động chọn nguồn
    """
    # Ưu tiên TCBS (không rate limit)
    if DATA_SOURCE == 'TCBS':
        data = get_fundamental_data_tcbs(symbol)
        if data is not None:
            return data
    
    # Fallback về vnstock
    return get_fundamental_data_vnstock(symbol)


def get_fundamental_data_vnstock(symbol):
    """
    Lấy dữ liệu cơ bản từ vnstock (có rate limit)
    """
    try:
        from vnstock import Vnstock
        
        stock = Vnstock().stock(symbol=symbol, source='VCI')
        
        # Lấy chỉ số tài chính
        ratio = stock.finance.ratio(period='quarter', lang='en')
        
        if ratio is not None and len(ratio) > 0:
            latest = ratio.iloc[-1]
            return {
                'pe': latest.get('priceToEarning', 0),
                'roe': latest.get('roe', 0) * 100,
                'eps_growth': latest.get('epsChange', 0) * 100,
                'debt_to_equity': latest.get('debtOnEquity', 0),
                'dividend_yield': latest.get('dividend', 0),
                'market_cap': latest.get('marketCap', 0) / 1e9,
            }
        
        return None
        
    except Exception as e:
        return None


# ============================================================================
# HÀM CHẠY CHÍNH
# ============================================================================

def run_screener(symbols=None, screen_type='ALL', exchanges=None, use_watchlist=None):
    """
    Chạy bộ lọc chứng khoán
    
    Args:
        symbols: Danh sách mã (None = sử dụng watchlist hoặc lấy từ API)
        screen_type: 'SWING', 'LONGTERM', hoặc 'ALL'
        exchanges: List sàn ['HOSE', 'HNX', 'UPCOM'] hoặc None = tất cả
        use_watchlist: 'VN30', 'TOP_100', 'TOP_200', 'TOP_250', 'SWING', 'LONGTERM'
    
    Returns:
        DataFrame kết quả
    """
    print("=" * 60)
    print("🔍 STOCK SCREENER - LỌC MÃ CHỨNG KHOÁN VIỆT NAM")
    print("=" * 60)
    print(f"📅 Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🌐 Nguồn dữ liệu: {DATA_SOURCE} {'(Không rate limit)' if DATA_SOURCE == 'TCBS' else '(Có rate limit)'}")
    
    # Lấy danh sách mã
    if symbols is not None:
        print(f"📊 Sử dụng danh sách tùy chỉnh: {len(symbols)} mã")
    elif use_watchlist and WATCHLIST_AVAILABLE:
        symbols = get_watchlist(use_watchlist)
        print(f"📊 Sử dụng watchlist [{use_watchlist}]: {len(symbols)} mã")
    else:
        # Mặc định dùng TOP_200 để tránh rate limit
        if WATCHLIST_AVAILABLE:
            symbols = TOP_200
            print(f"📊 Sử dụng TOP_200 mặc định: {len(symbols)} mã")
        else:
            print("\n📡 Đang lấy danh sách mã từ API...")
            symbols = get_all_stock_symbols(exchanges=exchanges)
            print(f"📊 Tổng số mã: {len(symbols)}")
    
    print(f"🎯 Loại lọc: {screen_type}")
    
    # Tính thời gian ước tính (TCBS nhanh hơn nhiều)
    if DATA_SOURCE == 'TCBS':
        delay = 0.5  # TCBS không rate limit, chỉ cần delay nhỏ
        batch_size = 50
        batch_rest = 2
    else:
        delay = RATE_LIMIT_CONFIG['delay_between_requests']
        batch_size = RATE_LIMIT_CONFIG['batch_size']
        batch_rest = RATE_LIMIT_CONFIG['batch_rest_time']
    
    total_time = len(symbols) * delay + (len(symbols) // batch_size) * batch_rest
    print(f"⏱️ Thời gian ước tính: {total_time // 60:.0f} phút {total_time % 60:.0f} giây")
    print(f"💡 Delay: {delay}s/mã | Batch: {batch_size} mã")
    print("-" * 60)
    
    swing_results = []
    longterm_results = []
    skipped = 0
    start_time = time.time()
    
    for i, symbol in enumerate(symbols, 1):
        elapsed = time.time() - start_time
        eta = (elapsed / i) * (len(symbols) - i) if i > 0 else 0
        print(f"\r⏳ {symbol} ({i}/{len(symbols)}) | Swing={len(swing_results)} LT={len(longterm_results)} Skip={skipped} | ETA: {eta/60:.1f}m   ", end="", flush=True)
        
        # Lấy dữ liệu
        df = get_stock_data(symbol)
        
        if df is None:
            skipped += 1
            time.sleep(delay)
            continue
        
        fundamental = get_fundamental_data(symbol)
        
        # Lọc Swing
        if screen_type in ['SWING', 'ALL']:
            result = screen_swing_trading(symbol, df, fundamental)
            if result:
                swing_results.append(result)
        
        # Lọc Dài hạn
        if screen_type in ['LONGTERM', 'ALL']:
            result = screen_long_term(symbol, df, fundamental)
            if result:
                longterm_results.append(result)
        
        # Delay (TCBS không cần delay nhiều)
        time.sleep(delay)
        
        # Nghỉ thêm sau mỗi batch (chỉ cần cho vnstock)
        if DATA_SOURCE != 'TCBS' and i % batch_size == 0:
            print(f"\n   💤 Nghỉ {batch_rest}s sau batch {i // batch_size}...")
            time.sleep(batch_rest)
    
    # Tổng thời gian
    total_elapsed = time.time() - start_time
    print(f"\n\n⏱️ Hoàn thành trong {total_elapsed/60:.1f} phút")
    
    # In kết quả Swing Trading
    if swing_results:
        swing_results.sort(key=lambda x: x['score'], reverse=True)
        print_swing_results(swing_results)
    
    # In kết quả Dài hạn
    if longterm_results:
        longterm_results.sort(key=lambda x: x['score'], reverse=True)
        print_longterm_results(longterm_results)
    
    # Thống kê
    print("\n" + "=" * 60)
    print("📊 THỐNG KÊ")
    print("=" * 60)
    print(f"   Nguồn dữ liệu: {DATA_SOURCE}")
    print(f"   Tổng mã quét: {len(symbols)}")
    print(f"   Mã bị bỏ qua (lỗi): {skipped}")
    print(f"   Mã đạt tiêu chí Swing: {len(swing_results)}")
    print(f"   Mã đạt tiêu chí Dài hạn: {len(longterm_results)}")
    print(f"   Thời gian: {total_elapsed/60:.1f} phút")
    
    return swing_results, longterm_results


def print_swing_results(results):
    """In kết quả lọc Swing Trading"""
    print("\n" + "=" * 60)
    print("📈 KẾT QUẢ LỌC SWING TRADING")
    print("=" * 60)
    
    for r in results[:10]:  # Top 10
        print(f"\n🎯 {r['symbol']} | Điểm: {r['score']}/100")
        print(f"   Giá: {r['price']:,.0f} | RSI: {r['rsi']:.1f} | Vol Ratio: {r['volume_ratio']:.1f}x")
        print(f"   Hỗ trợ: {r['support']:,.0f} | Kháng cự: {r['resistance']:,.0f}")
        print(f"   Stop-loss: {r['stop_loss']:,.0f} (-{r['stop_loss_pct']:.1f}%)")
        print(f"   Target 1: {r['target_1']:,.0f} | Target 2: {r['target_2']:,.0f}")
        print(f"   Risk/Reward: 1:{r['risk_reward']:.1f}")
        print("   Tín hiệu:")
        for signal in r['signals']:
            print(f"      {signal}")
    
    print("\n" + "-" * 60)


def print_longterm_results(results):
    """In kết quả lọc Dài hạn"""
    print("\n" + "=" * 60)
    print("🏦 KẾT QUẢ LỌC ĐẦU TƯ DÀI HẠN")
    print("=" * 60)
    
    for r in results[:10]:  # Top 10
        print(f"\n🎯 {r['symbol']} | Điểm: {r['score']}/100")
        print(f"   Giá: {r['price']:,.0f}")
        print(f"   P/E: {r['pe']:.1f} | ROE: {r['roe']:.1f}% | EPS Growth: {r['eps_growth']:.1f}%")
        print(f"   D/E: {r['debt_to_equity']:.2f} | Dividend: {r['dividend_yield']:.1f}%")
        print(f"   Market Cap: {r['market_cap']:,.0f} tỷ")
        print("   Tín hiệu:")
        for signal in r['signals']:
            print(f"      {signal}")
    
    print("\n" + "-" * 60)


def export_to_csv(swing_results, longterm_results, filename=None):
    """Xuất kết quả ra file CSV"""
    if filename is None:
        filename = f"screener_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    
    all_results = []
    
    for r in swing_results:
        all_results.append({
            'Mã': r['symbol'],
            'Loại': 'SWING',
            'Điểm': r['score'],
            'Giá': r['price'],
            'RSI': r.get('rsi', ''),
            'Volume Ratio': r.get('volume_ratio', ''),
            'Stop-loss': r.get('stop_loss', ''),
            'Target 1': r.get('target_1', ''),
            'R/R': r.get('risk_reward', ''),
        })
    
    for r in longterm_results:
        all_results.append({
            'Mã': r['symbol'],
            'Loại': 'LONG_TERM',
            'Điểm': r['score'],
            'Giá': r['price'],
            'P/E': r.get('pe', ''),
            'ROE': r.get('roe', ''),
            'EPS Growth': r.get('eps_growth', ''),
            'D/E': r.get('debt_to_equity', ''),
        })
    
    df = pd.DataFrame(all_results)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ Đã xuất kết quả ra file: {filename}")
    
    return filename


# ============================================================================
# DEMO VỚI DỮ LIỆU MẪU (Khi không có vnstock)
# ============================================================================

def generate_sample_data(symbol, days=100):
    """Tạo dữ liệu mẫu để demo"""
    np.random.seed(hash(symbol) % 2**32)
    
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    base_price = np.random.randint(20, 150) * 1000
    
    prices = [base_price]
    for _ in range(days - 1):
        change = np.random.randn() * 0.02
        prices.append(prices[-1] * (1 + change))
    
    prices = np.array(prices)
    
    df = pd.DataFrame({
        'time': dates,
        'open': prices * (1 + np.random.randn(days) * 0.01),
        'high': prices * (1 + np.abs(np.random.randn(days) * 0.02)),
        'low': prices * (1 - np.abs(np.random.randn(days) * 0.02)),
        'close': prices,
        'volume': np.random.randint(100000, 5000000, days)
    })
    
    return df


def generate_sample_fundamental(symbol):
    """Tạo dữ liệu cơ bản mẫu để demo"""
    np.random.seed(hash(symbol) % 2**32)
    
    return {
        'pe': np.random.uniform(8, 30),
        'roe': np.random.uniform(5, 25),
        'eps_growth': np.random.uniform(-10, 30),
        'debt_to_equity': np.random.uniform(0.2, 2.0),
        'dividend_yield': np.random.uniform(0, 8),
        'market_cap': np.random.uniform(500, 50000),
    }


def run_demo():
    """Chạy demo với dữ liệu mẫu - sử dụng TOÀN BỘ mã mở rộng"""
    print("\n" + "=" * 60)
    print("🧪 DEMO MODE - SỬ DỤNG DỮ LIỆU MẪU")
    print("=" * 60)
    print("(Cài vnstock3 để lấy dữ liệu thực)")
    print("-" * 60)
    
    # Sử dụng danh sách mã mở rộng thay vì chỉ VN30
    symbols = get_extended_symbol_list()
    # Loại bỏ trùng lặp
    symbols = list(set(symbols))
    
    print(f"📊 Tổng số mã quét: {len(symbols)}")
    
    swing_results = []
    longterm_results = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\r⏳ Đang quét: {symbol} ({i}/{len(symbols)})...", end="", flush=True)
        
        df = generate_sample_data(symbol)
        fundamental = generate_sample_fundamental(symbol)
        
        # Lọc Swing
        result = screen_swing_trading(symbol, df, fundamental)
        if result:
            swing_results.append(result)
        
        # Lọc Dài hạn
        result = screen_long_term(symbol, df, fundamental)
        if result:
            longterm_results.append(result)
    
    print("\n")
    
    if swing_results:
        swing_results.sort(key=lambda x: x['score'], reverse=True)
        print_swing_results(swing_results)
    
    if longterm_results:
        longterm_results.sort(key=lambda x: x['score'], reverse=True)
        print_longterm_results(longterm_results)
    
    return swing_results, longterm_results


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║       🇻🇳 STOCK SCREENER - LỌC MÃ CHỨNG KHOÁN VIỆT NAM          ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║  ✅ Hỗ trợ Watchlist để tránh Rate Limit                         ║
    ║  📊 Phong cách: Swing Trading + Đầu tư Dài hạn                   ║
    ║  🎯 Tiêu chí: Kỹ thuật + Cơ bản                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    print("=" * 60)
    print("📋 CHỌN DANH SÁCH MÃ ĐỂ QUÉT")
    print("=" * 60)
    print()
    print("  🏆 WATCHLIST CỐ ĐỊNH (Khuyến nghị - tránh rate limit):")
    print("     1. VN30         - 30 mã bluechip")
    print("     2. TOP 100      - 100 mã thanh khoản cao")
    print("     3. TOP 200      - 200 mã (mặc định)")
    print("     4. TOP 250      - 250 mã đầy đủ")
    print("     5. SWING        - Mã tốt cho Swing Trading")
    print("     6. LONGTERM     - Mã tốt cho Đầu tư dài hạn")
    print()
    print("  🌐 QUÉT TỪ API (Có thể bị rate limit):")
    print("     7. HOSE         - Tất cả mã sàn HOSE")
    print("     8. ALL          - Tất cả (HOSE + HNX + UPCOM)")
    print()
    print("  🧪 DEMO:")
    print("     9. Demo         - Dữ liệu mẫu (test)")
    print()
    print("=" * 60)
    
    try:
        choice = input("Nhập lựa chọn (1-9, mặc định=3): ").strip()
    except:
        choice = "3"
    
    if not choice:
        choice = "3"
    
    if choice == "1":
        print("\n🚀 Quét VN30 (30 mã)...")
        if WATCHLIST_AVAILABLE:
            swing_results, longterm_results = run_screener(use_watchlist='VN30')
        else:
            swing_results, longterm_results = run_screener(symbols=VN30_SYMBOLS)
    
    elif choice == "2":
        print("\n🚀 Quét TOP 100 mã thanh khoản cao...")
        swing_results, longterm_results = run_screener(use_watchlist='TOP_100')
    
    elif choice == "3":
        print("\n🚀 Quét TOP 200 mã (Khuyến nghị)...")
        swing_results, longterm_results = run_screener(use_watchlist='TOP_200')
    
    elif choice == "4":
        print("\n🚀 Quét TOP 250 mã đầy đủ...")
        swing_results, longterm_results = run_screener(use_watchlist='TOP_250')
    
    elif choice == "5":
        print("\n🚀 Quét mã phù hợp Swing Trading...")
        swing_results, longterm_results = run_screener(use_watchlist='SWING', screen_type='SWING')
    
    elif choice == "6":
        print("\n🚀 Quét mã phù hợp Đầu tư dài hạn...")
        swing_results, longterm_results = run_screener(use_watchlist='LONGTERM', screen_type='LONGTERM')
    
    elif choice == "7":
        print("\n🚀 Quét tất cả mã sàn HOSE...")
        print("⚠️  Cảnh báo: Có thể bị rate limit!")
        swing_results, longterm_results = run_screener(exchanges=['HOSE'])
    
    elif choice == "8":
        print("\n🚀 Quét TẤT CẢ mã từ HOSE, HNX, UPCOM...")
        print("⚠️  Cảnh báo: Có thể mất nhiều giờ và bị rate limit!")
        swing_results, longterm_results = run_screener(exchanges=['HOSE', 'HNX', 'UPCOM'])
    
    else:
        print("\n🧪 Chạy chế độ demo với dữ liệu mẫu...")
        swing_results, longterm_results = run_demo()
    
    # Xuất CSV
    if swing_results or longterm_results:
        export_to_csv(swing_results, longterm_results)
    
    print("\n✅ Hoàn thành!")
