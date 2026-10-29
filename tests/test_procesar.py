import json
from pathlib import Path

import pytest

from pipeline.procesar import a_dataframe, armar_salida, calcular_indicadores, resumen_anual

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "inflacion.json").read_text())


def serie_constante(valor, meses, desde="2020-01"):
    import pandas as pd

    fechas = pd.period_range(desde, periods=meses, freq="M").to_timestamp(how="end")
    return [{"fecha": f.strftime("%Y-%m-%d"), "valor": valor} for f in fechas]


def test_interanual_compone_doce_meses():
    df = calcular_indicadores(a_dataframe(serie_constante(1.0, 12)))
    assert df["interanual"].iloc[-1] == pytest.approx(12.68, abs=0.01)  # 1.01^12 - 1
    assert df["interanual"].iloc[:11].isna().all()


def test_acumulado_se_reinicia_cada_anio():
    df = calcular_indicadores(a_dataframe(serie_constante(2.0, 14)))
    assert df["acumulado_anio"].iloc[12] == 2.0  # enero del segundo año


def test_resumen_anual_ignora_anios_incompletos():
    df = calcular_indicadores(a_dataframe(serie_constante(1.0, 18)))
    assert resumen_anual(df) == [{"anio": 2020, "inflacion": 12.68}]


def test_duplicados_y_nulos():
    datos = serie_constante(1.0, 3) + [{"fecha": "2020-03-31", "valor": 5.0}, {"fecha": "2020-04-30", "valor": None}]
    df = a_dataframe(datos)
    assert len(df) == 3
    assert df["mensual"].iloc[-1] == 5.0


def test_armar_salida_con_datos_reales():
    salida = armar_salida(FIXTURE, desde="2000-01")
    assert salida["ultimo_mes"] == FIXTURE[-1]["fecha"][:7]
    assert salida["kpis"]["mensual"] == FIXTURE[-1]["valor"]
    assert len(salida["serie"]) == len(FIXTURE)
    json.dumps(salida)  # tiene que ser serializable
