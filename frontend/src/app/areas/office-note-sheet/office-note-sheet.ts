import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-office-note-sheet',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './office-note-sheet.html',
  styleUrl: './office-note-sheet.css',
})
export class OfficeNoteSheet {}