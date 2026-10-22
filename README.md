# Proyecto 1 · Práctica P1: Ingesta de datos de ITACA

## Descripción y objetivo

Pasar los XML de ITACA (alumnos, cursos, calificaciones y contenidos) a JSON en `data/raw/`, quedándonos solo con los campos necesarios y anonimizando el NIA.

## Arquitectura

```mermaid
graph LR
    A[XML de ITACA] --> B[Ingesta: XML a JSON]
    B --> C[data/raw + MongoDB]
    C --> D[ETL]
    D --> E[Dashboard]
```

## Estructura del repositorio

```
bigdata-p1-itaca/
├── data/
│   ├── exportaciones/     # XML originales
│   └── raw/               # JSON generados
├── ingesta/               # XML -> JSON
├── etl/
├── dashboard/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Puesta en marcha

```bash
cp .env.example .env           # rellena las credenciales
docker compose up -d
python ingesta/ingesta_itaca_xml.py
```

![docker compose up y ps con el contenedor bigdata-mongo en marcha](docs/docker-compose-up.png)
