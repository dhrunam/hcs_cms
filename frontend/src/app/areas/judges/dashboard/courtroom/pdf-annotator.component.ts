import { Component, Input, Output, EventEmitter, ViewChildren, QueryList, ElementRef, OnChanges, SimpleChanges, NgZone, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import * as pdfjsLib from 'pdfjs-dist';

// pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;
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
  imports: [CommonModule, FormsModule],
  templateUrl: './pdf-annotator.component.html',
  styleUrl: './pdf-annotator.component.css'
})
export class PdfAnnotatorComponent implements OnChanges, AfterViewInit {
  @Input() pdfUrl: string = '';
  @Input() annotationData: any = null;
  @Input() canWrite: boolean = false;
  @Output() save = new EventEmitter<any>();

  @ViewChildren('pdfCanvas') pdfCanvases!: QueryList<ElementRef<HTMLCanvasElement>>;
  @ViewChildren('drawCanvas') drawCanvases!: QueryList<ElementRef<HTMLCanvasElement>>;

  isLoading = false;
  loadingProgress = 0;
  pdfDocument: any | null = null;
  
  pages: PageData[] = [];

  currentTool: 'pen' | 'highlighter' | 'note' = 'pen';
  penColor: string = '#000000';
  highlighterColor: string = 'rgba(255, 255, 0, 0.4)';
  
  isDrawing = false;
  currentPath: DrawPath | null = null;
  activePageIndex: number | null = null;

  constructor(private ngZone: NgZone) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['pdfUrl'] && this.pdfUrl) {
      this.loadPdf();
    }
  }

  ngAfterViewInit(): void {
    this.drawCanvases.changes.subscribe(() => {
      this.redrawAllAnnotations();
    });
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
      const parsedData = this.annotationData || { pages: [] };

      for (let i = 1; i <= numPages; i++) {
        const page = await this.pdfDocument.getPage(i);
        const viewport = page.getViewport({ scale: 1.5 });
        
        const existingData = parsedData.pages.find((p: any) => p.pageIndex === i - 1) || { paths: [], notes: [] };

        this.pages.push({
          pageIndex: i - 1,
          width: viewport.width,
          height: viewport.height,
          pdfPage: page,
          paths: existingData.paths || [],
          notes: existingData.notes || []
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
        const canvas = canvasArray[i].nativeElement;
        const ctx = canvas.getContext('2d');
        if (!ctx) continue;

        const viewport = pd.pdfPage.getViewport({ scale: 1.5 });
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
    this.isDrawing = false;
    this.activePageIndex = null;
    this.currentPath = null;
  }

  addNoteAt(event: MouseEvent, pageIndex: number) {
    const canvas = this.drawCanvases.toArray()[pageIndex].nativeElement;
    const rect = canvas.getBoundingClientRect();
    const x = Math.max(0, Math.min((event.clientX - rect.left) / canvas.width, 0.8));
    const y = Math.max(0, Math.min((event.clientY - rect.top) / canvas.height, 0.9));

    this.pages[pageIndex].notes.push({ x, y, text: '' });
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
