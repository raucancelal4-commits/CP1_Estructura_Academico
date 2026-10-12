from datetime import date


# =====================================================================
# CLASE BASE: lo que los tres modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento común."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    # ---- ÚNICO MÉTODO DE CLASE DEL PROYECTO ----
    @classmethod
    def desde_diccionario(cls, datos):
        """Diccionario -> objeto. Escrito UNA vez y usado por los tres modelos.
        cls es la clase que llamó: Estudiante, Materia o Matricula."""
        datos = dict(datos)                 # copia, para no tocar el original
        id_registro = datos.pop("id")       # saco el id
        return cls(id_registro, **datos)    # el resto son los campos del modelo

    # ---- MÉTODOS DE INSTANCIA ----
    def a_diccionario(self):
        # Objeto -> diccionario. Cada hijo agrega sus campos.
        return {"id": self.id}

    def etiqueta(self):
        # POLIMORFISMO: cada hijo la reescribe a su manera
        return f"registro {self.id}"

    def __str__(self):
        # Lo que se ve al hacer print(objeto). Llama a etiqueta(),
        # así que cada modelo se imprime distinto sin cambiar esta línea.
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Estudiante
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona del sistema."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)      # el padre guarda el id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()    # {"id": ...} que arma el padre
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera."""

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        datos = super().a_diccionario()    # reutiliza lo de Persona
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        # Sobrescribe y EXTIENDE la del padre
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera or 'sin carrera'}"


# =====================================================================
# ÚNICA CLASE CON ATRIBUTOS Y MÉTODOS ESTÁTICOS
# =====================================================================
class Materia(ModeloBase):
    """Materia ES UN ModeloBase. Aquí vive todo lo estático."""

    # ATRIBUTOS ESTÁTICOS (de clase): existen una sola vez, no por objeto
    CUPOS_MAXIMOS = 30         # regla del negocio, igual para todas las materias
    NOTA_APROBACION = 14       # nota mínima para aprobar, igual para todas

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    # MÉTODO ESTÁTICO: regla que no necesita ninguna materia concreta
    @staticmethod
    def es_nota_valida(valor):
        try:
            return 0 <= float(valor) <= 20
        except (TypeError, ValueError):
            return False

    # MÉTODOS DE INSTANCIA: necesitan los datos de ESTA materia
    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        self.cupos -= 1

    def liberar_cupo(self):
        self.cupos += 1

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        return f"{self.nombre} · {self.codigo} · {self.creditos} créditos · cupos {self.cupos}"


# =====================================================================
class Matricula(ModeloBase):
    """Matrícula: un estudiante en una materia, en un periodo."""

    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=0,
                 fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        # Se calcula, no se guarda: así nunca queda desactualizado
        if self.esta_aprobada():
            return "Aprobado"
        else:
            return "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · estudiante {self.estudiante_id} · "
                f"materia {self.materia_id} · periodo {self.periodo} · "
                f"nota {self.nota} · {self.estado()}")


"""if __name__ == "__main__":
    # ---- Estudiante ----
    e = Estudiante(1, "Ana", "Pérez", "ana@mail.com", "EST2026001", "Software")
    print(e)
    print(e.a_diccionario())

    # ---- Materia ----
    m = Materia(1, "Cálculo I", "MAT101", 4, 30)
    print(m)
    print("¿Hay cupo?:", m.hay_cupo())
    m.ocupar_cupo()
    print("Después de ocupar:", m.cupos)
    m.liberar_cupo()
    print("Después de liberar:", m.cupos)
    print("¿'15' es nota válida?:", Materia.es_nota_valida("15"))
    print("¿'25' es nota válida?:", Materia.es_nota_valida("25"))
    print("¿'abc' es nota válida?:", Materia.es_nota_valida("abc"))

    # ---- Matrícula ----
    mat1 = Matricula(1, 1, 1, "2026-1", 16.5)
    mat2 = Matricula(2, 1, 1, "2026-1")          # sin nota todavía
    print(mat1)
    print(mat2)
    print("¿Aprobada?:", mat1.esta_aprobada(), "| Estado:", mat2.estado())

    # ---- Método de clase: diccionario -> objeto ----
    copia = Matricula.desde_diccionario(mat1.a_diccionario())
    print("Reconstruida:", copia)"""