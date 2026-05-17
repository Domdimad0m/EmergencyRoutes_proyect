class NodoHeap:
    def __init__(self, nodo, costo):
        self.nodo = nodo
        self.costo = costo

    def esMenorQue(self, otro):
        return self.costo < otro.costo


class MinHeap:
    def __init__(self):
        self.elementos = []

    def estaVacio(self):
        return len(self.elementos) == 0

    def insertar(self, dato):
        self.elementos.append(dato)
        indiceActual = len(self.elementos) - 1

        while indiceActual > 0:
            indicePadre = (indiceActual - 1) // 2

            if self.elementos[indicePadre].esMenorQue(
                self.elementos[indiceActual]
            ):
                break

            self.elementos[indicePadre], self.elementos[indiceActual] = (
                self.elementos[indiceActual],
                self.elementos[indicePadre],
            )

            indiceActual = indicePadre

    def eliminarMinimo(self):
        if self.estaVacio():
            return None

        minimo = self.elementos[0]
        ultimo = self.elementos.pop()

        if not self.estaVacio():
            self.elementos[0] = ultimo
            self.reordenarAbajo(0)

        return minimo

    def reordenarAbajo(self, indice):
        n = len(self.elementos)

        while True:
            menor = indice
            izquierdo = 2 * indice + 1
            derecho = 2 * indice + 2

            if (
                izquierdo < n
                and self.elementos[izquierdo].esMenorQue(
                    self.elementos[menor]
                )
            ):
                menor = izquierdo

            if (
                derecho < n
                and self.elementos[derecho].esMenorQue(
                    self.elementos[menor]
                )
            ):
                menor = derecho

            if menor == indice:
                break

            self.elementos[indice], self.elementos[menor] = (
                self.elementos[menor],
                self.elementos[indice],
            )

            indice = menor


class Grafo:
    def __init__(self):
        self.origen = {}

    def getOrigen(self):
        return self.origen

    def inserta_no_dirigido(self, v1, v2, peso):
        if v1 not in self.origen:
            self.origen[v1] = {}

        if v2 not in self.origen:
            self.origen[v2] = {}

        self.origen[v1][v2] = peso
        self.origen[v2][v1] = peso

    def DFS(self):
        visitados = {}

        for v in self.origen:
            visitados[v] = False

        lista = []

        for v in self.origen:
            if not visitados[v]:
                self.__DFS(v, lista, visitados)

        return lista

    def __DFS(self, actual, lista, visitados):
        visitados[actual] = True
        lista.append(actual)

        for hijo in self.origen[actual]:
            if not visitados[hijo]:
                self.__DFS(hijo, lista, visitados)

    def BFS(self):
        visitados = {}

        for v in self.origen:
            visitados[v] = False

        lista = []

        for v in self.origen:
            if not visitados[v]:
                self.__BFS(v, lista, visitados)

        return lista

    def __BFS(self, actual, lista, visitados):
        cola = []
        cola.append(actual)
        visitados[actual] = True

        while len(cola) > 0:
            actual = cola.pop(0)
            lista.append(actual)

            for hijo in self.origen[actual]:
                if not visitados[hijo]:
                    visitados[hijo] = True
                    cola.append(hijo)


def construir_grafo_desde_rutas(rutas):
    grafo = Grafo()

    for _, ruta in rutas.iterrows():
        peso = {
            "distancia": ruta["distancia_km"],
            "trafico": ruta["factor_trafico"],
            "costo": ruta["peso"],
        }

        grafo.inserta_no_dirigido(
            ruta["origen"],
            ruta["destino"],
            peso,
        )

    return grafo