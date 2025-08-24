# -*- coding: utf-8 -*-
"""
LaNi5 (Niが40サイト) のNiサイトを {Al, Sn, Zn, Ga, Si} で最大4個まで置換。
各「組成（各元素の置換数の組）」につきランダム配置を最大 N_SAMPLE 個生成し、
組成ごとに summary CSV のみを出力します。

要件:
- pymatgen が必要 (pip install pymatgen)
- CIF_PATH は置換前（Niが40ある）スーパーセルを指す
"""

import os
import random
import itertools
import json
import pandas as pd
from pymatgen.core import Structure

# ===================== ユーザ設定 =====================
CIF_PATH   = "LaNi5_2x2x2.cif"     # 置換前 CIF（Ni サイトが40個ある想定）
OUTPUT_DIR = "LaNi5_dope_50random" # 組成ごとの置換情報が保存するcsvファイルを保存するフォルダパス
N_SAMPLE   = 50                    # 各組成で生成する最大サンプル数
GLOBAL_SEED = 42                   # 乱数の固定（再現性）
# =====================================================

ELEMENTS = ["Al", "Sn", "Zn", "Ga", "Si"]
max_dope_al = 4
max_dope_sn = 4
max_dope_zn = 4
max_dope_ga = 4
max_dope_si = 4

def enumerate_substitution_cases():
    cases = []
    for al in range(max_dope_al+1):
        for sn in range(max_dope_sn+1):
            for zn in range(max_dope_zn+1):
                for ga in range(max_dope_ga+1):
                    for si in range(max_dope_si+1):
                        if al + sn + zn + ga + si <= 4:
                            comp = {"Al": al, "Sn": sn, "Zn": zn, "Ga": ga, "Si": si}
                            '''
                            if sum(comp.values()) == 0:
                                continue
                            '''
                            cases.append(comp)
    return cases

def composition_folder_name(comp):
    return "_".join([f"{el}{comp[el]}" for el in ELEMENTS])

def random_selection_for_composition(ni_indices, comp):
    """各元素ごとの置換数に従って Ni サイトをランダムに割り当てる"""
    available = list(ni_indices)
    random.shuffle(available)
    sel_map = {el: [] for el in ELEMENTS}
    ptr = 0
    for el in ELEMENTS:
        n = comp[el]
        if n <= 0:
            continue
        sel_map[el] = available[ptr:ptr+n]
        ptr += n
    return sel_map

def unique_key_from_selection(sel_map):
    return tuple((el, tuple(sorted(sel_map[el]))) for el in ELEMENTS)

def main():
    random.seed(GLOBAL_SEED)

    base_struct = Structure.from_file(CIF_PATH)
    ni_indices = [i for i, site in enumerate(base_struct) if site.specie.symbol == "Ni"]
    print(f"[INFO] CIF中のNiサイト数: {len(ni_indices)}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    compositions = enumerate_substitution_cases()
    print(f"[INFO] 組成ケース数: {len(compositions)}")

    for comp in compositions:
        folder = composition_folder_name(comp)
        out_dir = os.path.join(OUTPUT_DIR, folder)
        os.makedirs(out_dir, exist_ok=True)

        seen = set()
        records = []
        attempts = 0
        max_attempts = max(5 * N_SAMPLE, 500)

        while len(records) < N_SAMPLE and attempts < max_attempts:
            attempts += 1
            sel_map = random_selection_for_composition(ni_indices, comp)
            key = unique_key_from_selection(sel_map)
            if key in seen:
                continue
            seen.add(key)

            sample_id = len(records) + 1
            record = {
                "sample_id": sample_id,
                "n_sub_total": sum(comp.values()),
                **{f"n_{el}": comp[el] for el in ELEMENTS},
                **{f"indices_{el}": ",".join(map(str, sorted(sel_map[el]))) for el in ELEMENTS},
                "substitution_map_json": json.dumps(sel_map)
            }
            records.append(record)

        df = pd.DataFrame(records)
        csv_path = os.path.join(out_dir, f"{folder}__summary.csv")
        df.to_csv(csv_path, index=False)

        if len(records) < N_SAMPLE:
            print(f"[INFO] {folder}: {len(records)}/{N_SAMPLE} 件（ユニーク制約で頭打ち）")
        else:
            print(f"[INFO] {folder}: {len(records)} 件 生成")

    print("\n[DONE] CSV生成が完了しました。出力先:", os.path.abspath(OUTPUT_DIR))

if __name__ == "__main__":
    main()
