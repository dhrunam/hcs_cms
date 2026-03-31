export type BenchKey =
  | 'CJ'
  | 'Judge1'
  | 'Judge2'
  | 'CJ+Judge1'
  | 'CJ+Judge2'
  | 'Judge1+Judge2'
  | 'CJ+Judge1+Judge2';

export const BENCH_LABELS: Record<BenchKey, string> = {
  CJ: "Hon'ble Chief Justice",
  Judge1: "Hon'ble Judge - I",
  Judge2: "Hon'ble Judge - II",
  'CJ+Judge1': 'Division Bench I',
  'CJ+Judge2': 'Division Bench II',
  'Judge1+Judge2': 'Division Bench III',
  'CJ+Judge1+Judge2': 'Full Bench',
};

export const BENCH_TO_JUDGES: Record<BenchKey, string[]> = {
  CJ: ["Hon'ble Chief Justice"],
  Judge1: ["Hon'ble Judge - I"],
  Judge2: ["Hon'ble Judge - II"],
  'CJ+Judge1': ["Hon'ble Chief Justice", "Hon'ble Judge - I"],
  'CJ+Judge2': ["Hon'ble Chief Justice", "Hon'ble Judge - II"],
  'Judge1+Judge2': ["Hon'ble Judge - I", "Hon'ble Judge - II"],
  'CJ+Judge1+Judge2': ["Hon'ble Chief Justice", "Hon'ble Judge - I", "Hon'ble Judge - II"],
};

const UNASSIGNED_BENCH_VALUES = new Set([
  '',
  'high court of sikkim',
  'high court of skkim',
]);

export function isUnassignedBench(key: string | null | undefined): boolean {
  const v = String(key ?? '').trim().toLowerCase();
  if (!v) return true;
  return UNASSIGNED_BENCH_VALUES.has(v);
}

export function benchLabel(key: string | null | undefined): string {
  if (isUnassignedBench(key)) return '-';
  const k = String(key ?? '').trim();
  return (BENCH_LABELS as Record<string, string>)[k] ?? k;
}

export function judgesForBench(key: string | null | undefined): string[] {
  const k = String(key ?? '').trim() as BenchKey;
  return (BENCH_TO_JUDGES as Record<string, string[]>)[k] ?? [];
}

