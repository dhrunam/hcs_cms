/**
 * PDF upload validation constants and helpers.
 * - Size check: done on frontend
 * - OCR check: optional client-side via pdfjs; backend also validates
 */
export const MAX_PDF_SIZE_BYTES = 25 * 1024 * 1024; // 25 MB
const MIN_OCR_TEXT_LENGTH = 20;

export interface PdfValidationResult {
  valid: boolean;
  error?: string;
}

export function validatePdfSize(file: File): PdfValidationResult {
  if (file.size > MAX_PDF_SIZE_BYTES) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
    return {
      valid: false,
      error: `PDF must be less than 25 MB. "${file.name}" is ${sizeMB} MB.`,
    };
  }
  return { valid: true };
}

/** Browsers (notably Safari) may leave `type` empty for PDFs picked from disk. */
export function isLikelyPdfFile(file: File): boolean {
  const t = String(file.type || '').toLowerCase().trim();
  if (t === 'application/pdf' || t === 'application/x-pdf') return true;
  if (!t || t === 'application/octet-stream') {
    return /\.pdf$/i.test(String(file.name || ''));
  }
  return false;
}

export function validatePdfFiles(files: File[]): { valid: File[]; errors: string[] } {
  const valid: File[] = [];
  const errors: string[] = [];
  for (const file of files) {
    if (!isLikelyPdfFile(file)) {
      errors.push(`"${file.name}" is not a PDF.`);
      continue;
    }
    const result = validatePdfSize(file);
    if (result.valid) {
      valid.push(file);
    } else if (result.error) {
      errors.push(result.error);
    }
  }
  return { valid, errors };
}

/**
 * Async OCR validation: checks if PDF has extractable text (OCR-converted).
 * Returns { valid: true } or { valid: false, error: string }.
 * Uses pdfjs-dist; falls back to valid if library fails (backend will validate).
 */
export async function validatePdfOcr(file: File): Promise<PdfValidationResult> {
  try {
    const pdfjs = await import('pdfjs-dist');
    const p = pdfjs as any;
    if (p.GlobalWorkerOptions && !p.GlobalWorkerOptions.workerSrc) {
      p.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';
    }
    const arrayBuffer = await file.arrayBuffer();
    const loadingTask = p.getDocument?.({ data: arrayBuffer });
    if (!loadingTask?.promise) return { valid: true }; // Skip if API unavailable
    const doc = await loadingTask.promise;
    const numPages = doc?.numPages ?? 0;
    if (numPages === 0) return { valid: false, error: `"${file.name}": PDF has no pages.` };
    const page = await doc.getPage(1);
    const textContent = await page.getTextContent();
    const text = (textContent?.items ?? [])
      .map((i: any) => (typeof i?.str === 'string' ? i.str : ''))
      .join('');
    const cleanLen = text.replace(/\s/g, '').length;
    if (cleanLen < MIN_OCR_TEXT_LENGTH) {
      return {
        valid: false,
        error: `"${file.name}" must be OCR-converted (searchable). This file appears to be a scanned image without a text layer.`,
      };
    }
    return { valid: true };
  } catch (e) {
    return { valid: true }; // Fallback: let backend validate
  }
}

/** Validate all files for OCR. Returns first error or null. */
export async function validatePdfOcrForFiles(files: File[]): Promise<string | null> {
  for (const file of files) {
    if (!isLikelyPdfFile(file)) continue;
    const result = await validatePdfOcr(file);
    if (!result.valid && result.error) return result.error;
  }
  return null;
}

/** Extract validation error message from API error response (e.g. DRF ValidationError). */
export function getValidationErrorMessage(err: any): string {
  const body = err?.error;
  if (body && typeof body === 'object') {
    const firstKey = Object.keys(body)[0];
    if (firstKey) {
      const val = body[firstKey];
      if (Array.isArray(val) && val.length > 0) return String(val[0]);
      if (typeof val === 'string') return val;
    }
    if (typeof body.detail === 'string') return body.detail;
  }
  return err?.message || 'An error occurred.';
}
