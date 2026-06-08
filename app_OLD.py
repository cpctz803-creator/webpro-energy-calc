import streamlit as st

# 建物用途別の標準一次エネルギー消費量原単位の定義 (単位: MJ/m2・年)
BASE_UNIT = {
    1: {"name": "1.事務所等",   "ac": 150, "vent": 40,  "light": 90,  "wh": 10,  "ev": 15,  "other": 150},
    2: {"name": "2.ホテル等",   "ac": 300, "vent": 50,  "light": 120, "wh": 400, "ev": 20,  "other": 100},
    3: {"name": "3.病院等",     "ac": 400, "vent": 80,  "light": 150, "wh": 300, "ev": 20,  "other": 200},
    4: {"name": "4.物販店舗等", "ac": 350, "vent": 50,  "light": 300, "wh": 10,  "ev": 15,  "other": 100},
    5: {"name": "5.飲食店等",   "ac": 600, "vent": 200, "light": 200, "wh": 900, "ev": 10,  "other": 150},
    6: {"name": "6.学校等",     "ac": 100, "vent": 30,  "light": 70,  "wh": 20,  "ev": 5,   "other": 50},
    7: {"name": "7.集会場等",   "ac": 250, "vent": 60,  "light": 150, "wh": 30,  "ev": 10,  "other": 60},
    8: {"name": "8.工場等",     "ac": 200, "vent": 50,  "light": 100, "wh": 20,  "ev": 10,  "other": 100}
}

# 地域区分による空調負荷補正係数
REGION_COEFF = {1: 1.6, 2: 1.4, 3: 1.3, 4: 1.2, 5: 1.1, 6: 1.0, 7: 1.0, 8: 1.5}

# Web画面のレイアウト設定
st.set_page_config(page_title="WEBプロ基準一次エネルギー消費量試算", layout="centered")

st.title("🏢 WEBプロ基準一次エネルギー消費量 試算システム")
st.write("各項目を選択・入力すると、自動的に設備毎の年間基準一次エネルギー消費量が計算されます。")

st.markdown("---")

# 2カラムレイアウト（左側に入力、右側に出力）
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("📋 基本条件・仕様入力")
    
    # 1) 地域区分の入力
    region = st.selectbox(
        "■ 地域区分を選択してください (1〜8)", 
        options=list(REGION_COEFF.keys()),
        index=5 # デフォルト: 6地域
    )
    
    # 2) 日射地域区分
    solar_region = st.text_input("■ 日射地域区分を入力してください (任意)", value="A3")

    # 3) 主たる建物用途の選択
    type_idx = st.selectbox(
        "■ 主たる建物用途を選択してください",
        options=list(BASE_UNIT.keys()),
        format_func=lambda x: BASE_UNIT[x]["name"]
    )
    
    # 4) 延床面積の入力
    area = st.number_input(
        "■ 延床面積 (㎡) を入力してください",
        min_value=0.1,
        value=1000.0,
        step=50.0,
        format="%.2f"
    )

    # 5)〜9) 各種設備の有無
    st.markdown("##### ■ 評価対象設備の有無")
    has_ac = st.checkbox("空調設備あり", value=True)
    has_vent = st.checkbox("換気設備あり", value=True)
    has_light = st.checkbox("照明設備あり", value=True)
    has_wh = st.checkbox("給湯設備あり", value=True)
    has_ev = st.checkbox("エレベーター(EV)あり", value=True)

# --- 計算処理 ---
target_unit = BASE_UNIT[type_idx]
coeff = REGION_COEFF.get(region, 1.0)

# 各設備の年間総一次エネルギー量 (MJ/年)
ac_total_mj = (target_unit["ac"] * coeff if has_ac else 0) * area
vent_total_mj = (target_unit["vent"] if has_vent else 0) * area
light_total_mj = (target_unit["light"] if has_light else 0) * area
wh_total_mj = (target_unit["wh"] if has_wh else 0) * area
ev_total_mj = (target_unit["ev"] if has_ev else 0) * area
other_total_mj = target_unit["other"] * area

# 合計
grand_total_mj = ac_total_mj + vent_total_mj + light_total_mj + wh_total_mj + ev_total_mj + other_total_mj
grand_total_gj = grand_total_mj / 1000.0

with col2:
    st.subheader("📊 計算結果（年間消費量）")
    
    st.markdown("#### **設備別一次エネルギー量 (MJ/年)**")
    
    # 各設備の結果表示（見やすさ向上のため辞書を整形して表示）
    results = {
        "空調設備": f"{ac_total_mj:,.1f} MJ/年",
        "換気設備": f"{vent_total_mj:,.1f} MJ/年",
        "照明設備": f"{light_total_mj:,.1f} MJ/年",
        "給湯設備": f"{wh_total_mj:,.1f} MJ/年",
        "昇降機設備": f"{ev_total_mj:,.1f} MJ/年",
        "その他（OA機器等）": f"{other_total_mj:,.1f} MJ/年",
    }
    
    for label, val in results.items():
        st.write(f"**{label}** : {val}")
        
    st.markdown("---")
    
    # メトリック表示（ハイライト表示）
    st.metric(
        label="合計一次エネルギー消費量 (MJ/年)",
        value=f"{grand_total_mj:,.1f} MJ/年"
    )
    
    st.metric(
        label="ギガジュール換算 (GJ/年)",
        value=f"{grand_total_gj:,.1f} GJ/年"
    )

st.markdown("---")
st.caption("※本システムはWEBプロの簡易評価基準を模した試算用です。実際の省エネ適判等で使用する公式結果とは異なる場合があります。")
