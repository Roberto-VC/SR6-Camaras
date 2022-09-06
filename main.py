import struct
import math
from vector import *
from gl import *
from texture import *


def bounding_box(A, B, C):
    # Mira cual es la bounding box
    xs = [A.x, B.x, C.x]
    ys = [A.y, B.y, C.y]

    xs.sort()
    ys.sort()

    return xs[0], xs[-1], ys[0], ys[-1]


def cross(V1, V2):
    # Producto cruz
    return (
        V1.y * V2.z - V1.z * V2.y,
        V1.z * V2.x - V1.x * V2.z,
        V1.x * V2.y - V1.y * V2.x,
    )


def barycentric(A, B, C, P):
    # Se calculan las baricentricas
    cx, cy, cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x), V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )

    u = cx / cz
    v = cy / cz
    w = 1 - (cx + cy) / cz

    return (w, v, u)


print()


def main():

    d = 0
    scale_factor = (0.30, 0.30, 0.30)
    # transform_factor = (600,200,0)
    # roation_factor = (0,0,pi/6)

    transform_factor = (0, 0, 0)
    roation_factor = (0, 0, 0)
    side = 1000
    Zubat = Obj("zubat.obj")
    b = Bitmap(side, side)
    t = None
    print("Bienvenido al renderizador!\n")
    while True:
        print("1. Renderizar sin textura")
        print("2. Renderizar con textura")
        g = int(input())
        if g == 2:
            t = Texture("zubat.bmp")
            b._texture = t
            break
        elif g == 1:
            break
        else:
            print("Opción  no válida")
            continue
    nombre = None
    while True:
        print("¿Como quiere que sea la foto a tomar?")
        print("1. Medium Shot\n2. Low Angle\n3. High Angle\n4. Dutch Angle")
        angle = int(input())
        if angle == 1:
            b.lookAt(V3(0, 0, 20), V3(0, 0, 0), V3(0, 10, 0))
            nombre = "Medium.bmp"
            break
        elif angle == 2:
            b.lookAt(V3(0, -10, 20), V3(0, 0, 0), V3(0, 10, 0))
            nombre = "Low.bmp"
            break
        elif angle == 3:
            b.lookAt(V3(0, 10, 20), V3(0, 0, 0), V3(0, 10, 0))
            nombre = "High.bmp"
            break
        elif angle == 4:
            roation_factor = (0, 0, pi / 6)
            scale_factor = (0.4, 0.4, 0.4)
            transform_factor = (0.25, -0.3, 0)
            b.lookAt(V3(0, 0, 20), V3(0, 0, 0), V3(0, 10, 0))
            nombre = "Dutch.bmp"
            break
        else:
            print("Opción  no válida")
            continue

    b.clearColor(200, 0, 225)

    def transform_vertex(vertex):
        # Transforma el vertice
        augmented_vertex = Matrix([[vertex[0]], [vertex[1]], [vertex[2]], [1]])
        transformed_vertex = (
            b.Viewport * b.Projection * b.View * b.Model * augmented_vertex
        )

        transformed_vertex = V3(
            transformed_vertex.List[0][0],
            transformed_vertex.List[1][0],
            transformed_vertex.List[2][0],
            transformed_vertex.List[3][0],
        )
        return V3(
            transformed_vertex.x / transformed_vertex.w,
            transformed_vertex.y / transformed_vertex.w,
            transformed_vertex.z / transformed_vertex.w,
        )

    print()

    def triangle(A, B, C, verticest=[]):

        # "Se crea la normal del triangulo para sacar la intensidad")
        L = V3(0, 0, 1)
        N = (B - A) * (C - A)

        i = N.normalize() @ L.normalize()
        if i < 0:
            return

        grey = (round(255 * i), round(255 * i), round(255 * i))
        b._color = grey
        # Escalas de grises y se crea el bounding box
        p, q, r, s = bounding_box(A, B, C)
        for x in range(round(p), round(q) + 1):
            for y in range(round(r), round(s) + 1):
                # Mira las baricentras del bounding
                try:
                    w, v, u = barycentric(A, B, C, V3(x, y))
                except:
                    continue
                if w < 0 or v < 0 or u < 0:
                    continue
                z = A.z * w + B.z * v + C.z * u
                # "Usa el z bugger para mostrar que esta adelante o atras"
                if (
                    x >= 0
                    and y >= 0
                    and x < len(b._zbuffer)
                    and y < len(b._zbuffer[0])
                    and b._zbuffer[x][y] < z
                ):
                    b._zbuffer[x][y] = z
                    # Hay un atributo vació del método en caso que no haya textura.
                    if b._texture:
                        try:
                            tx = (
                                verticest[0].x * w
                                + verticest[1].x * u
                                + verticest[2].x * v
                            )
                            ty = (
                                verticest[0].y * w
                                + verticest[1].y * u
                                + verticest[2].y * v
                            )
                            b._color = t.getColori(tx, ty, i)
                        except:
                            continue
                        # "En vez de escalas de grises, utiliza los colores de la textura")
                    # "Se pinta el punto"
                    b.Vertex(x, y)

    def load_model(zubat):
        b.loadModelMatrix(transform_factor, scale_factor, roation_factor)
        vertext = []
        vertextt = []
        d = 0
        for face in zubat.faces:
            d = d + 1
            # Mira los poligonos y cuantos veritces tiene
            if len(face) == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1

                # Se obtienen los vertices de la figura y los transforma.
                v1 = transform_vertex(zubat.vertices[f1])
                v2 = transform_vertex(zubat.vertices[f2])
                v3 = transform_vertex(zubat.vertices[f3])
                v4 = transform_vertex(zubat.vertices[f4])

                # Si hay texuta. Saca de la textura las caras y vertices respectivos
                if b._texture:
                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1
                    ft4 = face[3][1] - 1

                    vt1 = V3(
                        zubat.tvertices[ft1][0] * t.width,
                        zubat.tvertices[ft1][1] * t.height,
                    )
                    vt2 = V3(
                        zubat.tvertices[ft2][0] * t.width,
                        zubat.tvertices[ft2][1] * t.height,
                    )
                    vt3 = V3(
                        zubat.tvertices[ft3][0] * t.width,
                        zubat.tvertices[ft3][1] * t.height,
                    )
                    vt4 = V3(
                        zubat.tvertices[ft4][0] * t.width,
                        zubat.tvertices[ft4][1] * t.height,
                    )
                    vertext = [vt1, vt2, vt3]
                    vertextt = [vt1, vt4, vt3]

                # Para los los de cuatro poligonos, utiliza don traingulos
                triangle(
                    V3(v1.x, v1.y, v1.z),
                    V3(v2.x, v2.y, v2.z),
                    V3(v3.x, v3.y, v3.z),
                    vertext,
                )
                triangle(
                    V3(v1.x, v1.y, v1.z),
                    V3(v4.x, v4.y, v4.z),
                    V3(v3.x, v3.y, v3.z),
                    vertextt,
                )
            else:

                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = transform_vertex(zubat.vertices[f1])
                v2 = transform_vertex(zubat.vertices[f2])
                v3 = transform_vertex(zubat.vertices[f3])
                if b._texture:
                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1

                    vt1 = V3(
                        zubat.tvertices[ft1][0] * t.width,
                        zubat.tvertices[ft1][1] * t.height,
                    )
                    vt2 = V3(
                        zubat.tvertices[ft2][0] * t.width,
                        zubat.tvertices[ft2][1] * t.height,
                    )
                    vt3 = V3(
                        zubat.tvertices[ft3][0] * t.width,
                        zubat.tvertices[ft3][1] * t.height,
                    )
                    vertext = [vt1, vt2, vt3]

                triangle(
                    V3(v3.x, v3.y, v3.z),
                    V3(v1.x, v1.y, v1.z),
                    V3(v2.x, v2.y, v2.z),
                    vertext,
                )

    load_model(Zubat)

    b.write(nombre)


if __name__ == "__main__":
    main()
