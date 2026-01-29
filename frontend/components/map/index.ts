/**
 * VoxParaguay 2026 - Map Components
 * TopoJSON Paraguay Map with ISO 3166-2:PY codes
 */

export { default as ParaguayMap } from "./ParaguayMap";
export {
  dataMapper,
  sentimentToColor,
  getDepartmentFill,
  PARAGUAY_TOPOJSON,
  DEPARTMENT_METADATA,
  NO_DATA_COLOR,
} from "./ParaguayMap";

export type {
  DepartmentData,
  SentimentPerDept,
} from "./ParaguayMap";
