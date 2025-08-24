from pymatgen.core import Structure

# ===== 入力 =====
CIF_LaNi5H6 = "LaNi5H6.cif"   # MPからダウンロードした CIF (H入り)
SUPERCELL = (2, 2, 2)         # スーパーセル倍率

# ===== 1. LaNi5H6 を読み込み =====
la_ni5h6 = Structure.from_file(CIF_LaNi5H6)
la_ni5h6.remove_oxidation_states()

# ===== 2. Hを削除して LaNi5 を作成 =====
la_ni5 = la_ni5h6.copy()
la_ni5.remove_species(["H"])

# ===== 3. スーパーセルを作成 =====
la_ni5_sc = la_ni5 * SUPERCELL
la_ni5h6_sc = la_ni5h6 * SUPERCELL

# ===== 4. Niサイトにインデックスを付与 =====
def relabel_sites(struct: Structure, prefix=""):
    struct = struct.copy()
    counters = {}
    for i, site in enumerate(struct):
        el = site.species_string
        if el == "Ni":
            # Niごとに通し番号を振る
            label = f"Ni_{i}"
        else:
            # 他の元素はそのまま
            if el not in counters:
                counters[el] = 0
            label = f"{el}_{counters[el]}"
            counters[el] += 1
        # propertiesにラベルを保持
        struct[i].properties["label"] = label
    return struct

la_ni5_sc_labeled   = relabel_sites(la_ni5_sc, "LaNi5")
la_ni5h6_sc_labeled = relabel_sites(la_ni5h6_sc, "LaNi5H6")

# ===== 5. CIF出力 =====
la_ni5_sc_labeled.to(fmt="cif", filename=f"LaNi5_{SUPERCELL[0]}x{SUPERCELL[1]}x{SUPERCELL[2]}_labeled.cif")
la_ni5h6_sc_labeled.to(fmt="cif", filename=f"LaNi5H6_{SUPERCELL[0]}x{SUPERCELL[1]}x{SUPERCELL[2]}_labeled.cif")

print("✅ インデックス付きスーパーセルCIFを保存しました")
