from dccortaramas import Bonsai

bonsai = Bonsai("pequeno_1.txt", 1, 1, [])
f_estudiante = bonsai.cargar_bonsai_de_archivo(
        carpeta="pequeno", archivo="pequeno_1.txt")
estructura_estudiante = bonsai.estructura
estructura_esperada = [
            ["1", True, False, ["2", "3"]],
            ["2", False, False, ["0", "0"]],
            ["3", True, False, ["0", "0"]]
        ]
