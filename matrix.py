class Matrix:
    def __init__(self, List):
        self.List = List

    def display(self):
        print(self.List)

    def __add__(self, other):
        newmatrix = Matrix([])
        for i in range(len(self.List)):
            for j in range(len(self.List[0])):
                newmatrix.List.append(self.List[i][j] + other.List[i][j])
        return newmatrix

    def __sub__(self, other):
        newmatrix = Matrix([])
        for i in range(len(self.List)):
            for j in range(len(self.List[0])):
                newmatrix.List.append(self.List[i][j] - other.List[i][j])
        return newmatrix

    def __mul__(self, other):
        newmatrix = Matrix(
            [[0 for j in range(len(other.List[0]))] for i in range(len(self.List))]
        )
        for i in range(len(self.List)):
            for j in range(len(other.List[0])):
                for k in range(len(other.List)):
                    newmatrix.List[i][j] += self.List[i][k] * other.List[k][j]
        return newmatrix
