import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { StenoNavbar } from '../common/navbar/navbar';
import { StenoSidebar } from '../common/sidebar/sidebar';

@Component({
  selector: 'app-steno-dashboard',
  imports: [CommonModule, RouterOutlet, StenoNavbar, StenoSidebar],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class StenoDashboard {}
