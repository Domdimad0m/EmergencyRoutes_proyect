# MaxHeap.py

"""
Max Heap para priorizar emergencias.

La estructura permite atender primero las emergencias de mayor gravedad:
ROJO > AMARILLO > VERDE.

En caso de empate en prioridad, se atiende primero la emergencia que fue insertada antes.
"""


class EmergenciaPrioridad:
    def __init__(self, emergencia, orden_llegada):
        self.emergencia = emergencia
        self.orden_llegada = orden_llegada
        self.prioridad_valor = self.convertir_prioridad(
            emergencia["prioridad"]
        )

    def convertir_prioridad(self, prioridad):
        prioridades = {
            "ROJO": 3,
            "AMARILLO": 2,
            "VERDE": 1,
        }

        return prioridades.get(prioridad, 0)

    def esMayorQue(self, otro):
        if self.prioridad_valor > otro.prioridad_valor:
            return True

        if self.prioridad_valor == otro.prioridad_valor:
            return self.orden_llegada < otro.orden_llegada

        return False


class MaxHeapEmergencias:
    def __init__(self):
        self.elementos = []
        self.contador_llegada = 0

    def estaVacio(self):
        return len(self.elementos) == 0

    def insertar(self, emergencia):
        emergencia_priorizada = EmergenciaPrioridad(
            emergencia,
            self.contador_llegada,
        )

        self.contador_llegada += 1

        self.elementos.append(emergencia_priorizada)

        indice_actual = len(self.elementos) - 1

        while indice_actual > 0:
            indice_padre = (indice_actual - 1) // 2

            if self.elementos[indice_padre].esMayorQue(
                self.elementos[indice_actual]
            ):
                break

            self.elementos[indice_padre], self.elementos[indice_actual] = (
                self.elementos[indice_actual],
                self.elementos[indice_padre],
            )

            indice_actual = indice_padre

    def extraer_maximo(self):
        if self.estaVacio():
            return None

        maximo = self.elementos[0]
        ultimo = self.elementos.pop()

        if not self.estaVacio():
            self.elementos[0] = ultimo
            self.reordenar_abajo(0)

        return maximo.emergencia

    def reordenar_abajo(self, indice):
        n = len(self.elementos)

        while True:
            mayor = indice
            izquierdo = 2 * indice + 1
            derecho = 2 * indice + 2

            if (
                izquierdo < n
                and self.elementos[izquierdo].esMayorQue(
                    self.elementos[mayor]
                )
            ):
                mayor = izquierdo

            if (
                derecho < n
                and self.elementos[derecho].esMayorQue(
                    self.elementos[mayor]
                )
            ):
                mayor = derecho

            if mayor == indice:
                break

            self.elementos[indice], self.elementos[mayor] = (
                self.elementos[mayor],
                self.elementos[indice],
            )

            indice = mayor

    def ver_siguiente(self):
        if self.estaVacio():
            return None

        return self.elementos[0].emergencia

    def tamaño(self):
        return len(self.elementos)


def construir_heap_emergencias(emergencias):
    heap = MaxHeapEmergencias()

    for _, emergencia in emergencias.iterrows():
        heap.insertar(emergencia)

    return heap


def obtener_siguiente_emergencia(emergencias):
    heap = construir_heap_emergencias(emergencias)
    return heap.extraer_maximo()
