#!/usr/bin/env python3
"""
VoxParaguay 2026 - Generate Paraguay TopoJSON
Downloads and converts Paraguay department boundaries to TopoJSON format
"""

import json
import geopandas as gpd
import topojson as tp
from pathlib import Path

# Output paths
OUTPUT_DIR = Path(__file__).parent.parent.parent / "frontend" / "public" / "geo"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Paraguay departments with ISO 3166-2:PY codes
DEPARTMENT_ISO_CODES = {
    "Concepción": "PY-1",
    "San Pedro": "PY-2",
    "Cordillera": "PY-3",
    "Guairá": "PY-4",
    "Caaguazú": "PY-5",
    "Caazapá": "PY-6",
    "Itapúa": "PY-7",
    "Misiones": "PY-8",
    "Paraguarí": "PY-9",
    "Alto Paraná": "PY-10",
    "Central": "PY-11",
    "Ñeembucú": "PY-12",
    "Amambay": "PY-13",
    "Canindeyú": "PY-14",
    "Presidente Hayes": "PY-15",
    "Alto Paraguay": "PY-16",
    "Boquerón": "PY-19",
    "Asunción": "PY-ASU",
}

# Alternative name mappings (handles GADM concatenated names)
NAME_ALIASES = {
    # GADM concatenated names
    "AltoParaguay": "Alto Paraguay",
    "AltoParaná": "Alto Paraná",
    "PresidenteHayes": "Presidente Hayes",
    "SanPedro": "San Pedro",
    # Accent variations
    "Neembucu": "Ñeembucú",
    "Neembucú": "Ñeembucú",
    "Canindeyu": "Canindeyú",
    "Boqueron": "Boquerón",
    "Guaira": "Guairá",
    "Caazapa": "Caazapá",
    "Itapua": "Itapúa",
    "Paraguari": "Paraguarí",
    "Concepcion": "Concepción",
    "Asuncion": "Asunción",
}

def normalize_name(name: str) -> str:
    """Normalize department name to match ISO codes."""
    name = name.strip()
    return NAME_ALIASES.get(name, name)

def download_paraguay_boundaries():
    """Download Paraguay administrative boundaries from Natural Earth or GADM."""
    print("Downloading Paraguay boundaries...")

    # Try GADM first (more detailed)
    try:
        # GADM level 1 = departments/states
        url = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_PRY_1.json"
        gdf = gpd.read_file(url)
        print(f"Downloaded from GADM: {len(gdf)} departments")
        return gdf
    except Exception as e:
        print(f"GADM download failed: {e}")

    # Fallback to Natural Earth
    try:
        url = "https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip"
        world = gpd.read_file(url)
        gdf = world[world['admin'] == 'Paraguay'].copy()
        print(f"Downloaded from Natural Earth: {len(gdf)} departments")
        return gdf
    except Exception as e:
        print(f"Natural Earth download failed: {e}")
        raise RuntimeError("Could not download Paraguay boundaries")

def create_topojson(gdf: gpd.GeoDataFrame) -> dict:
    """Convert GeoDataFrame to TopoJSON with ISO codes."""
    print("Converting to TopoJSON...")

    # Identify the name column
    name_col = None
    for col in ['NAME_1', 'name', 'NAME', 'admin1', 'VARNAME_1']:
        if col in gdf.columns:
            name_col = col
            break

    if name_col is None:
        print(f"Available columns: {gdf.columns.tolist()}")
        raise ValueError("Could not find name column")

    print(f"Using name column: {name_col}")

    # Add ISO codes
    gdf = gdf.copy()
    gdf['iso_code'] = gdf[name_col].apply(lambda x: DEPARTMENT_ISO_CODES.get(normalize_name(x), f"PY-{x}"))
    gdf['nombre'] = gdf[name_col].apply(normalize_name)

    # Print mapping for verification
    print("\nDepartment mapping:")
    for _, row in gdf.iterrows():
        print(f"  {row[name_col]} -> {row['iso_code']} ({row['nombre']})")

    # Simplify geometry for smaller file size (preserve topology)
    gdf_simplified = gdf.copy()
    gdf_simplified['geometry'] = gdf_simplified['geometry'].simplify(0.01, preserve_topology=True)

    # Select only needed columns
    gdf_export = gdf_simplified[['iso_code', 'nombre', 'geometry']].copy()
    gdf_export = gdf_export.rename(columns={'iso_code': 'id', 'nombre': 'name'})

    # Convert to TopoJSON
    topo = tp.Topology(gdf_export, prequantize=True)
    topojson_data = topo.to_dict()

    return topojson_data

def create_geojson(gdf: gpd.GeoDataFrame) -> dict:
    """Convert GeoDataFrame to GeoJSON with ISO codes."""
    print("Converting to GeoJSON...")

    # Identify the name column
    name_col = None
    for col in ['NAME_1', 'name', 'NAME', 'admin1', 'VARNAME_1']:
        if col in gdf.columns:
            name_col = col
            break

    if name_col is None:
        raise ValueError("Could not find name column")

    # Add ISO codes
    gdf = gdf.copy()
    gdf['id'] = gdf[name_col].apply(lambda x: DEPARTMENT_ISO_CODES.get(normalize_name(x), f"PY-{x}"))
    gdf['name'] = gdf[name_col].apply(normalize_name)

    # Simplify geometry
    gdf['geometry'] = gdf['geometry'].simplify(0.01, preserve_topology=True)

    # Select columns and convert
    gdf_export = gdf[['id', 'name', 'geometry']].copy()

    return json.loads(gdf_export.to_json())

def main():
    print("=" * 60)
    print("VoxParaguay 2026 - Paraguay TopoJSON Generator")
    print("=" * 60)

    # Download boundaries
    gdf = download_paraguay_boundaries()

    # Ensure CRS is WGS84
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Create TopoJSON
    topojson_data = create_topojson(gdf)

    # Save TopoJSON
    topojson_path = OUTPUT_DIR / "paraguay-departments.topojson"
    with open(topojson_path, 'w', encoding='utf-8') as f:
        json.dump(topojson_data, f, ensure_ascii=False)
    print(f"\nSaved TopoJSON: {topojson_path}")
    print(f"File size: {topojson_path.stat().st_size / 1024:.1f} KB")

    # Create GeoJSON (for compatibility)
    geojson_data = create_geojson(gdf)

    geojson_path = OUTPUT_DIR / "paraguay-departments.geojson"
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False)
    print(f"Saved GeoJSON: {geojson_path}")
    print(f"File size: {geojson_path.stat().st_size / 1024:.1f} KB")

    # Create a TypeScript constants file
    create_typescript_constants(topojson_data)

    print("\n" + "=" * 60)
    print("Done! Files created in frontend/public/geo/")
    print("=" * 60)

def create_typescript_constants(topojson_data: dict):
    """Create TypeScript file with department metadata."""
    ts_path = OUTPUT_DIR.parent.parent / "lib" / "geo" / "paraguay.ts"
    ts_path.parent.mkdir(parents=True, exist_ok=True)

    # Extract department info
    objects_key = list(topojson_data.get('objects', {}).keys())[0] if topojson_data.get('objects') else None

    ts_content = '''/**
 * VoxParaguay 2026 - Paraguay Geographic Data
 * Auto-generated from GADM boundaries
 */

// ISO 3166-2:PY Department Codes
export const PARAGUAY_DEPARTMENTS = {
  "PY-ASU": { name: "Asunción", capital: "Asunción", region: "Capital" },
  "PY-1": { name: "Concepción", capital: "Concepción", region: "Oriental" },
  "PY-2": { name: "San Pedro", capital: "San Pedro de Ycuamandiyú", region: "Oriental" },
  "PY-3": { name: "Cordillera", capital: "Caacupé", region: "Oriental" },
  "PY-4": { name: "Guairá", capital: "Villarrica", region: "Oriental" },
  "PY-5": { name: "Caaguazú", capital: "Coronel Oviedo", region: "Oriental" },
  "PY-6": { name: "Caazapá", capital: "Caazapá", region: "Oriental" },
  "PY-7": { name: "Itapúa", capital: "Encarnación", region: "Oriental" },
  "PY-8": { name: "Misiones", capital: "San Juan Bautista", region: "Oriental" },
  "PY-9": { name: "Paraguarí", capital: "Paraguarí", region: "Oriental" },
  "PY-10": { name: "Alto Paraná", capital: "Ciudad del Este", region: "Oriental" },
  "PY-11": { name: "Central", capital: "Areguá", region: "Oriental" },
  "PY-12": { name: "Ñeembucú", capital: "Pilar", region: "Oriental" },
  "PY-13": { name: "Amambay", capital: "Pedro Juan Caballero", region: "Oriental" },
  "PY-14": { name: "Canindeyú", capital: "Salto del Guairá", region: "Oriental" },
  "PY-15": { name: "Presidente Hayes", capital: "Villa Hayes", region: "Occidental" },
  "PY-16": { name: "Alto Paraguay", capital: "Fuerte Olimpo", region: "Occidental" },
  "PY-19": { name: "Boquerón", capital: "Filadelfia", region: "Occidental" },
} as const;

export type DepartmentCode = keyof typeof PARAGUAY_DEPARTMENTS;

// TopoJSON file path
export const TOPOJSON_PATH = "/geo/paraguay-departments.topojson";
export const GEOJSON_PATH = "/geo/paraguay-departments.geojson";

// Helper to get department info
export function getDepartmentInfo(code: DepartmentCode) {
  return PARAGUAY_DEPARTMENTS[code];
}

// Get all department codes
export function getAllDepartmentCodes(): DepartmentCode[] {
  return Object.keys(PARAGUAY_DEPARTMENTS) as DepartmentCode[];
}

// Get departments by region
export function getDepartmentsByRegion(region: "Oriental" | "Occidental" | "Capital"): DepartmentCode[] {
  return (Object.entries(PARAGUAY_DEPARTMENTS) as [DepartmentCode, typeof PARAGUAY_DEPARTMENTS[DepartmentCode]][])
    .filter(([_, info]) => info.region === region)
    .map(([code, _]) => code);
}
'''

    with open(ts_path, 'w', encoding='utf-8') as f:
        f.write(ts_content)
    print(f"Saved TypeScript: {ts_path}")

if __name__ == "__main__":
    main()
