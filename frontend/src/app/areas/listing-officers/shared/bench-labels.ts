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

export function benchLabel(key: string | null | undefined): string {
  if (!key) return '-';
  return (BENCH_LABELS as Record<string, string>)[key] ?? key;
}

