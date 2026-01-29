#!/usr/bin/env python3
"""
VoxParaguay 2026 - Map Optimization Script
Converts GeoJSON to optimized TopoJSON with simplification and quantization

Usage:
    python scripts/optimize_map.py

Input:  frontend/public/data/paraguay_raw.geojson
Output: frontend/public/data/paraguay_optimized.topojson
"""

import json
import sys
from pathlib import Path

import geopandas as gpd
import topojson as tp

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
INPUT_PATH = PROJECT_ROOT / "frontend" / "public" / "data" / "paraguay_raw.geojson"
OUTPUT_PATH = PROJECT_ROOT / "frontend" / "public" / "data" / "paraguay_optimized.topojson"
GADM_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_PRY_1.json"

# Optimization parameters
SIMPLIFY_TOLERANCE = 0.01  # Simplification tolerance (Douglas-Peucker)
QUANTIZATION = 1e5         # Quantization level (100,000)
OBJECT_NAME = "paraguay_departments"  # TopoJSON objects name

# ISO 3166-2:PY code mapping
DEPARTMENT_ISO_CODES = {
    "Concepción": "PY-1",
    "San Pedro": "PY-2",
    "SanPedro": "PY-2",
    "Cordillera": "PY-3",
    "Guairá": "PY-4",
    "Caaguazú": "PY-5",
    "Caazapá": "PY-6",
    "Itapúa": "PY-7",
    "Misiones": "PY-8",
    "Paraguarí": "PY-9",
    "Alto Paraná": "PY-10",
    "AltoParaná": "PY-10",
    "Central": "PY-11",
    "Ñeembucú": "PY-12",
    "Amambay": "PY-13",
    "Canindeyú": "PY-14",
    "Presidente Hayes": "PY-15",
    "PresidenteHayes": "PY-15",
    "Alto Paraguay": "PY-16",
    "AltoParaguay": "PY-16",
    "Boquerón": "PY-19",
    "Asunción": "PY-ASU",
}


def download_raw_geojson() -> gpd.GeoDataFrame:
    """Download raw GeoJSON from GADM if not exists."""
    print(f"📥 Downloading raw GeoJSON from GADM...")
    print(f"   URL: {GADM_URL}")

    gdf = gpd.read_file(GADM_URL)
    print(f"   Downloaded {len(gdf)} features")

    # Save raw file
    INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(INPUT_PATH, driver="GeoJSON")
    print(f"   Saved to: {INPUT_PATH}")

    return gdf


def load_geojson() -> gpd.GeoDataFrame:
    """Load GeoJSON from file or download if not exists."""
    if INPUT_PATH.exists():
        print(f"📂 Loading existing GeoJSON: {INPUT_PATH}")
        gdf = gpd.read_file(INPUT_PATH)
        print(f"   Loaded {len(gdf)} features")
    else:
        print(f"⚠️  Raw GeoJSON not found at: {INPUT_PATH}")
        gdf = download_raw_geojson()

    return gdf


def normalize_name(name: str) -> str:
    """Normalize department name for ISO code lookup."""
    return name.strip()


def get_iso_code(name: str) -> str:
    """Get ISO 3166-2:PY code for department name."""
    normalized = normalize_name(name)
    return DEPARTMENT_ISO_CODES.get(normalized, f"PY-{normalized}")


def process_geodataframe(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Process GeoDataFrame: add ISO codes and clean up columns."""
    print("🔧 Processing GeoDataFrame...")

    # Find name column
    name_col = None
    for col in ['NAME_1', 'name', 'NAME', 'VARNAME_1']:
        if col in gdf.columns:
            name_col = col
            break

    if name_col is None:
        print(f"   Available columns: {gdf.columns.tolist()}")
        raise ValueError("Could not find name column")

    print(f"   Using name column: {name_col}")

    # Add ISO codes
    gdf = gdf.copy()
    gdf['id'] = gdf[name_col].apply(get_iso_code)
    gdf['name'] = gdf[name_col].apply(normalize_name)

    # Select only needed columns
    gdf = gdf[['id', 'name', 'geometry']]

    # Ensure CRS is WGS84
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    print(f"   Processed {len(gdf)} departments")
    for _, row in gdf.iterrows():
        print(f"   - {row['id']}: {row['name']}")

    return gdf


def optimize_to_topojson(gdf: gpd.GeoDataFrame) -> dict:
    """
    Convert GeoDataFrame to optimized TopoJSON.

    Parameters:
        - toposimplify: Douglas-Peucker simplification tolerance (0.01)
        - prequantize: Quantization level (1e5 = 100,000)
        - object_name: Name for the TopoJSON objects collection
    """
    print("🗜️  Converting to TopoJSON with optimization...")
    print(f"   Simplification tolerance: {SIMPLIFY_TOLERANCE}")
    print(f"   Quantization level: {QUANTIZATION:.0e}")
    print(f"   Object name: {OBJECT_NAME}")

    # Create Topology with optimization parameters
    topo = tp.Topology(
        gdf,
        toposimplify=SIMPLIFY_TOLERANCE,
        prequantize=QUANTIZATION,
        object_name=OBJECT_NAME,
    )

    # Get dictionary representation
    topojson_dict = topo.to_dict()

    print(f"   Arcs count: {len(topojson_dict.get('arcs', []))}")

    return topojson_dict


def save_topojson(topojson_dict: dict, output_path: Path) -> None:
    """Save TopoJSON to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(topojson_dict, f, ensure_ascii=False, separators=(',', ':'))

    print(f"💾 Saved optimized TopoJSON: {output_path}")


def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    return path.stat().st_size if path.exists() else 0


def format_size(size_bytes: int) -> str:
    """Format file size for display."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def main():
    print("=" * 60)
    print("VoxParaguay 2026 - Map Optimization Script")
    print("=" * 60)
    print()

    # Load GeoJSON
    gdf = load_geojson()
    input_size = get_file_size(INPUT_PATH)
    print(f"   Input file size: {format_size(input_size)}")
    print()

    # Process GeoDataFrame
    gdf = process_geodataframe(gdf)
    print()

    # Convert to optimized TopoJSON
    topojson_dict = optimize_to_topojson(gdf)
    print()

    # Verify object name
    objects = topojson_dict.get('objects', {})
    print(f"📋 TopoJSON structure:")
    print(f"   Type: {topojson_dict.get('type')}")
    print(f"   Objects: {list(objects.keys())}")
    for obj_name, obj_data in objects.items():
        geoms = obj_data.get('geometries', [])
        print(f"   - {obj_name}: {len(geoms)} geometries")
    print()

    # Save TopoJSON
    save_topojson(topojson_dict, OUTPUT_PATH)
    output_size = get_file_size(OUTPUT_PATH)

    # Report size reduction
    print()
    print("📊 Size comparison:")
    print(f"   Input (GeoJSON):     {format_size(input_size)}")
    print(f"   Output (TopoJSON):   {format_size(output_size)}")

    if input_size > 0:
        reduction = ((input_size - output_size) / input_size) * 100
        print(f"   Size reduction:      {reduction:.1f}%")

    print()
    print("=" * 60)
    print("✅ Optimization complete!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
