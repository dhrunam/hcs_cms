import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { AuthService } from '../../../../auth.service';

@Component({
  selector: "app-navbar",
  templateUrl: "./navbar.html",
  styleUrl: "./navbar.css",
  imports: [RouterModule, CommonModule],
})
export class Navbar implements OnInit {
  currentTime: string = "";
  currentDate: string = "";

  constructor(
    private authService: AuthService,
    private toastr: ToastrService,
  ) {}

  ngOnInit() {
    this.authService.initializeAuth().catch((error) => {
      console.warn("Auth initialization warning:", error);
    });

    this.updateClock();
    setInterval(() => {
      this.updateClock();
    }, 1000);
  }

  isLoggedIn(): boolean {
    return this.authService.isLoggedIn();
  }

  onLogin(event: Event): void {
    event.preventDefault();
    this.authService.login();
  }

  // async onLogout(event: Event): Promise<void> {
  //   event.preventDefault();
  //   const status = await this.authService.logout();

  //   if (status.success) {
  //     this.toastr.success('Logged out from both API and SSO sessions.');
  //     return;
  //   }

  //   const issues: string[] = [];
  //   if (!status.apiSessionLoggedOut) {
  //     issues.push('API session');
  //   }
  //   if (!status.refreshBlacklisted) {
  //     issues.push('SSO session');
  //   }
  //   if (!status.tokensCleared) {
  //     issues.push('local tokens');
  //   }

  //   this.toastr.warning(
  //     `Logout partially completed. Check: ${issues.join(', ')}.`,
  //     'Logout Verification',
  //     { closeButton: true },
  //   );
  // }

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
    if (!status.refreshBlacklisted) {
      issues.push("refresh token revocation");
    }
    if (!status.tokensCleared) {
      issues.push("local tokens");
    }

    this.toastr.warning(
      `Logout partially completed. Check: ${issues.join(", ")}.`,
      "Logout Verification",
      { closeButton: true },
    );
    this.authService.login();
  }

  updateClock() {
    const now = new Date();

    this.currentTime = now.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    });

    this.currentDate = now.toLocaleDateString("en-IN", {
      weekday: "short",
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }
}
