import streamlit as st
import pandas as pd

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

# 画面設定
st.set_page_config(page_title="WEBプロ基準値＆実績按分システム", layout="wide")

st.title("🏢 WEBプロ基準値算出 ＆ 実績エネルギー按分システム")
st.write("基本条件を入力して基準値を算出した後、実績値を入力することで自動的に設備別の按分を行います。")

st.markdown("---")

# 左右2カラム構造（左側に入力エリア、右側に結果表示エリア）
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.subheader("📋 1. 基本情報の入力")
    
    # 1) 地域区分の入力
    region = st.selectbox(
        "■ 地域区分 (1〜8)", 
        options=list(REGION_COEFF.keys()),
        index=5 # デフォルト: 6地域
    )
    
    # 2) 日射地域区分
    solar_region = st.text_input("■ 日射地域区分 (任意)", value="A3")

    # 3) 主たる建物用途の選択
    type_idx = st.selectbox(
        "■ 主たる建物用途",
        options=list(BASE_UNIT.keys()),
        format_func=lambda x: BASE_UNIT[x]["name"]
    )
    
    # 4) 延床面積の入力
    area = st.number_input(
        "■ 延床面積 (㎡)",
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

# --- 計算処理①：まずWEBプロ基準値を算出 ---
target_unit = BASE_UNIT[type_idx]
coeff = REGION_COEFF.get(region, 1.0)

ac_base = (target_unit["ac"] * coeff if has_ac else 0) * area
vent_base = (target_unit["vent"] if has_vent else 0) * area
light_base = (target_unit["light"] if has_light else 0) * area
wh_base = (target_unit["wh"] if has_wh else 0) * area
ev_base = (target_unit["ev"] if has_ev else 0) * area
other_base = target_unit["other"] * area

grand_base_total_mj = ac_base + vent_base + light_base + wh_base + ev_base + other_base
grand_base_total_gj = grand_base_total_mj / 1000.0

# シェア（比率）の計算
if grand_base_total_mj > 0:
    shares = {
        "空調設備": ac_base / grand_base_total_mj,
        "換気設備": vent_base / grand_base_total_mj,
        "照明設備": light_base / grand_base_total_mj,
        "給湯設備": wh_base / grand_base_total_mj,
        "昇降機設備": ev_base / grand_base_total_mj,
        "その他OA機器等": other_base / grand_base_total_mj
    }
else:
    shares = {k: 0.0 for k in ["空調設備", "換気設備", "照明設備", "給湯設備", "昇降機設備", "その他OA機器等"]}

with right_col:
    st.subheader("📊 2. 第一段階：基準一次エネルギー消費量")
    
    # テーブル表示用のデータ作成
    base_data = pd.DataFrame({
        "設備区分": list(shares.keys()),
        "基準値 (MJ/年)": [ac_base, vent_base, light_base, wh_base, ev_base, other_base],
        "基準値 (GJ/年)": [ac_base/1000, vent_base/1000, light_base/1000, wh_base/1000, ev_base/1000, other_base/1000],
        "基準シェア比率": [f"{s * 100:.1f} %" for s in shares.values()]
    })
    
    st.table(base_data.style.format({
        "基準値 (MJ/年)": "{:,.1f}",
        "基準値 (GJ/年)": "{:,.1f}"
    }))
    
    # 基準合計値の表示
    st.metric(
        label="合計基準一次エネルギー消費量",
        value=f"{grand_base_total_gj:,.1f} GJ/年",
        help=f"MJ換算: {grand_base_total_mj:,.1f} MJ/年"
    )

st.markdown("---")

# 第二段階：実績値の入力と按分結果表示
st.subheader("🎯 第二段階：既存建物の実績値入力 ＆ 按分計算")

# 実績入力フォーム
actual_total_gj = st.number_input(
    "■ 上記基準値を参考に、実際の年間総エネルギー消費量 (GJ/年) を入力してください",
    min_value=0.0,
    value=float(round(grand_base_total_gj, 1)), # 初期値として基準合計値（GJ）を自動セット
    step=10.0,
    format="%.1f"
)

# 按分計算
ac_actual_gj = actual_total_gj * shares["空調設備"]
vent_actual_gj = actual_total_gj * shares["換気設備"]
light_actual_gj = actual_total_gj * shares["照明設備"]
wh_actual_gj = actual_total_gj * shares["給湯設備"]
ev_actual_gj = actual_total_gj * shares["昇降機設備"]
other_actual_gj = actual_total_gj * shares["その他OA機器等"]
actual_total_allocated = ac_actual_gj + vent_actual_gj + light_actual_gj + wh_actual_gj + ev_actual_gj + other_actual_gj

# 結果表示
st.markdown("#### **【設備別按分エネルギー消費量 結果一覧】**")

actual_data = pd.DataFrame({
    "設備区分": list(shares.keys()),
    "按分比率": [f"{s * 100:.1f} %" for s in shares.values()],
    "基準値 (GJ/年)": [ac_base/1000, vent_base/1000, light_base/1000, wh_base/1000, ev_base/1000, other_base/1000],
    "実績按分値 (GJ/年)": [ac_actual_gj, vent_actual_gj, light_actual_gj, wh_actual_gj, ev_actual_gj, other_actual_gj]
})

# 表を画面上に表示
st.dataframe(
    actual_data.style.format({
        "基準値 (GJ/年)": "{:,.1f}",
        "実績按分値 (GJ/年)": "{:,.1f}"
    }),
    use_container_width=True,
    hide_index=True
)

# 按分後の合計確認
st.markdown(f"**合計按分エネルギー消費量**: `{actual_total_allocated:,.1f} GJ/年` （入力値: `{actual_total_gj:,.1f} GJ/年`）")

st.markdown("---")
st.caption("※本ツールは、基準設計値の比率に基づき、実績値を簡易的に按分するシステムです。実際の各設備の詳細な実計測データが存在する場合は、そちらを優先してください。")
