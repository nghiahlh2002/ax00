# -*- coding: utf-8 -*-
"""
WATCHLIST - DANH SÁCH MÃ CỐ ĐỊNH ĐỂ QUÉT
=========================================
Danh sách ~250 mã đã được chọn lọc dựa trên:
- Thanh khoản tốt (Volume TB > 100,000/ngày)
- Vốn hóa đủ lớn (> 500 tỷ)
- Thuộc các ngành quan trọng

Cập nhật: 28/01/2026
"""

# ============================================================================
# DANH SÁCH MÃ THEO NGÀNH
# ============================================================================

# VN30 - 30 mã bluechip lớn nhất
VN30 = [
    'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
    'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
    'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE'
]

# Ngân hàng (Banks) - Thanh khoản rất cao
BANKS = [
    'ACB', 'BID', 'CTG', 'EIB', 'HDB', 'LPB', 'MBB', 'MSB', 'OCB', 'SHB',
    'SSB', 'STB', 'TCB', 'TPB', 'VCB', 'VIB', 'VPB',
    # Ngân hàng nhỏ hơn
    'ABB', 'BAB', 'BVB', 'KLB', 'NAB', 'NVB', 'PGB', 'SGB', 'VAB', 'VBB'
]

# Chứng khoán (Securities) - Biến động mạnh, tốt cho swing
SECURITIES = [
    'SSI', 'VND', 'HCM', 'VCI', 'SHS', 'MBS', 'VDS', 'BSI', 'CTS', 'FTS',
    'ORS', 'TVS', 'AGR', 'APG', 'ART', 'BMS', 'BVS', 'DSC', 'EVS', 'HBS',
    'IVS', 'KIS', 'PHS', 'PSI', 'TCI', 'VFS', 'VIG', 'VIX', 'WSS'
]

# Bất động sản (Real Estate) - Chu kỳ, quan trọng
REAL_ESTATE = [
    'VHM', 'VIC', 'NVL', 'KDH', 'DXG', 'DIG', 'HDG', 'NLG', 'PDR', 'TCH',
    'IJC', 'KBC', 'LDG', 'NBB', 'NTL', 'QCG', 'SCR', 'SJS', 'SZC', 'TDC',
    'CEO', 'CII', 'D2D', 'DPG', 'DRH', 'HAR', 'HDC', 'HQC', 'HUT', 'IDC',
    'ITA', 'LHG', 'NBB', 'NHA', 'NRC', 'PPI', 'PTL', 'VRC', 'VRE'
]

# Thép & Vật liệu xây dựng (Steel & Materials)
STEEL_MATERIALS = [
    'HPG', 'HSG', 'NKG', 'POM', 'SMC', 'TLH', 'VGS', 'DTL', 'HMC', 'VIS',
    'TIS', 'DNH', 'VCA', 'TVN', 'TKU'
]

# Dầu khí (Oil & Gas)
OIL_GAS = [
    'GAS', 'PVD', 'PVS', 'OIL', 'PLX', 'BSR', 'PVC', 'PVB', 'PVT', 'PGS',
    'PGC', 'PGD', 'PVG', 'PVI', 'PXS', 'PXT', 'TDG'
]

# Điện (Power)
POWER = [
    'POW', 'PPC', 'NT2', 'REE', 'PC1', 'GEG', 'BCG', 'HND', 'VSH', 'SBA',
    'CHP', 'HJS', 'SHP', 'TBC', 'TMP', 'VPH', 'TV2', 'NBP', 'QTP', 'SJD',
    'TTA', 'BTP', 'HNA', 'DNE', 'GEE', 'HDG', 'KHP', 'NSH', 'PGV', 'PIC'
]

# Thực phẩm & Đồ uống (Food & Beverage)
FOOD_BEVERAGE = [
    'VNM', 'SAB', 'MSN', 'MCH', 'QNS', 'KDC', 'SBT', 'LSS', 'TAC', 'BBC',
    'HAT', 'HNG', 'VLC', 'ASM', 'CLC', 'DBC', 'GTN', 'HVG', 'KDF', 'LAF',
    'NAF', 'NSC', 'SAF', 'SCD', 'VCF', 'VFG', 'VNS'
]

# Công nghệ (Technology)
TECHNOLOGY = [
    'FPT', 'CMG', 'FOX', 'ELC', 'ITD', 'SAM', 'SGT', 'TSC', 'VGI', 'ONE',
    'VTC', 'ICT', 'POT', 'ST8', 'VNT'
]

# Bán lẻ (Retail)
RETAIL = [
    'MWG', 'PNJ', 'DGW', 'FRT', 'PET', 'PLT', 'AMV', 'VGC', 'HAX', 'TMT'
]

# Dệt may (Textiles)
TEXTILES = [
    'TCM', 'VGT', 'MSH', 'TNG', 'GMC', 'GIL', 'STK', 'TVT', 'VGG', 'ADS',
    'EVE', 'HTG', 'MPT', 'PPH', 'TET', 'VTL'
]

# Hóa chất & Phân bón (Chemicals & Fertilizers)
CHEMICALS = [
    'DGC', 'DPM', 'DCM', 'CSV', 'LAS', 'BFC', 'SFG', 'DDV', 'PHR', 'HVT',
    'NFC', 'PMB', 'PCE'
]

# Cao su (Rubber)
RUBBER = [
    'GVR', 'PHR', 'DPR', 'TRC', 'HRC', 'TNC', 'BRR', 'DRI', 'RTB', 'SBR'
]

# Vận tải & Logistics (Transportation & Logistics)
LOGISTICS = [
    'GMD', 'VOS', 'HAH', 'VTP', 'MVN', 'PAN', 'TCL', 'VNA', 'VTO', 'SCS',
    'PDN', 'VNS', 'VTR', 'VSC', 'TMS', 'STG', 'MAC', 'MHC', 'TJC', 'VNL'
]

# Xây dựng (Construction)
CONSTRUCTION = [
    'CTD', 'HBC', 'HUT', 'VCG', 'FCN', 'LCG', 'C4G', 'C47', 'CIG', 'CTI',
    'HHV', 'HTN', 'LM8', 'ROS', 'SC5', 'VC3', 'VC7', 'VCS', 'BCE', 'CC1',
    'CDC', 'CTN', 'HU1', 'HU3', 'L10', 'LCD', 'MCG', 'SD6', 'SD9', 'SDD'
]

# Hàng không (Aviation)
AVIATION = [
    'VJC', 'HVN', 'ACV', 'SAS', 'AST', 'NCT', 'NCS', 'SGN'
]

# Du lịch & Khách sạn (Tourism & Hotels)
TOURISM = [
    'VTR', 'DAH', 'DSN', 'VNG', 'HOT', 'OCH', 'PDC', 'RIC', 'SHN', 'TCT',
    'TTD', 'VIR'
]

# Y tế & Dược phẩm (Healthcare & Pharma)
HEALTHCARE = [
    'DHG', 'DMC', 'IMP', 'DBD', 'DBT', 'DCL', 'DHT', 'PME', 'TRA', 'VMD',
    'AME', 'CDP', 'DNM', 'OPC', 'PDC', 'PPP', 'SPM', 'VDP', 'VPH'
]

# Bảo hiểm (Insurance)
INSURANCE = [
    'BVH', 'BMI', 'BIC', 'MIG', 'PGI', 'PRE', 'PTI', 'VNR', 'ABI', 'AIC',
    'BLI', 'PVI', 'SHI', 'VRE'
]

# Thủy sản (Seafood)
SEAFOOD = [
    'VHC', 'ANV', 'IDI', 'CMX', 'FMC', 'MPC', 'ACL', 'ABT', 'BLF', 'ICF',
    'AAM', 'AGF', 'CAD', 'NGC', 'SJ1', 'SPD', 'TS4', 'VNH'
]

# ============================================================================
# DANH SÁCH TỔNG HỢP THEO MỤC ĐÍCH
# ============================================================================

# TOP 100 - Thanh khoản cao nhất (ưu tiên quét)
TOP_100_LIQUIDITY = [
    # VN30
    'ACB', 'BCM', 'BID', 'BVH', 'CTG', 'FPT', 'GAS', 'GVR', 'HDB', 'HPG',
    'MBB', 'MSN', 'MWG', 'PLX', 'POW', 'SAB', 'SHB', 'SSB', 'SSI', 'STB',
    'TCB', 'TPB', 'VCB', 'VHM', 'VIB', 'VIC', 'VJC', 'VNM', 'VPB', 'VRE',
    # Ngân hàng + Chứng khoán
    'EIB', 'LPB', 'OCB', 'MSB', 'VND', 'HCM', 'VCI', 'SHS',
    # Bất động sản + Xây dựng
    'NVL', 'KDH', 'DXG', 'DIG', 'PDR', 'NLG', 'KBC', 'CTD', 'HBC',
    # Thép
    'HSG', 'NKG',
    # Dầu khí
    'PVD', 'PVS', 'OIL', 'BSR',
    # Điện
    'NT2', 'REE', 'PC1', 'GEG',
    # Thực phẩm
    'QNS', 'KDC', 'DBC',
    # Công nghệ
    'CMG', 'ELC',
    # Bán lẻ
    'PNJ', 'DGW', 'FRT',
    # Hóa chất
    'DGC', 'DPM', 'DCM',
    # Vận tải
    'GMD', 'HAH', 'VTP',
    # Hàng không
    'HVN', 'ACV',
    # Y tế
    'DHG', 'DMC', 'IMP',
    # Thủy sản
    'VHC', 'ANV', 'IDI',
    # Cao su
    'PHR', 'DPR',
    # Khác
    'HDG', 'TCH', 'IJC', 'CEO', 'HAG', 'HNG', 'PAN', 'SBT', 'LSS'
]

# TOP 200 - Đầy đủ hơn
TOP_200 = TOP_100_LIQUIDITY + [
    # Ngân hàng nhỏ
    'ABB', 'BAB', 'BVB', 'KLB', 'NAB', 'NVB', 'PGB', 'VAB',
    # Chứng khoán
    'MBS', 'VDS', 'BSI', 'CTS', 'FTS', 'ORS', 'TVS', 'AGR', 'VIX',
    # BĐS
    'HDC', 'LDG', 'SCR', 'SJS', 'TDC', 'D2D', 'DPG', 'ITA', 'NRC',
    # Thép
    'POM', 'SMC', 'TLH', 'VGS',
    # Dầu khí
    'PVC', 'PVB', 'PVT', 'PGS', 'PVI',
    # Điện
    'PPC', 'BCG', 'HND', 'VSH', 'SBA', 'CHP', 'TV2', 'NBP', 'PGV',
    # Thực phẩm
    'MCH', 'TAC', 'BBC', 'VCF', 'VFG',
    # Công nghệ
    'SAM', 'SGT', 'VGI',
    # Bán lẻ
    'PET', 'TMT',
    # Dệt may
    'TCM', 'VGT', 'MSH', 'TNG', 'STK',
    # Hóa chất
    'CSV', 'LAS', 'BFC', 'SFG',
    # Cao su
    'TRC', 'HRC', 'TNC',
    # Vận tải
    'VOS', 'MVN', 'TCL', 'VNA', 'SCS', 'VSC', 'TMS',
    # Xây dựng
    'VCG', 'FCN', 'LCG', 'C4G', 'HHV', 'VC3', 'CC1',
    # Hàng không
    'SAS', 'NCT',
    # Y tế
    'DBD', 'DCL', 'PME', 'TRA', 'OPC',
    # Bảo hiểm
    'BMI', 'BIC', 'MIG', 'PGI', 'PTI',
    # Thủy sản
    'CMX', 'FMC', 'MPC', 'ACL'
]

# Loại bỏ trùng lặp
TOP_200 = list(dict.fromkeys(TOP_200))

# TOP 250 - Đầy đủ nhất
TOP_250 = TOP_200 + [
    # Bổ sung thêm các mã còn thiếu
    'SGB', 'VBB', 'APG', 'ART', 'BMS', 'BVS', 'DSC', 'EVS', 'HBS',
    'NBB', 'NTL', 'QCG', 'HUT', 'CIG', 'CTI', 'HTN', 'SC5', 'VC7',
    'DTL', 'HMC', 'VIS', 'PGC', 'PGD', 'SJD', 'TTA', 'HVG', 'GTN',
    'FOX', 'ITD', 'ONE', 'GIL', 'TVT', 'DDV', 'BRR', 'VTO', 'PDN',
    'ROS', 'LM8', 'VCS', 'DSN', 'VTR', 'DBT', 'DHT', 'VMD', 'VNR',
    'ABT', 'BLF'
]

# Loại bỏ trùng lặp
TOP_250 = list(dict.fromkeys(TOP_250))

# ============================================================================
# DANH SÁCH THEO CHIẾN LƯỢC
# ============================================================================

# Mã tốt cho SWING TRADING (biến động, thanh khoản cao)
SWING_WATCHLIST = [
    # Chứng khoán - biến động mạnh theo thị trường
    'SSI', 'VND', 'HCM', 'VCI', 'SHS', 'MBS', 'VIX',
    # Thép - chu kỳ
    'HPG', 'HSG', 'NKG',
    # BĐS - biến động mạnh
    'VHM', 'NVL', 'KDH', 'DXG', 'DIG', 'PDR', 'KBC',
    # Ngân hàng thanh khoản cao
    'ACB', 'MBB', 'TCB', 'VPB', 'STB', 'SHB',
    # Dầu khí
    'PVD', 'PVS', 'OIL',
    # Công nghệ
    'FPT', 'CMG',
    # Bluechip thanh khoản
    'VNM', 'MWG', 'HPG', 'MSN',
    # Hàng không
    'VJC', 'HVN',
    # Điện
    'POW', 'REE', 'PC1', 'GEG',
    # Thủy sản
    'VHC', 'ANV',
    # Hóa chất
    'DGC', 'DPM', 'DCM'
]

# Mã tốt cho ĐẦU TƯ DÀI HẠN (cơ bản tốt, ổn định)
LONGTERM_WATCHLIST = [
    # Bluechip đầu ngành
    'FPT', 'VNM', 'MWG', 'PNJ', 'VCB', 'ACB', 'TCB', 'MBB',
    # Ngân hàng tốt
    'VCB', 'ACB', 'TCB', 'MBB', 'HDB', 'VIB', 'TPB',
    # Công nghệ
    'FPT', 'CMG',
    # Tiêu dùng
    'VNM', 'SAB', 'MSN', 'MWG', 'PNJ', 'KDC',
    # Y tế
    'DHG', 'DMC', 'IMP',
    # Điện
    'REE', 'PC1', 'GEG', 'NT2',
    # Dầu khí
    'GAS', 'PLX',
    # Cảng biển
    'GMD', 'HAH',
    # Khu công nghiệp
    'KBC', 'SZC', 'IJC', 'BCM',
    # Cao su
    'GVR', 'PHR',
    # Bảo hiểm
    'BVH',
    # Thủy sản
    'VHC', 'ANV'
]

# ============================================================================
# HÀM HỖ TRỢ
# ============================================================================

def get_watchlist(list_type='TOP_200'):
    """
    Lấy danh sách mã theo loại
    
    Args:
        list_type: 'VN30', 'TOP_100', 'TOP_200', 'TOP_250', 
                   'SWING', 'LONGTERM', hoặc tên ngành
    
    Returns:
        List mã cổ phiếu
    """
    lists = {
        'VN30': VN30,
        'TOP_100': TOP_100_LIQUIDITY,
        'TOP_200': TOP_200,
        'TOP_250': TOP_250,
        'SWING': SWING_WATCHLIST,
        'LONGTERM': LONGTERM_WATCHLIST,
        # Theo ngành
        'BANKS': BANKS,
        'SECURITIES': SECURITIES,
        'REAL_ESTATE': REAL_ESTATE,
        'STEEL': STEEL_MATERIALS,
        'OIL_GAS': OIL_GAS,
        'POWER': POWER,
        'FOOD': FOOD_BEVERAGE,
        'TECH': TECHNOLOGY,
        'RETAIL': RETAIL,
        'TEXTILES': TEXTILES,
        'CHEMICALS': CHEMICALS,
        'LOGISTICS': LOGISTICS,
        'CONSTRUCTION': CONSTRUCTION,
        'HEALTHCARE': HEALTHCARE,
        'SEAFOOD': SEAFOOD,
    }
    
    return lists.get(list_type.upper(), TOP_200)


def get_all_industry_symbols():
    """Lấy tất cả mã từ tất cả các ngành"""
    all_symbols = (
        BANKS + SECURITIES + REAL_ESTATE + STEEL_MATERIALS + 
        OIL_GAS + POWER + FOOD_BEVERAGE + TECHNOLOGY + RETAIL +
        TEXTILES + CHEMICALS + RUBBER + LOGISTICS + CONSTRUCTION +
        AVIATION + TOURISM + HEALTHCARE + INSURANCE + SEAFOOD
    )
    return list(dict.fromkeys(all_symbols))  # Loại trùng


# Thống kê
if __name__ == "__main__":
    print("📊 THỐNG KÊ WATCHLIST")
    print("=" * 40)
    print(f"VN30:        {len(VN30)} mã")
    print(f"TOP 100:     {len(TOP_100_LIQUIDITY)} mã")
    print(f"TOP 200:     {len(TOP_200)} mã")
    print(f"TOP 250:     {len(TOP_250)} mã")
    print(f"Swing:       {len(SWING_WATCHLIST)} mã")
    print(f"Long-term:   {len(LONGTERM_WATCHLIST)} mã")
    print("=" * 40)
    print(f"Tổng ngành:  {len(get_all_industry_symbols())} mã")
