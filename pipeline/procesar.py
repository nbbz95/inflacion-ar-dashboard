"""Calcula indicadores de inflación a partir de la serie mensual del INDEC."""

import pandas as pd


def a_dataframe(registros):
    df = pd.DataFrame(registros)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df.dropna(subset=["valor"]).drop_duplicates("fecha", keep="last").sort_values("fecha")
    df["mes"] = df["fecha"].dt.to_period("M")
    return df.set_index("mes")[["valor"]].rename(columns={"valor": "mensual"})


def calcular_indicadores(df):
    """Agrega interanual (últimos 12 meses compuestos) y acumulado en el año."""
    factor = 1 + df["mensual"] / 100
    df = df.copy()
    df["interanual"] = (factor.rolling(12).apply(lambda x: x.prod(), raw=True) - 1) * 100
    df["acumulado_anio"] = (factor.groupby(df.index.year).cumprod() - 1) * 100
    return df.round(2)


def resumen_anual(df):
    """Inflación de cada año calendario completo (diciembre contra diciembre)."""
    anual = df.groupby(df.index.year).agg(meses=("mensual", "size"), inflacion=("acumulado_anio", "last"))
    anual = anual[anual["meses"] == 12]
    return [{"anio": int(a), "inflacion": float(v)} for a, v in anual["inflacion"].items()]


def armar_salida(registros, desde="2017-01"):
    """Arma el JSON que consume el dashboard. Por defecto muestra desde 2017, cuando arranca el IPC nacional actual."""
    df = calcular_indicadores(a_dataframe(registros))
    ultimo = df.iloc[-1]
    serie = df[df.index >= pd.Period(desde, "M")]
    return {
        "ultimo_mes": str(df.index[-1]),
        "kpis": {
            "mensual": float(ultimo["mensual"]),
            "interanual": float(ultimo["interanual"]),
            "acumulado_anio": float(ultimo["acumulado_anio"]),
            "max_mensual": {"mes": str(serie["mensual"].idxmax()), "valor": float(serie["mensual"].max())},
        },
        "serie": [
            {
                "mes": str(m),
                "mensual": float(r.mensual),
                "interanual": None if pd.isna(r.interanual) else float(r.interanual),
                "acumulado_anio": float(r.acumulado_anio),
            }
            for m, r in serie.iterrows()
        ],
        "anual": [a for a in resumen_anual(df) if a["anio"] >= int(desde[:4])],
    }
