from audioop import cross
from math import *
from xml.etree import cElementTree
from matrix import *
from vector import *
import struct


class Bitmap:
    def __init__(self, width, height):
        self._bcBitCount = 24
        self._headerbits = 14
        self._headerbitmap = 40
        self._bcWidth = width
        self._bcHeight = height
        self._color = (45, 0, 0)
        self._bfSize = self._bcWidth * 3 * self._bcHeight
        self._dotsx = []
        self._dotsy = []
        self._texture = None
        self.active_vertex_array = []
        self.clear()
        self.View = Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    def loadModelMatrix(self, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
        translate = V3(translate[0], translate[1], translate[2])
        scale = V3(scale[0], scale[1], scale[2])
        rotate = V3(rotate[0], rotate[1], rotate[2])

        translation_matrix = Matrix(
            [
                [1, 0, 0, translate.x],
                [0, 1, 0, translate.y],
                [0, 0, 1, translate.z],
                [0, 0, 0, 1],
            ]
        )

        scale_matrix = Matrix(
            [[scale.x, 0, 0, 0], [0, scale.y, 0, 0], [0, 0, scale.z, 0], [0, 0, 0, 1]]
        )

        a = rotate.x
        rotation_x = Matrix(
            [
                [1, 0, 0, 0],
                [0, cos(a), -sin(a), 0],
                [0, sin(a), cos(a), 0],
                [0, 0, 0, 1],
            ]
        )

        a = rotate.y
        rotation_y = Matrix(
            [
                [cos(a), 0, -sin(a), 0],
                [0, 1, 0, 0],
                [sin(a), 0, cos(a), 0],
                [0, 0, 0, 1],
            ]
        )

        a = rotate.z
        rotation_z = Matrix(
            [
                [cos(a), -sin(a), 0, 0],
                [sin(a), cos(a), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        rotation_matrix = rotation_x * rotation_y * rotation_z
        self.Model = translation_matrix * rotation_matrix * scale_matrix

    def loadViewMatrix(self, x, y, z, center):
        Mi = Matrix(
            [[x.x, x.y, x.z, 0], [y.x, y.y, y.z, 0], [z.x, z.y, z.z, 0], [0, 0, 0, 1]]
        )
        OP = Matrix(
            [
                [1, 0, 0, -center.x],
                [0, 1, 0, -center.y],
                [0, 0, 1, -center.z],
                [0, 0, 0, 1],
            ]
        )

        self.View = Mi * OP

    def loadProjectionMatrix(self, coeff):
        self.Projection = Matrix(
            [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, coeff, 1]]
        )

    def loadViewport(self):
        x = 0
        y = -200
        w = self._bcWidth / 2
        h = self._bcHeight / 2

        self.Viewport = Matrix(
            [[w, 0, 0, x + w], [0, h, 0, y + h], [0, 0, 128, 128], [0, 0, 0, 1]]
        )

    def lookAt(self, eye, center, up):
        z = (eye - center).normalize()
        x = (up * z).normalize()
        y = (z * x).normalize()
        coeff = -1 / (eye.length() - center.length())

        self.loadViewMatrix(x, y, z, center)
        self.loadProjectionMatrix(coeff)
        self.loadViewport()

    def clear(self):
        self._fondo = [[self._color] * self._bcHeight for i in range(self._bcWidth)]
        self._zbuffer = [[-999999] * self._bcHeight for i in range(self._bcWidth)]

    def clearColor(self, r, g, b):
        self._color = (b, g, r)

    def Vertex(self, x, y):
        if isinstance(self._color, tuple):
            if x < 0 or y < 0 or x > self._bcWidth or y > self._bcHeight:
                # raise ValueError('Coords out of range')
                return
            if len(self._color) != 3:
                raise ValueError("Color must be a tuple of 3 elems")
            self._fondo[y - 1][x - 1] = (self._color[0], self._color[1], self._color[2])
            self._dotsx.append(x)
            self._dotsy.append(y)

        else:
            raise ValueError("Color must be a tuple of 3 elems")

    def getDotx(self):
        return self._dotsx

    def getDoty(self):
        return self._dotsy

    def Clear(self):
        self._dotsx.clear()
        self._dotsy.clear()

    def write(s, file):
        with open(file, "wb") as f:
            f.write(
                struct.pack(
                    "<hlhhl",
                    19778,
                    14 + 40 + s._bcHeight * s._bcWidth * 3,
                    0,
                    0,
                    40 + 14,
                )
            )  # Writing BITMAPFILEHEADER
            f.write(
                struct.pack(
                    "<lllhhllllll",
                    40,
                    s._bcWidth,
                    s._bcHeight,
                    1,
                    s._bcBitCount,
                    0,
                    s._bfSize,
                    0,
                    0,
                    0,
                    0,
                )
            )  # Writing BITMAPINFO
            for x in range(s._bcWidth):
                for y in range(s._bcHeight):
                    f.write(
                        struct.pack(
                            "<BBB",
                            s._fondo[x][y][0],
                            s._fondo[x][y][1],
                            s._fondo[x][y][2],
                        )
                    )

    def linea(self, A, B):

        x0 = round(A.x)
        x1 = round(B.x)
        y0 = round(A.y)
        y1 = round(B.y)

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        inclinado = dy > dx
        if inclinado:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        thres = dx
        y = y0

        for x in range(x0, x1 + 1):
            if inclinado:
                self.Vertex(y, x)
            else:
                self.Vertex(x, y)

            offset += dy * 2
            if offset >= thres:
                y += 1 if y0 < y1 else -1
                thres += dx * 2


class Obj(object):
    def __init__(self, filename):
        with open(filename) as f:
            self.lines = f.read().splitlines()
            self.tvertices = []
            self.vertices = []
            self.faces = []

            for line in self.lines:
                prefix, value = line.split(" ", 1)
                if prefix == "v":
                    self.vertices.append((list(map(float, value.split(" ")))))
                if prefix == "vt":
                    self.tvertices.append((list(map(float, value.split(" ")))))
                if prefix == "f":
                    try:
                        self.faces.append(
                            [list(map(int, face.split("/"))) for face in value.split()]
                        )
                    except:
                        continue
