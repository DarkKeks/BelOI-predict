from src.main import Platform, Column


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

    def __init__(self):
        super().__init__('score')

    def get_columns(self):
        return [ScoreColumn('score', 'GP30')]


class ScoreColumn(Column):
    formula = "=IF(ISREF({0});{0})"
    sheet = "GP30"

    def __init__(self, name, header):
        super().__init__(name, header)

    def get_value(self, user, cell):
        # awful way to reference sum column, think about better solution later
        return self.formula.format(cell.copy(col=2, sheet=self.sheet))
