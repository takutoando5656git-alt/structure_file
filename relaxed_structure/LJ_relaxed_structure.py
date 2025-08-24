from ase.io import read, write
from ase.optimize import BFGS, FIRE
from ase.calculators.lj import LennardJones

# CIFファイルを読み込み
atoms = read("/Users/andotakuto/Desktop/MI講習会/internship/CIF_file/LaNi5H6_2x2x2.cif")

# ASE 内蔵 LJ 計算器を付与（全元素に同じパラメータが適用される）
atoms.calc = LennardJones(epsilon=0.0103, sigma=3.40, rc=10.0)

# 原子座標を緩和
opt = FIRE(atoms, logfile="relax.log")
opt.run(fmax=0.05, steps=2000)

# 結果を保存
write("LaNi5H6_2x2x2_relaxed.cif", atoms)

