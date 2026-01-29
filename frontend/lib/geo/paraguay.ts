/**
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
