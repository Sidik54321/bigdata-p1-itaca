"""Ingesta de los XML exportados de ITACA.

Lee data/exportaciones/Analisis_Academico/<anyo>/*.xml y escribe en
data/raw/<anyo>/ un JSON por fichero (lista de registros) conservando solo:
    alumnos.json        -> Anyo, NIA, Curso, Turno, Grupo
    cursos.json         -> Anyo, Codigo, Nombre_Cas, Nombre_Val, Padre
    calificaciones.json -> Anyo, NIA, Curso, Modulo, Nota, Evaluacion
    contenidos.json     -> Anyo, Curso, Modulo, Nombre_Modulo

El Anyo se obtiene del atributo "curso" de la cabecera <centro> de cada XML.
El NIA se anonimiza con SHA-256 antes de escribirlo.

Uso:
    python ingesta/ingesta_itaca_xml.py
"""

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ORIGEN_DIR = DATA_DIR / "exportaciones" / "Analisis_Academico"
RAW_DIR = DATA_DIR / "raw"


def anonimizar_nia(nia: str) -> str:
    return hashlib.sha256(str(nia).encode()).hexdigest()[:10]


def limpiar(valor):
    """ITACA rellena los campos vacíos con un espacio: los convertimos a ''."""
    return (valor or "").strip()


def campos_alumno(e):
    return {
        "NIA": anonimizar_nia(limpiar(e.get("NIA"))),
        "Curso": limpiar(e.get("curso")),
        "Turno": limpiar(e.get("turno")),
        "Grupo": limpiar(e.get("grupo")),
    }


def campos_curso(e):
    return {
        "Codigo": limpiar(e.get("codigo")),
        "Nombre_Cas": limpiar(e.get("nombre_cas")),
        "Nombre_Val": limpiar(e.get("nombre_val")),
        "Padre": limpiar(e.get("padre")),
    }


def campos_calificacion(e):
    return {
        "NIA": anonimizar_nia(limpiar(e.get("alumno"))),
        "Curso": limpiar(e.get("curso")),
        "Modulo": limpiar(e.get("contenido")),
        "Nota": limpiar(e.get("nota_numerica")),
        "Evaluacion": limpiar(e.get("evaluacion")),
    }


def campos_contenido(e):
    return {
        "Curso": limpiar(e.get("curso")),
        "Modulo": limpiar(e.get("codigo")),
        "Nombre_Modulo": limpiar(e.get("nombre_cas")),
    }


# fichero -> (etiqueta de cada registro, función de campos)
TABLAS = {
    "alumnos": ("alumno", campos_alumno),
    "cursos": ("curso", campos_curso),
    "calificaciones": ("calificacion", campos_calificacion),
    "contenidos": ("contenido", campos_contenido),
}


def procesar(origen: Path, destino: Path, etiqueta: str, campos):
    centro = ET.parse(origen).getroot()
    anyo = limpiar(centro.get("curso"))

    registros = [{"Anyo": anyo, **campos(e)} for e in centro.iter(etiqueta)]

    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    return len(registros)


def main():
    for carpeta in sorted(p for p in ORIGEN_DIR.iterdir() if p.is_dir()):
        for nombre, (etiqueta, campos) in TABLAS.items():
            origen = carpeta / f"{nombre}.xml"
            if not origen.exists():
                print(f"[aviso] no existe {origen}")
                continue
            destino = RAW_DIR / carpeta.name / f"{nombre}.json"
            # en raw solo queremos JSON: borramos el XML de versiones anteriores
            destino.with_suffix(".xml").unlink(missing_ok=True)
            n = procesar(origen, destino, etiqueta, campos)
            print(f"{carpeta.name}/{nombre}.json: {n} registros")


if __name__ == "__main__":
    main()
