# Dashboard de inflación Argentina

Dashboard estático con la inflación de Argentina (IPC del INDEC): mensual, interanual, acumulada en el año y por año calendario. Un pipeline en Python baja los datos, calcula los indicadores y GitHub Actions lo republica todas las semanas.

**Demo:** https://nbbz95.github.io/inflacion-ar-dashboard/

## Qué calcula

| Indicador | Cómo |
|---|---|
| Mensual | Dato publicado por el INDEC |
| Interanual | Producto compuesto de los últimos 12 meses: ∏(1 + mᵢ/100) − 1 |
| Acumulado del año | Producto compuesto desde enero del año en curso |
| Anual | Acumulado a diciembre, solo para años con 12 meses |

Las tasas se componen en vez de sumarse, que es el error típico al calcular inflación acumulada.

## Arquitectura

```
GitHub Actions (cron semanal)
  → pipeline/generar.py   descarga la serie mensual
  → pipeline/procesar.py  limpia con pandas y calcula indicadores
  → site/datos.json + web/index.html (Chart.js)
  → GitHub Pages
```

## Correr localmente

```bash
pip install -r requirements.txt pytest
python -m pytest -q
python -m pipeline.generar --destino site
python -m http.server -d site 8000
```

## Stack

Python, pandas, Chart.js, GitHub Actions y GitHub Pages.

Fuente: INDEC, a través de [ArgentinaDatos](https://argentinadatos.com).
