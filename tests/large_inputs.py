import os

from tests.utils import parse_maxflow_file_names

DAG_INPUT_EXPECTED = [
    ("tests/data/dag_edges_25.txt", 65, "dag_edges_25"),
    ("tests/data/dag_edges_50.txt", 169, "dag_edges_50"),
    ("tests/data/dag_edges_100.txt", 222, "dag_edges_100"),
    ("tests/data/dag_edges_150.txt", 264, "dag_edges_150"),
    ("tests/data/dag_edges_200.txt", 357, "dag_edges_200"),
    ("tests/data/dag_edges_250.txt", 383, "dag_edges_250"),
    ("tests/data/dag_edges_500.txt", 674, "dag_edges_500"),
]

FULLY_CONNECTED_INPUT_EXPECTED = [
    ("tests/data/fully_connected_edges_20.txt", 40, "fully_connected_edges_20"),
    ("tests/data/fully_connected_edges_210.txt", 312, "fully_connected_edges_210"),
    ("tests/data/fully_connected_edges_90.txt", 179, "fully_connected_edges_90"),
    ("tests/data/fully_connected_edges_380.txt", 462, "fully_connected_edges_380"),
    # ("tests/data/fully_connected_edges_600.txt", 10, "fully_connected_edges_600"),
]

LINE_INPUT_EXPECTED = [
    ("tests/data/line_edges_25.txt", 4, "line_edges_25"),
    ("tests/data/line_edges_50.txt", 4, "line_edges_50"),
    ("tests/data/line_edges_100.txt", 4, "line_edges_100"),
    ("tests/data/line_edges_150.txt", 4, "line_edges_150"),
    ("tests/data/line_edges_200.txt", 4, "line_edges_200"),
    ("tests/data/line_edges_250.txt", 4, "line_edges_250"),
    ("tests/data/line_edges_500.txt", 4, "line_edges_500"),
]

MAXFLOW_DAG_FILES = [
    "tests/data/maxflow/000_4_5_3.txt",
    "tests/data/maxflow/000_2_1_100000.txt",
    "tests/data/maxflow/001_2_1_0.txt",
    "tests/data/maxflow/002_4_5_3.txt",
    "tests/data/maxflow/003_498_497_328891.txt",
    "tests/data/maxflow/004_499_498_373603.txt",
    "tests/data/maxflow/005_498_497_328891.txt",
    "tests/data/maxflow/006_499_498_373603.txt",
    "tests/data/maxflow/007_499_698_38465926.txt",
    "tests/data/maxflow/008_404_805_165635950.txt",
    "tests/data/maxflow/009_404_805_165635950.txt",
    "tests/data/maxflow/009_499_698_38465926.txt",
    "tests/data/maxflow/010_479_955_67108864.txt",
    "tests/data/maxflow/010_404_805_165635950.txt",
    "tests/data/maxflow/011_404_805_165635950.txt",
    "tests/data/maxflow/011_479_955_67108864.txt",
    "tests/data/maxflow/012_481_959_111126052.txt",
    "tests/data/maxflow/012_479_955_67108864.txt",
    "tests/data/maxflow/013_479_955_67108864.txt",
    "tests/data/maxflow/013_484_965_91034320.txt",
    "tests/data/maxflow/014_487_971_145586566.txt",
    "tests/data/maxflow/014_481_959_111126052.txt",
    "tests/data/maxflow/015_488_973_111955490.txt",
    "tests/data/maxflow/015_484_965_91034320.txt",
    "tests/data/maxflow/016_487_971_145586566.txt",
    "tests/data/maxflow/016_488_973_111955490.txt",
    "tests/data/maxflow/017_490_977_67201230.txt",
    "tests/data/maxflow/017_488_973_111955490.txt",
    "tests/data/maxflow/018_498_993_114179816.txt",
    "tests/data/maxflow/018_488_973_111955490.txt",
    "tests/data/maxflow/019_490_977_67201230.txt",
    "tests/data/maxflow/019_499_995_80508994.txt",
    "tests/data/maxflow/020_500_997_68424164.txt",
    "tests/data/maxflow/020_498_993_114179816.txt",
    "tests/data/maxflow/021_499_995_80508994.txt",
    "tests/data/maxflow/022_500_997_68424164.txt",
]

MAXFLOW_NOT_DAG_FILES = [
    "tests/data/maxflow/001_468_490_1219139.txt",
    "tests/data/maxflow/002_468_490_1340991.txt",
    "tests/data/maxflow/003_468_490_1219139.txt",
    "tests/data/maxflow/004_468_490_1340991.txt",
    "tests/data/maxflow/005_492_591_28141590.txt",
    "tests/data/maxflow/006_495_594_19452032.txt",
    "tests/data/maxflow/008_495_594_19452032.txt",
    "tests/data/maxflow/022_100_2273_920680583.txt",
    "tests/data/maxflow/023_100_1700_518816803.txt",
    "tests/data/maxflow/023_413_2370_184306415.txt",
    "tests/data/maxflow/024_100_2273_920680583.txt",
    "tests/data/maxflow/025_413_2370_184306415.txt",
    "tests/data/maxflow/026_500_3824_24315761.txt",
    "tests/data/maxflow/027_324_5687_679698373.txt",
    "tests/data/maxflow/028_290_6667_953735136.txt",
    "tests/data/maxflow/030_166_7642_1823874790.txt",
    "tests/data/maxflow/031_500_8174_787664309.txt",
    "tests/data/maxflow/034_327_9020_293978834.txt",
    "tests/data/maxflow/035_500_9042_104658622.txt",
    "tests/data/maxflow/036_483_9211_351476866.txt",
    "tests/data/maxflow/037_359_9256_238314638.txt",
    "tests/data/maxflow/038_500_9363_200000000.txt",
    "tests/data/maxflow/039_304_9419_860960053.txt",
    "tests/data/maxflow/040_500_9776_117452029.txt",
    "tests/data/maxflow/041_500_9780_965640408.txt",
    "tests/data/maxflow/042_500_9790_667639572.txt",
    "tests/data/maxflow/043_500_9790_265142382.txt",
    "tests/data/maxflow/044_500_9794_1462035113.txt",
    "tests/data/maxflow/045_500_9815_1070732820.txt",
    "tests/data/maxflow/046_500_9900_854026659.txt",
    "tests/data/maxflow/047_499_9901_1027542608.txt",
    "tests/data/maxflow/048_499_9908_1262307361.txt",
]

MAXFLOW_DAG_INPUT_EXPECTED = parse_maxflow_file_names(MAXFLOW_DAG_FILES)
MAXFLOW_NOT_DAG_INPUT_EXPECTED = parse_maxflow_file_names(MAXFLOW_NOT_DAG_FILES)

WAISSI_FILES = [
    "tests/data/waissi/001_22_72_52.txt",
]

WAISSI_INPUT_EXPECTED = parse_maxflow_file_names(WAISSI_FILES)
