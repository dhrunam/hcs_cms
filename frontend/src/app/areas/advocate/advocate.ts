import { Component } from '@angular/core';
import { Navbar } from './common/navbar/navbar';
import { Sidebar } from './common/sidebar/sidebar';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-advocate',
  imports: [Navbar, Sidebar, RouterOutlet],
  templateUrl: './advocate.html',
  styleUrl: './advocate.css',
})
export class Advocate {
  advocateName: string = 'Sagar Pradhan';
}
