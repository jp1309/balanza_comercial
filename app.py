"""
Dashboard de Balanza Comercial del Ecuador por País
Combina datos de exportaciones (FOB) e importaciones (CIF) para visualizar
el balance comercial bilateral, composición de exportaciones e importaciones.
Datos: Banco Central del Ecuador (BCE), 2000–2025.
"""
import os
import unicodedata
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── Configuración de página ──────────────────────────────────────────
st.set_page_config(
    page_title="Balanza Comercial del Ecuador",
    page_icon="⚖️",
    layout="wide",
)

PLOT_BG = "white"
GRID_COLOR = "#f0f0f0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Diccionarios de colores ──────────────────────────────────────────

PRODUCT_COLORS = {
    "PETRÓLEO CRUDO":                          "#000000",
    "DERIVADOS DE PETRÓLEO":                   "#333333",
    "CAMARONES":                               "#e11d48",
    "BANANO":                                  "#eab308",
    "ENLATADOS DE PESCADO":                    "#0891b2",
    "CACAO":                                   "#92400e",
    "FLORES NATURALES":                        "#c026d3",
    "ORO":                                     "#ca8a04",
    "CONCENTRADO DE PLOMO Y COBRE":            "#6d28d9",
    "OTRAS MANUFACTURAS DE METALES":           "#14b8a6",
    "OTROS PRODUCTOS MINEROS":                 "#7c3aed",
    "EXTRACTOS Y ACEITES VEGETALES":           "#65a30d",
    "VEHÍCULOS Y SUS PARTES":                  "#dc2626",
    "MANUFACTURAS DE CUERO, PLÁSTICO Y CAUCHO":"#ea580c",
    "PESCADO":                                 "#0284c7",
    "JUGOS Y CONSERVAS DE FRUTAS":             "#16a34a",
    "OTRAS MADERAS":                           "#78716c",
    "ELABORADOS DE CACAO":                     "#a16207",
    "OTRAS MERCANCÍAS":                        "#64748b",
    "ELABORADOS DE BANANO":                    "#d97706",
}

# Mapa Sector para treemap exportaciones (primeros 2 dígitos de Codigo_PP)
SECTOR_MAP = {
    "11": "Prod. Primarios Agrícolas",
    "12": "Silvicultura",
    "13": "Pecuarios",
    "14": "Pesca",
    "15": "Minería y Petróleo",
    "21": "Químicos y Farmacéuticos",
    "22": "Alimentos Procesados",
    "23": "Industrializados",
    "31": "Desperdicios de Papel",
    "32": "Desperdicios de Metales",
    "33": "Otros Desperdicios",
    "41": "Animales Vivos",
    "-9": "No Definido",
}

SECTOR_COLORS = {
    # Agropecuario / Pesca → verdes
    "Prod. Primarios Agrícolas":  "#16a34a",
    "Pecuarios":                  "#4ade80",
    "Animales Vivos":             "#86efac",
    "Pesca":                      "#0891b2",   # cyan-azul (pesca = mar)
    # Madera / Silvicultura → marrón
    "Silvicultura":               "#92400e",
    # Minería / Petróleo → negro/gris oscuro
    "Minería y Petróleo":         "#000000",
    # Industria alimentaria → ámbar
    "Alimentos Procesados":       "#d97706",
    # Industrial / Manufacturas → azul
    "Industrializados":           "#1d4ed8",
    # Químicos → cyan oscuro
    "Químicos y Farmacéuticos":   "#0e7490",
    # Desperdicios → grises
    "Desperdicios de Papel":      "#9ca3af",
    "Desperdicios de Metales":    "#6b7280",
    "Otros Desperdicios":         "#d1d5db",
    # Sin clasificar
    "No Definido":                "#e5e7eb",
}

# Mapa Grupo CUODE para treemap importaciones
GRUPO_MAP = {
    "01": "Consumo No Duradero",
    "02": "Consumo Duradero",
    "03": "Combustibles y Lubricantes",
    "04": "Mat. Primas Agropecuarias",
    "05": "Mat. Primas Industriales",
    "06": "Construcción",
    "07": "Capital Agrícola",
    "08": "Capital Industrial",
    "09": "Equipo de Transporte",
    "10": "Diversos",
    "99": "Otros",
}

GRUPO_COLORS = {
    # Agropecuario → verdes (paralelo con exportaciones)
    "Mat. Primas Agropecuarias":  "#16a34a",
    "Capital Agrícola":           "#4ade80",
    # Pesca / Alimentos mar → cyan (no hay directo, pero consumo no duradero incluye alimentos)
    "Consumo No Duradero":        "#0891b2",
    # Combustibles → negro (paralelo con Minería y Petróleo)
    "Combustibles y Lubricantes": "#000000",
    # Consumo duradero → ámbar (bienes finales procesados, paralelo Alimentos Procesados)
    "Consumo Duradero":           "#d97706",
    # Capital Industrial / Mat. Primas Ind. → azules (paralelo Industrializados)
    "Capital Industrial":         "#1d4ed8",
    "Mat. Primas Industriales":   "#3b82f6",
    # Construcción → marrón (paralelo Silvicultura)
    "Construcción":               "#92400e",
    # Transporte → rojo
    "Equipo de Transporte":       "#dc2626",
    # Otros → grises
    "Diversos":                   "#9ca3af",
    "Otros":                      "#d1d5db",
}

SUBGRUPO_MAP = {
    "011": "Productos Alimenticios",
    "012": "Bebidas",
    "013": "Tabaco",
    "014": "Farmacéuticos y Tocador",
    "015": "Vestuario y Confecciones",
    "019": "Otros No Duraderos",
    "021": "Utensilios Domésticos",
    "022": "Adorno y Uso Personal",
    "023": "Muebles y Hogar",
    "024": "Electrodomésticos",
    "025": "Vehículos Particulares",
    "029": "Armas y Equipo Militar",
    "031": "Combustibles",
    "032": "Lubricantes",
    "033": "Electricidad",
    "041": "Alimentos para Animales",
    "042": "Mat. Primas Agrícolas",
    "051": "Alimentos Industriales",
    "052": "Agropecuarios no Aliment.",
    "053": "Minerales Industriales",
    "055": "Químicos y Farmacéuticos",
    "061": "Mat. de Construcción",
    "071": "Maq. y Herram. Agrícolas",
    "072": "Otro Equipo Agrícola",
    "073": "Transp. Agrícola",
    "081": "Maq. Oficina y Científicas",
    "082": "Herramientas Industriales",
    "083": "Partes de Maquinaria",
    "084": "Maquinaria Industrial",
    "085": "Otro Equipo Fijo Ind.",
    "091": "Partes de Transporte",
    "092": "Equipo Rodante",
    "093": "Equipo Fijo Transporte",
    "100": "Diversos",
    "999": "Tráfico Postal",
}

SUBGRUPO_COLORS = {
    "Productos Alimenticios":        "#16a34a",
    "Bebidas":                       "#4ade80",
    "Tabaco":                        "#854d0e",
    "Farmacéuticos y Tocador":       "#34d399",
    "Vestuario y Confecciones":      "#6ee7b7",
    "Otros No Duraderos":            "#bbf7d0",
    "Utensilios Domésticos":         "#f43f5e",
    "Adorno y Uso Personal":         "#fb7185",
    "Muebles y Hogar":               "#fda4af",
    "Electrodomésticos":             "#e11d48",
    "Vehículos Particulares":        "#9f1239",
    "Armas y Equipo Militar":        "#4c0519",
    "Combustibles":                  "#000000",
    "Lubricantes":                   "#374151",
    "Electricidad":                  "#facc15",
    "Alimentos para Animales":       "#ca8a04",
    "Mat. Primas Agrícolas":         "#fbbf24",
    "Alimentos Industriales":        "#0891b2",
    "Agropecuarios no Aliment.":     "#06b6d4",
    "Minerales Industriales":        "#164e63",
    "Químicos y Farmacéuticos":      "#0e7490",
    "Mat. de Construcción":          "#92400e",
    "Maq. y Herram. Agrícolas":      "#65a30d",
    "Otro Equipo Agrícola":          "#84cc16",
    "Transp. Agrícola":              "#a3e635",
    "Maq. Oficina y Científicas":    "#1d4ed8",
    "Herramientas Industriales":     "#2563eb",
    "Partes de Maquinaria":          "#3b82f6",
    "Maquinaria Industrial":         "#60a5fa",
    "Otro Equipo Fijo Ind.":         "#93c5fd",
    "Partes de Transporte":          "#dc2626",
    "Equipo Rodante":                "#f87171",
    "Equipo Fijo Transporte":        "#fca5a5",
    "Diversos":                      "#9ca3af",
    "Tráfico Postal":                "#d1d5db",
}

_FALLBACK_COLORS = [
    "#2563eb", "#f59e0b", "#10b981", "#8b5cf6", "#f43f5e",
    "#06b6d4", "#84cc16", "#a855f7", "#14b8a6", "#fb923c",
    "#6366f1", "#22c55e", "#e879f9", "#38bdf8", "#facc15",
]

RESTO_COLOR = "#d1d5db"


def _get_product_color(name, idx=0):
    return PRODUCT_COLORS.get(name, _FALLBACK_COLORS[idx % len(_FALLBACK_COLORS)])


def _get_subgrupo_color(name, idx=0):
    return SUBGRUPO_COLORS.get(name, _FALLBACK_COLORS[idx % len(_FALLBACK_COLORS)])


# ── Normalización y regiones ─────────────────────────────────────────

def _normalizar(s):
    """Elimina acentos y pasa a mayúsculas para comparación."""
    return "".join(
        c for c in unicodedata.normalize("NFD", str(s).upper().strip())
        if unicodedata.category(c) != "Mn"
    )

_REGION_PATTERNS = [
    ("ESTADOS UNIDOS", "América del Norte"),
    ("CANAD", "América del Norte"),
    ("MEXIC", "América del Norte"), ("MÉXIC", "América del Norte"),
    ("ALEMANI", "Europa"), ("ESPAÑ", "Europa"), ("FRANCI", "Europa"),
    ("ITALI", "Europa"), ("HOLANDA", "Europa"), ("PAÍSES BAJOS", "Europa"),
    ("REINO UNIDO", "Europa"), ("BÉLGI", "Europa"), ("BELGI", "Europa"), ("BELG", "Europa"),
    ("RUSI", "Europa"), ("SUIZ", "Europa"), ("PORTUG", "Europa"),
    ("SUECI", "Europa"), ("POLONI", "Europa"), ("GRECI", "Europa"),
    ("TURQU", "Europa"), ("UCRANI", "Europa"), ("NORUEG", "Europa"),
    ("DINAMARC", "Europa"), ("FINLANDI", "Europa"), ("IRLAND", "Europa"),
    ("RUMANI", "Europa"), ("AUSTRI", "Europa"), ("CHECA", "Europa"),
    ("BULGARI", "Europa"), ("ESLOVENI", "Europa"), ("LITUANI", "Europa"),
    ("CROACI", "Europa"), ("MONTENEGR", "Europa"), ("ESTONI", "Europa"),
    ("ALBANI", "Europa"), ("SERBI", "Europa"), ("MALT", "Europa"),
    ("LETONI", "Europa"), ("ESLOVAQU", "Europa"), ("HUNGR", "Europa"),
    ("MACEDONI", "Europa"), ("BOSNIA", "Europa"), ("LUXEMBURG", "Europa"),
    ("ISLANDI", "Europa"), ("LIECHTENSTEIN", "Europa"), ("ANDORR", "Europa"),
    ("SAN MARINO", "Europa"), ("MONACO", "Europa"), ("GIBRALTAR", "Europa"),
    ("SANTA SEDE", "Europa"), ("VATICANO", "Europa"), ("BELAR", "Europa"),
    ("MOLDOV", "Europa"), ("GEORGI", "Europa"), ("CHIPRE", "Europa"),
    ("CHINA", "Asia"), ("JAPON", "Asia"), ("JAPÓN", "Asia"),
    ("COREA", "Asia"), ("INDIA", "Asia"), ("INDONESI", "Asia"),
    ("TAILANDI", "Asia"), ("VIETNAM", "Asia"), ("MALASI", "Asia"),
    ("FILIPIN", "Asia"), ("TAIW", "Asia"), ("SINGAPUR", "Asia"),
    ("HONG KONG", "Asia"), ("MACAO", "Asia"), ("PAKIST", "Asia"),
    ("BANGLADESH", "Asia"), ("SRI LANKA", "Asia"), ("CAMBOYA", "Asia"),
    ("MYANMAR", "Asia"), ("BRUNEI", "Asia"), ("LAOS", "Asia"),
    ("MONGOLI", "Asia"), ("NEPAL", "Asia"), ("MALDIV", "Asia"),
    ("KAZAJIST", "Asia"), ("UZBEKIST", "Asia"), ("TAYIKIST", "Asia"),
    ("TURKMENIST", "Asia"), ("AZERBAIY", "Asia"), ("ARMENI", "Asia"),
    ("KIRGUIST", "Asia"), ("AFGANIST", "Asia"),
    ("ARABIA SAUDITA", "Medio Oriente"), ("EMIRATOS", "Medio Oriente"),
    ("ISRAEL", "Medio Oriente"), ("IRAN", "Medio Oriente"), ("IRÁN", "Medio Oriente"),
    ("IRAK", "Medio Oriente"), ("KUWAIT", "Medio Oriente"),
    ("QATAR", "Medio Oriente"), ("OMAN", "Medio Oriente"), ("OMÁN", "Medio Oriente"),
    ("BAHREIN", "Medio Oriente"), ("JORDANI", "Medio Oriente"),
    ("LIBANO", "Medio Oriente"), ("LÍBANO", "Medio Oriente"),
    ("SIRIA", "Medio Oriente"), ("YEMEN", "Medio Oriente"), ("PALESTIN", "Medio Oriente"),
    ("AUSTRALIA", "Oceanía"), ("NUEVA ZELAND", "Oceanía"),
    ("PAPUA", "Oceanía"), ("FIJI", "Oceanía"), ("SAMOA", "Oceanía"),
    ("POLINESIA", "Oceanía"), ("NUEVA CALEDONI", "Oceanía"),
    ("GUAM", "Oceanía"), ("MARIANAS", "Oceanía"),
    ("SUDAFRICA", "África"), ("SUDÁFRICA", "África"),
    ("EGIPTO", "África"), ("NIGERIA", "África"), ("MARRUECOS", "África"),
    ("KENYA", "África"), ("KENIA", "África"), ("GHANA", "África"),
    ("ARGELIA", "África"), ("COSTA DE MARFIL", "África"),
    ("LIBIA", "África"), ("TUNEZ", "África"), ("TÚNEZ", "África"),
    ("SENEGAL", "África"), ("CAMERUN", "África"), ("CAMERÚN", "África"),
    ("GUINEA", "África"), ("MADAGASCAR", "África"), ("ETIOP", "África"),
    ("MOZAMBIQUE", "África"), ("ANGOLA", "África"), ("TOGO", "África"),
    ("BENIN", "África"), ("BENÍN", "África"), ("CONGO", "África"),
    ("GABON", "África"), ("GABÓN", "África"), ("MAURICIO", "África"),
    ("MAURITANI", "África"), ("NAMIBIA", "África"), ("SUDAN", "África"),
    ("LIBERIA", "África"), ("UGANDA", "África"), ("TANZAN", "África"),
    ("RWANDA", "África"), ("BURUNDI", "África"), ("BURKINA", "África"),
    ("MALI", "África"), ("MALÍ", "África"), ("NIGER", "África"), ("NÍGER", "África"),
    ("CHAD", "África"), ("GAMBIA", "África"), ("DJIBOUTI", "África"),
    # América Latina
    ("COLOMBIA", "América Latina"), ("PERU", "América Latina"), ("PERÚ", "América Latina"),
    ("CHILE", "América Latina"), ("ARGENTINA", "América Latina"),
    ("BRASIL", "América Latina"), ("VENEZUEL", "América Latina"),
    ("ECUADOR", "América Latina"), ("BOLIVI", "América Latina"),
    ("PARAGUA", "América Latina"), ("URUGUA", "América Latina"),
    ("GUATEMAL", "América Latina"), ("HONDUR", "América Latina"),
    ("EL SALVADOR", "América Latina"), ("NICARAG", "América Latina"),
    ("COSTA RICA", "América Latina"), ("PANAM", "América Latina"),
    ("CUBA", "América Latina"), ("HAITI", "América Latina"), ("HAITÍ", "América Latina"),
    ("REP. DOMINICAN", "América Latina"), ("DOMINICAN", "América Latina"),
    ("PUERTO RICO", "América Latina"), ("JAMAICA", "América Latina"),
    ("TRINIDAD", "América Latina"), ("BARBADOS", "América Latina"),
    ("GUYANA", "América Latina"), ("SURINAM", "América Latina"),
    ("BELIZE", "América Latina"), ("BELICE", "América Latina"),
    ("ANTILLAS", "América Latina"), ("ARUBA", "América Latina"),
    ("CURAZAO", "América Latina"), ("BAHAMAS", "América Latina"),
]

REGION_ORDER = [
    "América Latina", "América del Norte", "Europa",
    "Asia", "Medio Oriente", "África", "Oceanía", "Otros",
]

def _asignar_region(pais: str) -> str:
    p = _normalizar(pais)
    for patron, region in _REGION_PATTERNS:
        if _normalizar(patron) in p:
            return region
    return "Otros"


# ── Carga de datos ──────────────────────────────────────────────────

@st.cache_data
def load_export_data():
    path = os.path.join(BASE_DIR, "data", "exportaciones_ecuador.parquet")
    cols = ["Anio", "Pais_Destino", "Codigo_PP", "PP", "FOB", "TM_Peso_Neto"]
    df = pd.read_parquet(path, columns=cols)
    agg = (df.groupby(["Anio", "Pais_Destino", "Codigo_PP", "PP"], observed=True)
             .agg(FOB=("FOB", "sum"), TM=("TM_Peso_Neto", "sum"))
             .reset_index())
    agg["FOB"] = agg["FOB"] / 1000  # miles → millones USD
    agg["Codigo_PP"] = agg["Codigo_PP"].astype(str)
    agg["Cod_Sector"] = agg["Codigo_PP"].str[:2]
    agg["Sector"] = agg["Cod_Sector"].map(SECTOR_MAP).fillna("No Definido")
    agg["Pais_Norm"] = agg["Pais_Destino"].apply(_normalizar)
    agg["Region"] = agg["Pais_Destino"].apply(_asignar_region)
    return agg


@st.cache_data
def load_import_data():
    path = os.path.join(BASE_DIR, "data", "importaciones_ecuador.parquet")
    cols = ["Anio", "Pais_Origen", "Cod_Grupo", "Cod_Subgrupo", "CIF"]
    df = pd.read_parquet(path, columns=cols)
    # Agregar ANTES de convertir Categorical → str (CRÍTICO: 6.7M filas Categorical)
    agg = (df.groupby(["Anio", "Pais_Origen", "Cod_Grupo", "Cod_Subgrupo"], observed=True)
             .agg(CIF=("CIF", "sum"))
             .reset_index())
    # Post-groupby: seguro convertir (~55K filas)
    agg["Pais_Origen"]  = agg["Pais_Origen"].astype(str).str.strip()
    agg["Cod_Grupo"]    = agg["Cod_Grupo"].astype(str)
    agg["Cod_Subgrupo"] = agg["Cod_Subgrupo"].astype(str)
    agg["Grupo"]    = agg["Cod_Grupo"].map(GRUPO_MAP).fillna("Otros")
    agg["Subgrupo"] = agg["Cod_Subgrupo"].map(SUBGRUPO_MAP).fillna("Otros")
    agg["CIF"] = agg["CIF"] / 1000  # miles → millones USD
    agg["Pais_Norm"] = agg["Pais_Origen"].apply(_normalizar)
    agg["Region"] = agg["Pais_Origen"].apply(_asignar_region)
    return agg


@st.cache_data
def build_country_list(_df_exp, _df_imp):
    """Construye lista unificada de países con su región, prefiriendo nombre de exportaciones."""
    exp_map = {_normalizar(c): c for c in _df_exp["Pais_Destino"].unique()}
    imp_map = {_normalizar(c): c for c in _df_imp["Pais_Origen"].unique()}
    all_norm = sorted(set(exp_map.keys()) | set(imp_map.keys()))
    # display_name → (norm_key, region)
    result = {}
    for n in all_norm:
        display = exp_map.get(n, imp_map.get(n, n))
        region = _asignar_region(display)
        result[display] = (n, region)
    return result


# ── Cargar datos ─────────────────────────────────────────────────────

df_exp = load_export_data()
df_imp = load_import_data()
country_map = build_country_list(df_exp, df_imp)

# ── Sidebar — filtros ────────────────────────────────────────────────

anio_min = min(int(df_exp["Anio"].min()), int(df_imp["Anio"].min()))
anio_max = max(int(df_exp["Anio"].max()), int(df_imp["Anio"].max()))

st.sidebar.title("Filtros")

# Región
regiones_disponibles = sorted(
    {v[1] for v in country_map.values()},
    key=lambda r: REGION_ORDER.index(r) if r in REGION_ORDER else 99,
)
region_sel = st.sidebar.selectbox(
    "Región", ["Todas"] + regiones_disponibles
)

# Período
st.sidebar.markdown("**Período de análisis**")
col_desde, col_hasta = st.sidebar.columns(2)
anio_desde = col_desde.number_input(
    "Desde", min_value=anio_min, max_value=anio_max, value=anio_min, step=1
)
anio_hasta = col_hasta.number_input(
    "Hasta", min_value=anio_min, max_value=anio_max, value=anio_max, step=1
)
if anio_desde > anio_hasta:
    anio_desde, anio_hasta = anio_hasta, anio_desde
rango = (int(anio_desde), int(anio_hasta))

# ── Selector de país — área principal (filtrado por región) ───────────

TODOS_LABEL = "— Todos —"

if region_sel == "Todas":
    country_list = sorted(country_map.keys())
    default_pais = "ESTADOS UNIDOS"
    if default_pais not in country_list:
        default_pais = country_list[0] if country_list else ""
    default_idx = country_list.index(default_pais) if default_pais in country_list else 0
else:
    paises_region = sorted(
        [name for name, (_, reg) in country_map.items() if reg == region_sel]
    )
    country_list = [TODOS_LABEL] + paises_region
    default_idx = 0  # "— Todos —" seleccionado por defecto al cambiar región

st.markdown("### Selecciona un país socio comercial")
pais_sel = st.selectbox(
    "País",
    country_list,
    index=default_idx,
    label_visibility="collapsed",
)

modo_region = (pais_sel == TODOS_LABEL)

# ── Filtrar por país (o región completa) y rango ──────────────────────

if modo_region:
    # Agrega todos los países de la región seleccionada
    paises_en_region = {name for name, (_, reg) in country_map.items() if reg == region_sel}
    norm_keys_region = {v[0] for name, v in country_map.items() if name in paises_en_region}
    df_exp_pais = df_exp[
        (df_exp["Pais_Norm"].isin(norm_keys_region)) &
        (df_exp["Anio"] >= rango[0]) & (df_exp["Anio"] <= rango[1])
    ]
    df_imp_pais = df_imp[
        (df_imp["Pais_Norm"].isin(norm_keys_region)) &
        (df_imp["Anio"] >= rango[0]) & (df_imp["Anio"] <= rango[1])
    ]
    titulo_pais = f"{region_sel} (todos los países)"
else:
    norm_key, _ = country_map[pais_sel]
    df_exp_pais = df_exp[
        (df_exp["Pais_Norm"] == norm_key) &
        (df_exp["Anio"] >= rango[0]) & (df_exp["Anio"] <= rango[1])
    ]
    df_imp_pais = df_imp[
        (df_imp["Pais_Norm"] == norm_key) &
        (df_imp["Anio"] >= rango[0]) & (df_imp["Anio"] <= rango[1])
    ]
    titulo_pais = pais_sel

# ── Título ───────────────────────────────────────────────────────────

# Etiqueta corta reutilizable en los títulos de cada gráfico
ctx_label = f"{titulo_pais}  ·  {rango[0]}–{rango[1]}"

st.title(f"Balanza Comercial de Ecuador con {titulo_pais}")
st.caption(f"{rango[0]}–{rango[1]}  |  Exportaciones FOB vs Importaciones CIF, millones USD")

# ── KPIs ─────────────────────────────────────────────────────────────

exp_total = df_exp_pais["FOB"].sum()
imp_total = df_imp_pais["CIF"].sum()
saldo = exp_total - imp_total

ultimo_anio = rango[1]
exp_ult  = df_exp_pais[df_exp_pais["Anio"] == ultimo_anio]["FOB"].sum()
imp_ult  = df_imp_pais[df_imp_pais["Anio"] == ultimo_anio]["CIF"].sum()
exp_prev = df_exp_pais[df_exp_pais["Anio"] == ultimo_anio - 1]["FOB"].sum()
imp_prev = df_imp_pais[df_imp_pais["Anio"] == ultimo_anio - 1]["CIF"].sum()
delta_exp = ((exp_ult / exp_prev - 1) * 100) if exp_prev > 0 else None
delta_imp = ((imp_ult / imp_prev - 1) * 100) if imp_prev > 0 else None

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Exportaciones FOB", f"${exp_total:,.1f} M")
k2.metric("Importaciones CIF", f"${imp_total:,.1f} M")
k3.metric("Saldo Comercial", f"${saldo:,.1f} M",
          delta=f"{'Superávit' if saldo >= 0 else 'Déficit'}",
          delta_color="normal" if saldo >= 0 else "inverse")
k4.metric(f"Exp. {ultimo_anio}", f"${exp_ult:,.1f} M",
          delta=f"{delta_exp:+.1f}%" if delta_exp is not None else "—")
k5.metric(f"Imp. {ultimo_anio}", f"${imp_ult:,.1f} M",
          delta=f"{delta_imp:+.1f}%" if delta_imp is not None else "—",
          delta_color="inverse")

st.divider()

# ══════════════════════════════════════════════════════════════════════
# 1. Balanza Comercial Anual
# ══════════════════════════════════════════════════════════════════════

st.subheader("1. Balanza Comercial Anual")

exp_anual = df_exp_pais.groupby("Anio")["FOB"].sum().reset_index()
imp_anual = df_imp_pais.groupby("Anio")["CIF"].sum().reset_index()
# Usar todos los años del rango, rellenar con 0 si no hay datos
all_years = pd.DataFrame({"Anio": range(rango[0], rango[1] + 1)})
balance = (all_years
           .merge(exp_anual, on="Anio", how="left")
           .merge(imp_anual, on="Anio", how="left")
           .fillna(0))
balance["Saldo"] = balance["FOB"] - balance["CIF"]

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    x=balance["Anio"], y=balance["FOB"],
    name="Exportaciones FOB", marker_color="#2563eb",
    hovertemplate="Exp: $%{y:,.1f} M<extra></extra>",
))
fig1.add_trace(go.Bar(
    x=balance["Anio"], y=balance["CIF"],
    name="Importaciones CIF", marker_color="#dc2626",
    hovertemplate="Imp: $%{y:,.1f} M<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=balance["Anio"], y=balance["Saldo"],
    name="Saldo", mode="lines+markers",
    line=dict(color="#000000", width=2, dash="dot"),
    marker=dict(size=5),
    hovertemplate="Saldo: $%{y:,.1f} M<extra></extra>",
))
fig1.add_hline(y=0, line_dash="dash", line_color="#888", line_width=1)
fig1.update_layout(
    title=dict(text=f"Balanza Comercial Anual  ·  {ctx_label}", font=dict(size=13), x=0),
    barmode="group", height=420, plot_bgcolor=PLOT_BG,
    yaxis=dict(title="Millones USD", tickformat=",.1f", gridcolor=GRID_COLOR),
    xaxis=dict(
        title="",
        range=[rango[0] - 0.5, rango[1] + 0.5],
        dtick=1 if (rango[1] - rango[0]) <= 15 else 2,
        tickformat="d",
    ),
    legend=dict(orientation="h", y=-0.15),
    margin=dict(t=50, b=60),
    hovermode="x unified",
)
st.plotly_chart(fig1, width="stretch")

st.divider()

# ══════════════════════════════════════════════════════════════════════
# 2. ¿Qué le exportamos? — Composición por Producto Principal
# ══════════════════════════════════════════════════════════════════════

st.subheader("2. ¿Qué le exportamos?")

if df_exp_pais.empty:
    st.info("No hay exportaciones registradas hacia este destino en el período seleccionado.")
else:
    prod_total = (df_exp_pais.groupby("PP")["FOB"].sum()
                  .sort_values(ascending=False).reset_index())
    top8 = prod_total.head(10)["PP"].tolist()
    n_resto_exp = prod_total[~prod_total["PP"].isin(top8)].shape[0]
    all_years_exp = pd.DataFrame({"Anio": range(rango[0], rango[1] + 1)})

    exp_pivot = df_exp_pais.copy()
    exp_pivot["PP_grupo"] = exp_pivot["PP"].where(exp_pivot["PP"].isin(top8), "RESTO")
    exp_area = exp_pivot.groupby(["Anio", "PP_grupo"])["FOB"].sum().reset_index()
    exp_area_total = exp_area.groupby("Anio")["FOB"].sum().rename("Total")
    exp_area = exp_area.merge(exp_area_total, on="Anio")
    exp_area["Pct"] = (exp_area["FOB"] / exp_area["Total"].replace(0, 1) * 100).round(1)

    _xaxis_exp = dict(
        range=[rango[0] - 0.5, rango[1] + 0.5],
        dtick=2 if (rango[1] - rango[0]) > 10 else 1,
        tickformat="d",
    )

    col_exp_val, col_exp_pct = st.columns(2)

    # -- Gráfico USD (líneas) --
    with col_exp_val:
        st.caption("Evolución en millones USD (FOB)")
        fig2a = go.Figure()
        for i, prod in enumerate(top8):
            sub = all_years_exp.merge(
                exp_area[exp_area["PP_grupo"] == prod].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            color = _get_product_color(prod, i)
            fig2a.add_trace(go.Scatter(
                x=sub["Anio"], y=sub["FOB"], name=prod,
                mode="lines", line=dict(width=2, color=color),
                hovertemplate=f"<b>{prod}</b><br>$%{{y:,.1f}} M<extra></extra>",
            ))
        if n_resto_exp > 0:
            sub_r = all_years_exp.merge(
                exp_area[exp_area["PP_grupo"] == "RESTO"].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            fig2a.add_trace(go.Scatter(
                x=sub_r["Anio"], y=sub_r["FOB"],
                name=f"RESTO ({n_resto_exp})", mode="lines",
                line=dict(width=2, color=RESTO_COLOR),
                hovertemplate="<b>RESTO</b><br>$%{y:,.1f} M<extra></extra>",
            ))
        fig2a.update_layout(
            title=dict(text=f"Exportaciones FOB  ·  {ctx_label}", font=dict(size=12), x=0),
            height=400, plot_bgcolor=PLOT_BG, xaxis=_xaxis_exp,
            yaxis=dict(title="FOB (millones USD)", tickformat=",.1f", gridcolor=GRID_COLOR),
            legend=dict(orientation="h", y=-0.28, font=dict(size=9)),
            margin=dict(t=45, b=90), hovermode="x unified",
        )
        st.plotly_chart(fig2a, width="stretch")

    # -- Gráfico % (stacked area, traces en orden inverso para que mayor quede arriba) --
    with col_exp_pct:
        st.caption("Participación % anual")
        fig2b = go.Figure()
        # Agregar RESTO primero (fondo), luego top8 de menor a mayor
        if n_resto_exp > 0:
            sub_r = all_years_exp.merge(
                exp_area[exp_area["PP_grupo"] == "RESTO"].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            fig2b.add_trace(go.Scatter(
                x=sub_r["Anio"], y=sub_r["Pct"],
                name=f"RESTO ({n_resto_exp})", stackgroup="one", mode="lines",
                line=dict(width=0.5, color=RESTO_COLOR), fillcolor=RESTO_COLOR,
                showlegend=False,
                hovertemplate="<b>RESTO</b><br>%{y:.1f}%<extra></extra>",
            ))
        for i, prod in enumerate(reversed(top8)):
            orig_i = len(top8) - 1 - i
            sub = all_years_exp.merge(
                exp_area[exp_area["PP_grupo"] == prod].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            color = _get_product_color(prod, orig_i)
            fig2b.add_trace(go.Scatter(
                x=sub["Anio"], y=sub["Pct"], name=prod,
                stackgroup="one", mode="lines",
                line=dict(width=0.5, color=color), fillcolor=color,
                showlegend=False,
                hovertemplate=f"<b>{prod}</b><br>%{{y:.1f}}%<extra></extra>",
            ))
        fig2b.update_layout(
            title=dict(text=f"Participación % por Producto  ·  {ctx_label}", font=dict(size=12), x=0),
            height=400, plot_bgcolor=PLOT_BG, xaxis=_xaxis_exp,
            yaxis=dict(title="Participación (%)", tickformat=".0f", ticksuffix="%",
                       range=[0, 100], dtick=10, gridcolor=GRID_COLOR),
            margin=dict(t=45, b=90), hovermode="x unified",
        )
        st.plotly_chart(fig2b, width="stretch")

st.divider()

# ══════════════════════════════════════════════════════════════════════
# 3. ¿Qué le importamos? — Composición por Subgrupo CUODE
# ══════════════════════════════════════════════════════════════════════

st.subheader("3. ¿Qué le importamos?")

if df_imp_pais.empty:
    st.info("No hay importaciones registradas desde este origen en el período seleccionado.")
else:
    sub_total = (df_imp_pais.groupby("Subgrupo")["CIF"].sum()
                 .sort_values(ascending=False).reset_index())
    top8s = sub_total.head(10)["Subgrupo"].tolist()
    n_resto_imp = sub_total[~sub_total["Subgrupo"].isin(top8s)].shape[0]
    all_years_imp = pd.DataFrame({"Anio": range(rango[0], rango[1] + 1)})

    imp_pivot = df_imp_pais.copy()
    imp_pivot["Sub_grupo"] = imp_pivot["Subgrupo"].where(
        imp_pivot["Subgrupo"].isin(top8s), "RESTO")
    imp_area = imp_pivot.groupby(["Anio", "Sub_grupo"])["CIF"].sum().reset_index()
    imp_area_total = imp_area.groupby("Anio")["CIF"].sum().rename("Total")
    imp_area = imp_area.merge(imp_area_total, on="Anio")
    imp_area["Pct"] = (imp_area["CIF"] / imp_area["Total"].replace(0, 1) * 100).round(1)

    _xaxis_imp = dict(
        range=[rango[0] - 0.5, rango[1] + 0.5],
        dtick=2 if (rango[1] - rango[0]) > 10 else 1,
        tickformat="d",
    )

    col_imp_val, col_imp_pct = st.columns(2)

    # -- Gráfico USD (líneas) --
    with col_imp_val:
        st.caption("Evolución en millones USD (CIF)")
        fig3a = go.Figure()
        for i, sub in enumerate(top8s):
            d = all_years_imp.merge(
                imp_area[imp_area["Sub_grupo"] == sub].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            color = _get_subgrupo_color(sub, i)
            fig3a.add_trace(go.Scatter(
                x=d["Anio"], y=d["CIF"], name=sub,
                mode="lines", line=dict(width=2, color=color),
                hovertemplate=f"<b>{sub}</b><br>$%{{y:,.1f}} M<extra></extra>",
            ))
        if n_resto_imp > 0:
            sub_r_imp = all_years_imp.merge(
                imp_area[imp_area["Sub_grupo"] == "RESTO"].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            fig3a.add_trace(go.Scatter(
                x=sub_r_imp["Anio"], y=sub_r_imp["CIF"],
                name=f"RESTO ({n_resto_imp})", mode="lines",
                line=dict(width=2, color=RESTO_COLOR),
                hovertemplate="<b>RESTO</b><br>$%{y:,.1f} M<extra></extra>",
            ))
        fig3a.update_layout(
            title=dict(text=f"Importaciones CIF  ·  {ctx_label}", font=dict(size=12), x=0),
            height=400, plot_bgcolor=PLOT_BG, xaxis=_xaxis_imp,
            yaxis=dict(title="CIF (millones USD)", tickformat=",.1f", gridcolor=GRID_COLOR),
            legend=dict(orientation="h", y=-0.28, font=dict(size=9)),
            margin=dict(t=45, b=90), hovermode="x unified",
        )
        st.plotly_chart(fig3a, width="stretch")

    # -- Gráfico % (stacked area, traces en orden inverso para que mayor quede arriba) --
    with col_imp_pct:
        st.caption("Participación % anual")
        fig3b = go.Figure()
        # Agregar RESTO primero (fondo), luego top8s de menor a mayor
        if n_resto_imp > 0:
            sub_r_imp = all_years_imp.merge(
                imp_area[imp_area["Sub_grupo"] == "RESTO"].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            fig3b.add_trace(go.Scatter(
                x=sub_r_imp["Anio"], y=sub_r_imp["Pct"],
                name=f"RESTO ({n_resto_imp})", stackgroup="one", mode="lines",
                line=dict(width=0.5, color=RESTO_COLOR), fillcolor=RESTO_COLOR,
                showlegend=False,
                hovertemplate="<b>RESTO</b><br>%{y:.1f}%<extra></extra>",
            ))
        for i, sub in enumerate(reversed(top8s)):
            orig_i = len(top8s) - 1 - i
            d = all_years_imp.merge(
                imp_area[imp_area["Sub_grupo"] == sub].sort_values("Anio"),
                on="Anio", how="left").fillna(0)
            color = _get_subgrupo_color(sub, orig_i)
            fig3b.add_trace(go.Scatter(
                x=d["Anio"], y=d["Pct"], name=sub,
                stackgroup="one", mode="lines",
                line=dict(width=0.5, color=color), fillcolor=color,
                showlegend=False,
                hovertemplate=f"<b>{sub}</b><br>%{{y:.1f}}%<extra></extra>",
            ))
        fig3b.update_layout(
            title=dict(text=f"Participación % por Subgrupo  ·  {ctx_label}", font=dict(size=12), x=0),
            height=400, plot_bgcolor=PLOT_BG, xaxis=_xaxis_imp,
            yaxis=dict(title="Participación (%)", tickformat=".0f", ticksuffix="%",
                       range=[0, 100], dtick=10, gridcolor=GRID_COLOR),
            margin=dict(t=45, b=90), hovermode="x unified",
        )
        st.plotly_chart(fig3b, width="stretch")

st.divider()

# ══════════════════════════════════════════════════════════════════════
# 4. Treemaps comparativos — Exportaciones vs Importaciones
# ══════════════════════════════════════════════════════════════════════

st.subheader("4. Composición por categoría")

col_tm_exp, col_tm_imp = st.columns(2)

with col_tm_exp:
    st.caption("Exportaciones: Sector → Producto Principal (FOB)")
    if not df_exp_pais.empty:
        tree_exp = (df_exp_pais.groupby(["Sector", "PP"])["FOB"].sum()
                    .reset_index().rename(columns={"FOB": "FOB_total"}))
        tree_exp = tree_exp[tree_exp["FOB_total"] > 0]
        if not tree_exp.empty:
            fig4a = px.treemap(
                tree_exp, path=["Sector", "PP"], values="FOB_total",
                color="Sector", color_discrete_map=SECTOR_COLORS,
                custom_data=["FOB_total"],
            )
            fig4a.update_traces(
                hovertemplate="<b>%{label}</b><br>$%{customdata[0]:,.1f} M<extra></extra>",
                texttemplate="%{label}<br>$%{value:,.1f} M",
                textfont_size=11,
            )
            fig4a.update_layout(
                title=dict(text=f"Exportaciones FOB  ·  {ctx_label}", font=dict(size=12), x=0),
                height=500, margin=dict(t=45, b=10, l=10, r=10),
            )
            st.plotly_chart(fig4a, width="stretch")
    else:
        st.info("Sin datos de exportaciones para este país y período.")

with col_tm_imp:
    st.caption("Importaciones: Grupo CUODE → Subgrupo (CIF)")
    if not df_imp_pais.empty:
        tree_imp = (df_imp_pais.groupby(["Grupo", "Subgrupo"])["CIF"].sum()
                    .reset_index().rename(columns={"CIF": "CIF_total"}))
        tree_imp = tree_imp[tree_imp["CIF_total"] > 0]
        if not tree_imp.empty:
            fig4b = px.treemap(
                tree_imp, path=["Grupo", "Subgrupo"], values="CIF_total",
                color="Grupo", color_discrete_map=GRUPO_COLORS,
                custom_data=["CIF_total"],
            )
            fig4b.update_traces(
                hovertemplate="<b>%{label}</b><br>$%{customdata[0]:,.1f} M<extra></extra>",
                texttemplate="%{label}<br>$%{value:,.1f} M",
                textfont_size=11,
            )
            fig4b.update_layout(
                title=dict(text=f"Importaciones CIF  ·  {ctx_label}", font=dict(size=12), x=0),
                height=500, margin=dict(t=45, b=10, l=10, r=10),
            )
            st.plotly_chart(fig4b, width="stretch")
    else:
        st.info("Sin datos de importaciones para este país y período.")

# ── Footer ───────────────────────────────────────────────────────────

st.divider()

st.info(
    "Explora también los dashboards detallados: "
    "**[Exportaciones](https://jp1309-exportaciones.streamlit.app/)** | "
    "**[Importaciones](https://jp1309-importaciones.streamlit.app/)**",
    icon="🔗"
)

st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem; padding:1rem 0;'>"
    "Fuente: Banco Central del Ecuador (BCE) · Datos 2000–2025<br>"
    "Desarrollado por <b>Juan Pablo Erráez</b>"
    "</div>",
    unsafe_allow_html=True,
)
