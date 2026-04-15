import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import {
  RegistrationService,
  formatRegistrationError,
} from '../../../services/registration.service';

@Component({
  selector: 'app-verify-email',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './verify-email.html',
})
export class VerifyEmail implements OnInit {
  private route = inject(ActivatedRoute);
  private registration = inject(RegistrationService);

  tokenInput = '';
  isLoading = false;
  formError = '';
  successMessage = '';

  ngOnInit(): void {
    const t = this.route.snapshot.queryParamMap.get('token')?.trim();
    if (t) {
      this.tokenInput = t;
      this.verify(t);
    }
  }

  verify(token?: string): void {
    const t = (token ?? this.tokenInput).trim();
    this.formError = '';
    this.successMessage = '';
    if (!t) {
      this.formError = 'Enter the verification token from your email.';
      return;
    }
    this.isLoading = true;
    this.registration.verifyEmail(t).subscribe({
      next: (res) => {
        this.isLoading = false;
        this.successMessage = res.detail || 'Email verified successfully.';
      },
      error: (e: unknown) => {
        this.isLoading = false;
        this.formError = formatRegistrationError(e);
      },
    });
  }
}
