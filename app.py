# ==============================================================================
# WEBプロ準拠 基準一次エネルギー消費量（設備別総量出力版）
# 建築設備専門アドバイザー兼秘書 Ver3.0
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
    print("  WEBプロ基準一次エネルギー消費量 試算システム  ")
    print("==================================================")
    
    # 1) 地域区分の入力
    while True:
        try:
            region = int(input("■ 地域区分を入力してください (1〜8): "))
            if 1 <= region <= 8:
                break
            print("【入力エラー】1から8の範囲で入力してください。")
        except ValueError:
            print("【入力エラー】半角数字で入力してください。")
            
    # 2) 日射地域区分の入力（記録用・そのままリターンでも可）
    solar_region = input("■ 日射地域区分を入力してください (例: A3、不明ならEnter): ").strip().upper()
    if not solar_region:
        solar_region = "未指定"

    # 3) 主たる建物用途の選択
    print("\n■ 主たる建物用途の番号を選択してください:")
    for key, val in BASE_UNIT.items():
        print(f"  {key}: {val['name']}")
    while True:
        try:
            type_idx = int(input("番号を入力 (1〜8): "))
            if type_idx in BASE_UNIT:
                break
            print("【入力エラー】1から8の選択肢から選んでください。")
        except ValueError:
            print("【入力エラー】半角数字で入力してください。")
            
    # 4) 延床面積の入力
    while True:
        try:
            area = float(input("\n■ 延床面積 (m2) を入力してください: "))
            if area > 0:
                break
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

    # --- 計算処理 ---
    target_unit = BASE_UNIT[type_idx]
    coeff = REGION_COEFF.get(region, 1.0)
    
    # 各設備の年間総一次エネルギー量 (MJ/年) = 原単位 * 補正 * 延床面積
    ac_total_mj = (target_unit["ac"] * coeff if has_ac else 0) * area
    vent_total_mj = (target_unit["vent"] if has_vent else 0) * area
    light_total_mj = (target_unit["light"] if has_light else 0) * area
    wh_total_mj = (target_unit["wh"] if has_wh else 0) * area
    ev_total_mj = (target_unit["ev"] if has_ev else 0) * area
    other_total_mj = target_unit["other"] * area  # その他（OA機器等）は必ず自動計上
    
    # 合計一次エネルギー量
    grand_total_mj = ac_total_mj + vent_total_mj + light_total_mj + wh_total_mj + ev_total_mj + other_total_mj

    # --- 変更部分：指定フォーマットでの出力表示 ---
    print("\n==================================================")
    print("【計算結果】各設備毎の年間基準一次エネルギー消費量")
    print("==================================================")
    print(f"空調設備一次エネルギー量     : {ac_total_mj:,.1f} MJ/年")
    print(f"換気設備一次エネルギー量     : {vent_total_mj:,.1f} MJ/年")
    print(f"照明設備一次エネルギー量     : {light_total_mj:,.1f} MJ/年")
    print(f"給湯設備一次エネルギー量     : {wh_total_mj:,.1f} MJ/年")
    print(f"昇降機設備一次エネルギー量   : {ev_total_mj:,.1f} MJ/年")
    print(f"その他（OA機器等）エネルギー量: {other_total_mj:,.1f} MJ/年")
    print("--------------------------------------------------")
    print(f"合計一次エネルギー消費量     : {grand_total_mj:,.1f} MJ/年")
    print(f"（ギガジュール換算           : {grand_total_mj/1000.0:,.1f} GJ/年）")
    print("==================================================")

if __name__ == "__main__":
    main()