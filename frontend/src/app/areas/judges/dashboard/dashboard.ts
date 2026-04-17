import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../../auth.service';

@Component({
  selector: "app-judge-dashboard",
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: "./dashboard.html",
  styleUrl: "./dashboard.css",
})
export class JudgeDashboard implements OnInit {
  judgeDisplayName = '';

  constructor(private authService: AuthService) {}

  async ngOnInit(): Promise<void> {
    await this.authService.initializeAuth().catch(() => undefined);
    this.judgeDisplayName = this.authService.getSessionProfile()?.displayName?.trim() ?? '';
  }

  get judgeHeaderTitle(): string {
    return this.judgeDisplayName
      ? `Hon'ble Judge, ${this.judgeDisplayName}`
      : "Hon'ble Judge";
  }

  async onLogout(event?: Event): Promise<void> {
    event?.preventDefault();
    const status = await this.authService.logout();
    console.log("Logout status:", status);
    if (status.success) {
      this.authService.login();
      return;
    }

    const issues: string[] = [];
    if (!status.apiSessionLoggedOut) {
      issues.push("API session");
    }
    if (!status.refreshBlacklisted) {
      issues.push("refresh token revocation");
    }
    if (!status.tokensCleared) {
      issues.push("local tokens");
    }

    console.warn("Logout partially completed:", issues.join(", "));
    this.authService.login();
  }
}

