from src.main import Platform, Column
from src.cell import Cell


class GP30:
    scores = [100, 75, 60, 50, 45,
              40, 36, 32, 29, 26,
              24, 22, 20, 18, 16,
              15, 14, 13, 12, 11,
              10, 9, 8, 7, 6,
              5, 4, 3, 2, 1]


class ScorePlatform(Platform):
    SCORE_FORMULA = "=IF(ISBLANK({0});;INDEX({1}:{2}; {0}; 1))"
    SUM_FORMULA = "=SUM({}:{})"
    AVERAGE_FORMULA = "=AVERAGE({}:{})"

    START_CELL = Cell(row=2)
    SCORE_CELL = START_CELL.add(col=1)
    AVERAGE_CELL = START_CELL.add(col=2)

    def __init__(self):
        super().__init__('score')

    def get_columns(self):
        return [
            ScoreColumn('score', 'GP30', self.SCORE_CELL),
            ScoreColumn('score_avg', 'GP30 AVG', self.AVERAGE_CELL),
        ]


class ScoreColumn(Column):
    formula = "=IF(ISREF({0});{0})"
    sheet = "GP30"

    def __init__(self, name, header, target_cell):
        super().__init__(name, header)
        self.target_cell = target_cell

    def get_values(self, users, start_cell):
        return [self.get_score_value(user, start_cell, idx) for idx, user in enumerate(users)]

    def get_score_value(self, user, cell, idx):
        return self.formula.format(self.target_cell.add(row=idx).copy(sheet=self.sheet))
