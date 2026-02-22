# Balanza Comercial del Ecuador por País

Dashboard interactivo que combina exportaciones e importaciones del Ecuador para visualizar el balance comercial bilateral con cada país socio, de 2000 a 2025.

**URL pública:** https://jp1309-balanza.streamlit.app/

Forma parte de una suite de tres dashboards de comercio exterior:

| Dashboard | URL |
|-----------|-----|
| Exportaciones | https://jp1309-exportaciones.streamlit.app/ |
| Importaciones | https://jp1309-importaciones.streamlit.app/ |
| **Balanza Comercial** | https://jp1309-balanza.streamlit.app/ |

---

## Qué muestra

Seleccionas un país socio (o una región completa) y un rango de años, y el dashboard presenta:

1. **KPIs** — Exportaciones FOB totales, Importaciones CIF totales, Saldo comercial (superávit/déficit), y variación % del último año para cada flujo.
2. **Balanza Comercial Anual** — Barras agrupadas (azul = exportaciones, rojo = importaciones) más línea punteada del saldo neto.
3. **¿Qué le exportamos?** — Evolución en USD (líneas, top 10 productos) y participación % anual (área apilada), clasificados por Producto Principal del BCE.
4. **¿Qué le importamos?** — Igual estructura pero por Subgrupo CUODE (clasificación de uso o destino económico).
5. **Treemaps comparativos** — Composición acumulada del período: exportaciones por Sector → Producto, importaciones por Grupo → Subgrupo CUODE.

---

## Datos

| Fuente | Archivo | Tamaño | Filas originales |
|--------|---------|--------|-----------------|
| BCE — Exportaciones | `data/exportaciones_ecuador.parquet` | 12 MB | ~1.09 M |
| BCE — Importaciones | `data/importaciones_ecuador.parquet` | 52 MB | ~6.7 M |

- **Período:** enero 2000 – diciembre 2025
- **Exportaciones:** valor FOB en miles USD en el parquet → convertido a millones USD en carga
- **Importaciones:** valor CIF en miles USD en el parquet → convertido a millones USD en carga
- Los parquets están incluidos en el repositorio como archivos binarios (sin Git LFS)

---

## Estructura del proyecto

```
balanza_comercial/
├── app.py                          # Aplicación principal (archivo único)
├── requirements.txt                # Dependencias Python
├── data/
│   ├── exportaciones_ecuador.parquet
│   └── importaciones_ecuador.parquet
└── README.md
```

---

## Filtros

- **Región** (sidebar) — filtra la lista de países por zona geográfica: América Latina, América del Norte, Europa, Asia, Medio Oriente, África, Oceanía. Al seleccionar una región aparece la opción "— Todos —" para ver el agregado regional completo.
- **Período** (sidebar) — inputs numéricos Desde / Hasta (2000–2025).
- **País** (área principal) — selectbox con todos los países del rango seleccionado.

---

## Clasificaciones

**Exportaciones — Sectores** (primeros 2 dígitos del código de Producto Principal BCE):

| Código | Sector |
|--------|--------|
| 11 | Prod. Primarios Agrícolas |
| 12 | Silvicultura |
| 13 | Pecuarios |
| 14 | Pesca |
| 15 | Minería y Petróleo |
| 21 | Químicos y Farmacéuticos |
| 22 | Alimentos Procesados |
| 23 | Industrializados |
| 31 | Desperdicios de Papel |
| 32 | Desperdicios de Metales |
| 33 | Otros Desperdicios |
| 41 | Animales Vivos |

**Importaciones — Grupos CUODE** (Clasificación por Uso o Destino Económico):

| Código | Grupo |
|--------|-------|
| 01 | Consumo No Duradero |
| 02 | Consumo Duradero |
| 03 | Combustibles y Lubricantes |
| 04 | Mat. Primas Agropecuarias |
| 05 | Mat. Primas Industriales |
| 06 | Construcción |
| 07 | Capital Agrícola |
| 08 | Capital Industrial |
| 09 | Equipo de Transporte |
| 10 | Diversos |

---

## Lógica de colores

Los colores son semánticos y consistentes entre exportaciones e importaciones:

| Categoría económica | Color |
|--------------------|-------|
| Agropecuario / Agricultura | Verde (`#16a34a`) |
| Petróleo / Combustibles | Negro (`#000000`) |
| Industrial / Capital | Azul (`#1d4ed8`) |
| Silvicultura / Construcción | Marrón (`#92400e`) |
| Transporte | Rojo (`#dc2626`) |
| Pesca / Mar | Cyan (`#0891b2`) |
| Desperdicios / Diversos | Gris (`#9ca3af`) |

---

## Instalación local

```bash
git clone https://github.com/jp1309/balanza_comercial.git
cd balanza_comercial
pip install -r requirements.txt
streamlit run app.py
```

Requiere Python 3.9+. Los parquets ya están incluidos en `data/`.

---

## Dependencias

```
streamlit>=1.30
plotly>=5.0
pandas>=2.0
pyarrow>=14.0
```

---

## Autor

**Juan Pablo Erráez**
Fuente de datos: [Banco Central del Ecuador (BCE)](https://www.bce.fin.ec/)
