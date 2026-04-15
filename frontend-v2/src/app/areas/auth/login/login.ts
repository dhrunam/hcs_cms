import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { AuthService } from '../../../auth.service';

/** Reads DRF / SimpleJWT error bodies (`detail` as string or list of strings). */
function messageFromHttpError(err: unknown): string {
  const fallback = 'Login failed. Check your email or phone number and password.';
  if (!(err instanceof HttpErrorResponse)) {
    return err instanceof Error ? err.message : fallback;
  }
  const body = err.error;
  if (body && typeof body === 'object') {
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length) {
      return detail.map((x) => (typeof x === 'string' ? x : String(x))).join(' ');
    }
  }
  if (typeof body === 'string' && body.trim()) {
    return body;
  }
  return fallback;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const PHONE_RE = /^[\d\s\-+()]{8,24}$/;

function isValidLoginIdentifier(raw: string): boolean {
  const t = raw.trim();
  if (!t) return false;
  if (EMAIL_RE.test(t)) return true;
  if (PHONE_RE.test(t)) {
    const digits = t.replace(/\D/g, '');
    return digits.length >= 8;
  }
  return false;
}

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login implements OnInit {
  isLoading = false;
  authErrorMessage = '';
  registeredBanner = false;
  /** Shown after advocate/party registration while account awaits admin ID verification (`is_active=false`). */
  pendingActivationBanner = false;
  submitted = false;

  email = '';
  password = '';
  showPassword = false;

  constructor(
    private authService: AuthService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    const authError = this.route.snapshot.queryParamMap.get('auth_error');
    const authErrorDescription = this.route.snapshot.queryParamMap.get('auth_error_description');

    if (authError) {
      this.authErrorMessage = authErrorDescription || `Sign-in failed: ${authError}`;
    }

    if (this.route.snapshot.queryParamMap.get('registered') === '1') {
      this.registeredBanner = true;
    }

    if (this.route.snapshot.queryParamMap.get('pending_activation') === '1') {
      this.pendingActivationBanner = true;
    }
  }

  get identifierInvalid(): boolean {
    return this.submitted && !isValidLoginIdentifier(this.email);
  }

  async submit(): Promise<void> {
    this.submitted = true;
    this.authErrorMessage = '';
    const id = this.email.trim();
    if (!isValidLoginIdentifier(id)) {
      this.authErrorMessage = 'Enter a valid email address or phone number.';
      return;
    }
    if (!this.password) {
      this.authErrorMessage = 'Password is required.';
      return;
    }

    this.isLoading = true;
    try {
      await this.authService.loginWithPassword(id, this.password);
      await this.authService.navigateToDashboardByRole();
    } catch (err: any) {
      console.log(err.error.detail[0]);
      this.authErrorMessage = messageFromHttpError(err);
    } finally {
      this.isLoading = false;
    }
  }
}
