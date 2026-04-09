import { Component, Input, Output, EventEmitter, ViewChildren, QueryList, ElementRef, OnChanges, SimpleChanges, NgZone, AfterViewInit, ViewChild, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DragDropModule, CdkDragEnd } from '@angular/cdk/drag-drop';
import { FormsModule } from '@angular/forms';
import * as pdfjsLib from 'pdfjs-dist';

// Must match the installed `pdfjs-dist` major version (copied to site root via angular.json assets).
pdfjsLib.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

interface Point { x: number; y: number; }
interface DrawPath {
  type: 'pen' | 'highlighter';
  color: string;
  width: number;
  points: Point[];
}
interface Note {
  x: number;
  y: number;
  text: string;
}

interface PageData {
  pageIndex: number;
  width: number;
  height: number;
  pdfPage: any;
  paths: DrawPath[];
  notes: Note[];
}

@Component({
  selector: 'app-pdf-annotator',
  standalone: true,
  imports: [CommonModule, FormsModule, DragDropModule],
  templateUrl: './pdf-annotator.component.html',
  styleUrl: './pdf-annotator.component.css'
})
export class PdfAnnotatorComponent implements OnChanges, AfterViewInit, OnDestroy {
  @Input() pdfUrl: string = '';
  @Input() annotationData: any = null;
  @Input() canWrite: boolean = false;
  @Output() save = new EventEmitter<any>();
  @Output() pageChange = new EventEmitter<number>();

  @ViewChild('scrollContainer') scrollContainer!: ElementRef<HTMLDivElement>;
  @ViewChildren('pdfCanvas') pdfCanvases!: QueryList<ElementRef<HTMLCanvasElement>>;
  @ViewChildren('drawCanvas') drawCanvases!: QueryList<ElementRef<HTMLCanvasElement>>;

  isLoading = false;
  loadingProgress = 0;
  pdfDocument: any | null = null;
  
  pages: PageData[] = [];
  scale: number = 1.0;
  currentPageIndex: number = 0;

  private resizeObserver: ResizeObserver | null = null;

  currentTool: 'pen' | 'highlighter' | 'note' = 'pen';
  penColor: string = '#000000';
  highlighterColor: string = 'rgba(255, 255, 0, 0.4)';
  
  isDrawing = false;
  currentPath: DrawPath | null = null;
  activePageIndex: number | null = null;
  
  undoStack: { pageIndex: number; type: 'path' | 'note'; item: any }[] = [];

  constructor(private ngZone: NgZone) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['pdfUrl'] && this.pdfUrl) {
      this.loadPdf();
      return;
    }
    if (
      changes['annotationData'] &&
      this.pdfDocument &&
      this.pages.length &&
      !this.isLoading
    ) {
      this.applyAnnotationDataToPages();
    }
  }

  ngAfterViewInit(): void {
    this.drawCanvases.changes.subscribe(() => {
      this.redrawAllAnnotations();
    });
    this.setupResizeObserver();
  }

  ngOnDestroy(): void {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
  }

  setupResizeObserver() {
    this.resizeObserver = new ResizeObserver(() => {
      this.ngZone.run(() => {
        this.recalculateScaleAndRender();
      });
    });
    if (this.scrollContainer) {
      this.resizeObserver.observe(this.scrollContainer.nativeElement);
    }
  }

  async recalculateScaleAndRender() {
    if (!this.pages.length || !this.pdfDocument || this.isLoading) return;
    
    // Default to 1.5 as requested (previous size)
    const newScale = 1.5;
    
    if (Math.abs(this.scale - newScale) < 0.01) return;
    
    this.scale = newScale;
    
    for (let i = 0; i < this.pages.length; i++) {
      const page = await this.pdfDocument.getPage(i + 1);
      const viewport = page.getViewport({ scale: this.scale });
      this.pages[i].width = viewport.width;
      this.pages[i].height = viewport.height;
    }
    
    this.renderPdfPages();
  }

  /** Re-apply annotation payload after PDF is loaded (e.g. server data arrived). */
  private applyAnnotationDataToPages(): void {
    let parsedData = this.annotationData;
    if (typeof parsedData === 'string' && parsedData) {
      try {
        parsedData = JSON.parse(parsedData);
      } catch {
        parsedData = { pages: [] };
      }
    }
    if (!parsedData || !Array.isArray(parsedData.pages)) {
      parsedData = { pages: [] };
    }
    for (const p of this.pages) {
      const existing = (parsedData.pages as any[]).find(
        (x: any) => x.pageIndex === p.pageIndex,
      ) || { paths: [], notes: [] };
      p.paths = Array.isArray(existing.paths)
        ? existing.paths.map((path: any) => ({
            ...path,
            points: Array.isArray(path.points)
              ? path.points.map((pt: any) => ({ ...pt }))
              : [],
          }))
        : [];
      p.notes = Array.isArray(existing.notes)
        ? existing.notes.map((n: any) => ({ ...n, text: n.text ?? '' }))
        : [];
    }
    this.undoStack = [];
    this.redrawAllAnnotations();
  }

  setTool(tool: 'pen' | 'highlighter' | 'note', color?: string) {
    this.currentTool = tool;
    if (color && tool === 'pen') {
      this.penColor = color;
    }
  }

  async loadPdf() {
    this.isLoading = true;
    this.loadingProgress = 0;
    this.pages = [];
    this.undoStack = [];

    try {
      const loadingTask = pdfjsLib.getDocument(this.pdfUrl);
      
      loadingTask.onProgress = (progressData: any) => {
        this.ngZone.run(() => {
          if (progressData.total > 0) {
            this.loadingProgress = Math.round((progressData.loaded / progressData.total) * 100);
          }
        });
      };

      this.pdfDocument = await loadingTask.promise;
      const numPages = this.pdfDocument.numPages;
      
      let parsedData = this.annotationData;
      if (typeof parsedData === 'string' && parsedData) {
        try {
          parsedData = JSON.parse(parsedData);
        } catch (e) {
          parsedData = { pages: [] };
        }
      }
      if (!parsedData || !Array.isArray(parsedData.pages)) {
        parsedData = { pages: [] };
      }

      this.scale = 1.5; // Fixed size (previous size)

      for (let i = 1; i <= numPages; i++) {
        const page = await this.pdfDocument.getPage(i);
        const viewport = page.getViewport({ scale: this.scale });
        
        const existingData = (parsedData.pages as any[]).find((p: any) => p.pageIndex === i - 1) || { paths: [], notes: [] };

        this.pages.push({
          pageIndex: i - 1,
          width: viewport.width,
          height: viewport.height,
          pdfPage: page,
          paths: Array.isArray(existingData.paths) ? existingData.paths : [],
          notes: Array.isArray(existingData.notes) ? existingData.notes : []
        });
      }
      
      this.isLoading = false;
      setTimeout(() => this.renderPdfPages(), 100);
    } catch (error) {
      console.error('Error loading PDF', error);
      this.isLoading = false;
    }
  }

  async renderPdfPages() {
    const canvasArray = this.pdfCanvases.toArray();
    for (let i = 0; i < this.pages.length; i++) {
        const pd = this.pages[i];
        if (!canvasArray[i]) continue;
        const canvas = canvasArray[i].nativeElement;
        const ctx = canvas.getContext('2d');
        if (!ctx) continue;

        const viewport = pd.pdfPage.getViewport({ scale: this.scale });
        
        // CRITICAL FIX: Explicitly set canvas dimensions to prevent blurry/small view
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        
        const drawCanvasArray = this.drawCanvases.toArray();
        if (drawCanvasArray[i]) {
          drawCanvasArray[i].nativeElement.width = viewport.width;
          drawCanvasArray[i].nativeElement.height = viewport.height;
        }

        await pd.pdfPage.render({ canvasContext: ctx, viewport: viewport }).promise;
    }
    this.redrawAllAnnotations();
  }

  redrawAllAnnotations() {
    const drawCanvasArray = this.drawCanvases.toArray();
    for (let i = 0; i < this.pages.length; i++) {
      if (!drawCanvasArray[i]) continue;
      const canvas = drawCanvasArray[i].nativeElement;
      this.redrawCanvas(canvas, this.pages[i].paths);
    }
  }

  redrawCanvas(canvas: HTMLCanvasElement, paths: DrawPath[]) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    for (const path of paths) {
      if (path.points.length < 2) continue;
      
      ctx.beginPath();
      ctx.strokeStyle = path.color;
      ctx.lineWidth = path.width;
      if (path.type === 'highlighter') {
         ctx.globalCompositeOperation = 'multiply';
      } else {
         ctx.globalCompositeOperation = 'source-over';
      }

      ctx.moveTo(path.points[0].x * canvas.width, path.points[0].y * canvas.height);
      for (let i = 1; i < path.points.length; i++) {
        ctx.lineTo(path.points[i].x * canvas.width, path.points[i].y * canvas.height);
      }
      ctx.stroke();
    }
    ctx.globalCompositeOperation = 'source-over';
  }

  onMouseDown(event: MouseEvent, pageIndex: number) {
    if (!this.canWrite) return;
    if (this.currentTool === 'note') {
       this.addNoteAt(event, pageIndex);
       return;
    }

    this.isDrawing = true;
    this.activePageIndex = pageIndex;
    
    const canvas = this.drawCanvases.toArray()[pageIndex].nativeElement;
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left) / canvas.width;
    const y = (event.clientY - rect.top) / canvas.height;

    this.currentPath = {
      type: this.currentTool,
      color: this.currentTool === 'highlighter' ? this.highlighterColor : this.penColor,
      width: this.currentTool === 'highlighter' ? 16 : 2,
      points: [{ x, y }]
    };
    
    this.pages[pageIndex].paths.push(this.currentPath);
  }

  onMouseMove(event: MouseEvent, pageIndex: number) {
    if (!this.isDrawing || pageIndex !== this.activePageIndex || !this.currentPath) return;

    const canvas = this.drawCanvases.toArray()[pageIndex].nativeElement;
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left) / canvas.width;
    const y = (event.clientY - rect.top) / canvas.height;

    this.currentPath.points.push({ x, y });
    this.redrawCanvas(canvas, this.pages[pageIndex].paths);
  }

  onMouseUp() {
    if (this.isDrawing && this.activePageIndex !== null && this.currentPath) {
       this.undoStack.push({ pageIndex: this.activePageIndex, type: 'path', item: this.currentPath });
    }
    this.isDrawing = false;
    this.activePageIndex = null;
    this.currentPath = null;
  }

  addNoteAt(event: MouseEvent, pageIndex: number) {
    const canvas = this.drawCanvases.toArray()[pageIndex].nativeElement;
    const rect = canvas.getBoundingClientRect();
    const x = Math.max(0, Math.min((event.clientX - rect.left) / canvas.width, 0.8));
    const y = Math.max(0, Math.min((event.clientY - rect.top) / canvas.height, 0.9));

    const newNote = { x, y, text: '' };
    this.pages[pageIndex].notes.push(newNote);
    this.undoStack.push({ pageIndex, type: 'note', item: newNote });
    this.setTool('pen');
  }

  onScroll(event: any) {
    const container = event.target;
    if (this.pages.length === 0) return;
    const pageHeight = container.scrollHeight / this.pages.length;
    const newIndex = Math.round(container.scrollTop / pageHeight);
    
    if (newIndex !== this.currentPageIndex && newIndex >= 0 && newIndex < this.pages.length) {
      this.currentPageIndex = newIndex;
      this.pageChange.emit(newIndex);
    }
  }

  scrollToPage(index: number) {
    if (!this.scrollContainer || index < 0 || index >= this.pages.length) return;
    const container = this.scrollContainer.nativeElement;
    const pageHeight = container.scrollHeight / this.pages.length;
    container.scrollTo({
      top: index * pageHeight,
      behavior: 'smooth'
    });
  }

  undoLastAction() {
    const action = this.undoStack.pop();
    if (!action) return;

    const page = this.pages[action.pageIndex];
    if (!page) return;

    if (action.type === 'path') {
      const idx = page.paths.indexOf(action.item);
      if (idx !== -1) page.paths.splice(idx, 1);
    } else {
      const idx = page.notes.indexOf(action.item);
      if (idx !== -1) page.notes.splice(idx, 1);
    }
    this.redrawAllAnnotations();
  }

  onNoteDropped(event: CdkDragEnd, pageIndex: number, noteIndex: number) {
    const note = this.pages[pageIndex].notes[noteIndex];
    const element = event.source.element.nativeElement;
    const parent = element.parentElement;
    if (!parent) return;

    const parentRect = parent.getBoundingClientRect();
    const elementRect = element.getBoundingClientRect();

    // Calculate new relative position
    note.x = (elementRect.left - parentRect.left) / parentRect.width;
    note.y = (elementRect.top - parentRect.top) / parentRect.height;
    
    // Reset the transform so Angular's [style.left.px] takes over properly
    event.source.reset();
  }

  getNotesForPage(pageIndex: number) {
    return this.pages[pageIndex]?.notes || [];
  }

  removeNote(pageIndex: number, noteIndex: number) {
     this.pages[pageIndex].notes.splice(noteIndex, 1);
  }

  clearCurrentPage() {
    if (!this.canWrite) return;
    const ans = confirm('Clear annotations on all pages?');
    if (ans) {
       for (const pg of this.pages) {
          pg.paths = [];
          pg.notes = [];
       }
       this.redrawAllAnnotations();
    }
  }

  triggerChange() {
    // Note bounds updated via ngModel bindings.
  }

  saveAnnotations() {
    if (!this.canWrite) return;
    
    const payload = {
       pages: this.pages.map((p) => ({
          pageIndex: p.pageIndex,
          paths: p.paths,
          notes: p.notes
       }))
    };
    
    this.save.emit(payload);
  }
}
