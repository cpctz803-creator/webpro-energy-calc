# ==============================================================================
# WEBプロ基準値表示 ⇒ 実績値インプット ⇒ 設備按分プログラム
# 建築設備専門アドバイザー兼秘書 Ver5.0
# ==============================================================================

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

def get_yes_no(prompt_text):
    while True:
        ans = input(prompt_text).strip().lower()
        if ans in ['y', 'yes', '1', '有', 'あり']:
            return True
        if ans in ['n', 'no', '0', '無', 'なし']:
            return False
        print("【入力エラー】『 y 』または『 n 』で入力してください。")

def main():
    print("==================================================")
    print("  WEBプロ基準値算出 ＆ 実績エネルギー按分システム ")
    print("==================================================")
    
    # 1)〜4) 基本情報の入力
    while True:
        try:
            region = int(input("■ 地域区分を入力してください (1〜8): "))
            if 1 <= region <= 8: break
            print("【入力エラー】1から8の範囲で入力してください。")
        except ValueError:
            print("【入力エラー】半角数字で入力してください。")
            
    solar_region = input("■ 日射地域区分を入力してください (例: A3、不明ならEnter): ").strip().upper()
    if not solar_region: solar_region = "未指定"

    print("\n■ 主たる建物用途の番号を選択してください:")
    for key, val in BASE_UNIT.items():
        print(f"  {key}: {val['name']}")
    while True:
        try:
            type_idx = int(input("番号を入力 (1〜8): "))
            if type_idx in BASE_UNIT: break
            print("【入力エラー】1から8の選択肢から選んでください。")
        except ValueError:
            print("【入力エラー】半角数字で入力してください。")
            
    while True:
        try:
            area = float(input("\n■ 延床面積 (m2) を入力してください: "))
            if area > 0: break
            print("【入力エラー】0より大きい数値を入力してください。")
        except ValueError:
            print("【入力エラー】半角数字で入力してください。")

    # 5)〜9) 各種設備の有無
    print("\n■ 各評価対象設備の「有無」を選択してください (y:有り / n:無し)")
    has_ac = get_yes_no("  ・空調設備はありますか？ (y/n): ")
    has_vent = get_yes_no("  ・換気設備はありますか？ (y/n): ")
    has_light = get_yes_no("  ・照明設備はありますか？ (y/n): ")
    has_wh = get_yes_no("  ・給湯設備はありますか？ (y/n): ")
    has_ev = get_yes_no("  ・エレベーター(EV)はありますか？ (y/n): ")

    # --- 計算処理①：まずWEBプロ基準値（MJ/年、GJ/年）を算出 ---
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

    # === 【変更】フェーズ1：先に基準一次エネルギー消費量の結果を表示 ===
    print("\n==================================================")
    print("【第一段階】算出された「基準一次エネルギー消費量」")
    print("==================================================")
    print(f"空調設備基準量      : {ac_base:,.1f} MJ/年  ({ac_base/1000.0:,.1f} GJ/年)")
    print(f"換気設備基準量      : {vent_base:,.1f} MJ/年  ({vent_base/1000.0:,.1f} GJ/年)")
    print(f"照明設備基準量      : {light_base:,.1f} MJ/年  ({light_base/1000.0:,.1f} GJ/年)")
    print(f"給湯設備基準量      : {wh_base:,.1f} MJ/年  ({wh_base/1000.0:,.1f} GJ/年)")
    print(f"昇降機設備基準量    : {ev_base:,.1f} MJ/年  ({ev_base/1000.0:,.1f} GJ/年)")
    print(f"その他OA機器等基準量: {other_base:,.1f} MJ/年  ({other_base/1000.0:,.1f} GJ/年)")
    print("--------------------------------------------------")
    print(f"合計基準エネルギー量: {grand_base_total_mj:,.1f} MJ/年")
    print(f"★合計（GJ換算）    : {grand_base_total_gj:,.1f} GJ/年")
    print("==================================================")

    # === 【変更】フェーズ2：結果を見てから、実績値の入力を促す ===
    print("\n上記基準値を参考に、既存建物の実際のデータを入力してください。")
    while True:
        try:
            actual_total_gj = float(input("■ 実際の年間総エネルギー消費量 (GJ/年) を入力: "))
            if actual_total_gj >= 0: break
            print("【入力エラー】0以上の数値を入力してください。")
        except ValueError:
            print("【入力エラー】半角数字で入力してください。")

    # --- 計算処理②：シェア（比率）の計算と按分 ---
    if grand_base_total_mj > 0:
        ac_share = ac_base / grand_base_total_mj
        vent_share = vent_base / grand_base_total_mj
        light_share = light_base / grand_base_total_mj
        wh_share = wh_base / grand_base_total_mj
        ev_share = ev_base / grand_base_total_mj
        other_share = other_base / grand_base_total_mj
    else:
        ac_share = vent_share = light_share = wh_share = ev_share = other_share = 0

    ac_actual_gj = actual_total_gj * ac_share
    vent_actual_gj = actual_total_gj * vent_share
    light_actual_gj = actual_total_gj * light_share
    wh_actual_gj = actual_total_gj * wh_share
    ev_actual_gj = actual_total_gj * ev_share
    other_actual_gj = actual_total_gj * other_share

    # === フェーズ3：按分した実際のエネルギー消費量をprint ===
    print("\n==================================================")
    print("【第二段階】実績値の設備別按分エネルギー消費量")
    print("==================================================")
    print(f"空調設備消費量（按分）     : {ac_actual_gj:6.1f} GJ/年  ({ac_share*100:4.1f}%)")
    print(f"換気設備消費量（按分）     : {vent_actual_gj:6.1f} GJ/年  ({vent_share*100:4.1f}%)")
    print(f"照明設備消費量（按分）     : {light_actual_gj:6.1f} GJ/年  ({light_share*100:4.1f}%)")
    print(f"給湯設備消費量（按分）     : {wh_actual_gj:6.1f} GJ/年  ({wh_share*100:4.1f}%)")
    print(f"昇降機設備消費量（按分）   : {ev_actual_gj:6.1f} GJ/年  ({ev_share*100:4.1f}%)")
    print(f"その他OA機器消費量（按分） : {other_actual_gj:6.1f} GJ/年  ({other_share*100:4.1f}%)")
    print("--------------------------------------------------")
    print(f"合計按分エネルギー消費量   : {ac_actual_gj + vent_actual_gj + light_actual_gj + wh_actual_gj + ev_actual_gj + other_actual_gj:,.1f} GJ/年")
    print("==================================================")

if __name__ == "__main__":
    main()