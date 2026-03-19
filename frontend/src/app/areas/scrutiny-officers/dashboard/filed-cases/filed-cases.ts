import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-filed-cases',
  standalone: true,
  imports: [CommonModule, RouterOutlet],
  templateUrl: './filed-cases.html',
  styleUrls: ['./filed-cases.css'],
})
export class FiledCases {}
