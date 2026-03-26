// Ensures TypeScript can resolve `pdfjs-dist` even if the package ships without type declarations.
// This is needed because `tsconfig.app.json` only includes `src/**/*.ts` (not `src/**/*.d.ts`).
declare module 'pdfjs-dist';

export {};

