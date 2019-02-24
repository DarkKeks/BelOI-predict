class Cell:
    def __init__(self, row=1, col=1, sheet=None):
        self.sheet = sheet
        self.row = row
        self.col = col

    def __str__(self):
        if self.sheet:
            return f"{self.sheet}!{Cell.idx_to_col(self.col)}{self.row}"
        return f"{Cell.idx_to_col(self.col)}{self.row}"

    def copy(self, row=None, col=None, sheet=None):
        result = Cell(self.row if not row else row,
                      self.col if not col else col,
                      self.sheet if not sheet  else sheet)
        return result

    def add(self, row=0, col=0):
        return Cell(self.row + row, self.col + col, self.sheet)

    def sub(self, row=0, col=0):
        return self.add(-row, -col)

    @staticmethod
    def idx_to_col(idx):
        result = ''
        while idx > 0:
            digit = (idx % 26)
            if digit == 0:
                result += 'Z'
                idx -= 26
            else:
                result += chr(ord('A') + digit - 1)
            idx //= 26
        return result[::-1]