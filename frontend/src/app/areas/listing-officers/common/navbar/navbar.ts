import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../auth.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
  imports: [RouterModule, CommonModule],
})
export class Navbar implements OnInit {
  currentTime: string = '';
  currentDate: string = '';

  constructor(private authService: AuthService) {}

  ngOnInit() {
    this.authService.initializeAuth().catch((error) => {
      console.warn('SSO initialization skipped in local mode.');
    });

    this.updateClock();
    setInterval(() => {
      this.updateClock();
    }, 1000);
  }

  onLogin(event: Event): void {
    event.preventDefault();
    this.authService.login();
  }

  onLogout(): void {
    window.location.href = '/user/login';
  }

  updateClock() {
    const now = new Date();
    this.currentTime = now.toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
    this.currentDate = now.toLocaleDateString('en-IN', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  }
}

