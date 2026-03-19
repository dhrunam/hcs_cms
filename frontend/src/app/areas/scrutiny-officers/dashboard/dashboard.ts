import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Navbar } from '../common/navbar/navbar';
import { Sidebar } from '../common/sidebar/sidebar';

@Component({
  selector: 'app-scrutiny-officer-dashboard',
  imports: [Navbar, Sidebar, CommonModule, RouterOutlet],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class ScrutinyOfficerDashboard {}
