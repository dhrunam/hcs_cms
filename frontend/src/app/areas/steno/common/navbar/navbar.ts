import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../auth.service';

@Component({
  selector: 'app-steno-navbar',
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
  imports: [RouterModule, CommonModule],
})
export class StenoNavbar implements OnInit {
  currentTime = '';
  currentDate = '';

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.initializeAuth().catch((error) => {
      console.warn('Auth initialization warning:', error);
    });

    this.updateClock();
    setInterval(() => {
      this.updateClock();
    }, 1000);
  }

  async onLogout(event?: Event): Promise<void> {
    event?.preventDefault();
    const status = await this.authService.logout();
    if (status.success) {
      this.authService.login();
      return;
    }

    this.authService.login();
  }

  private updateClock(): void {
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
