import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../../auth.service';

@Component({
  selector: "app-judge-dashboard",
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: "./dashboard.html",
  styleUrl: "./dashboard.css",
})
export class JudgeDashboard {
  constructor(private authService: AuthService) {}

  async onLogout(event?: Event): Promise<void> {
    event?.preventDefault();
    const status = await this.authService.logout();
    console.log("Logout status:", status);
    if (status.success) {
      alert("You have been logged out successfully.");
      this.authService.login();
      return;
    }

    const issues: string[] = [];
    if (!status.apiSessionLoggedOut) {
      issues.push("API session");
    }
    if (!status.ssoSessionLoggedOut) {
      issues.push("SSO session");
    }
    if (!status.tokensCleared) {
      issues.push("local tokens");
    }

    this.authService.login();
  }
}

