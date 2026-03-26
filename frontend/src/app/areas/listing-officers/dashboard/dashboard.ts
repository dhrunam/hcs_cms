import { Component } from '@angular/core';
import { Navbar } from '../common/navbar/navbar';
import { Sidebar } from '../common/sidebar/sidebar';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-listing-officer-dashboard',
  imports: [Navbar, Sidebar, CommonModule, RouterOutlet],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class ListingOfficerDashboard {}

