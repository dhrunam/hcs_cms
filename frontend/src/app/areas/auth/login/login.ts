import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { trigger, transition, style, animate } from '@angular/animations';
import { ToastrService } from 'ngx-toastr';
import { AuthService } from '../../../auth.service';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrls: ['../auth-shell.css', './login.css'],
  animations: [
    trigger('fadeInCard', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(12px)' }),
        animate('420ms cubic-bezier(0.22, 1, 0.36, 1)', style({ opacity: 1, transform: 'translateY(0)' })),
      ]),
    ]),
  ],
})
export class Login implements OnInit {
  isLoading = false;
  authErrorMessage = '';
  submitted = false;

  email = '';
  password = '';
  showPassword = false;

  constructor(
    private authService: AuthService,
    private route: ActivatedRoute,
    private toastr: ToastrService,
  ) {}

  ngOnInit(): void {
    const authError = this.route.snapshot.queryParamMap.get('auth_error');
    const authErrorDescription = this.route.snapshot.queryParamMap.get('auth_error_description');

    if (authError) {
      this.authErrorMessage = authErrorDescription || `Sign-in failed: ${authError}`;
    }

    if (this.route.snapshot.queryParamMap.get('registered') === '1') {
      this.toastr.success('Account created. Sign in with your email and password.');
    }
  }

  get emailInvalid(): boolean {
    return this.submitted && (!this.email.trim() || !EMAIL_RE.test(this.email.trim()));
  }

  async submit(): Promise<void> {
    this.submitted = true;
    this.authErrorMessage = '';
    if (!this.email.trim() || !EMAIL_RE.test(this.email.trim())) {
      this.authErrorMessage = 'Enter a valid email address.';
      return;
    }
    if (!this.password) {
      this.authErrorMessage = 'Password is required.';
      return;
    }

    this.isLoading = true;
    try {
      await this.authService.loginWithPassword(this.email.trim(), this.password);
      await this.authService.navigateToDashboardByRole();
    } catch (err: unknown) {
      const body =
        err && typeof err === 'object' && 'error' in err ? (err as { error?: unknown }).error : null;
      const detail =
        body && typeof body === 'object' && body !== null && 'detail' in body
          ? String((body as { detail?: unknown }).detail)
          : 'Login failed. Check your email and password.';
      this.authErrorMessage = detail;
      this.toastr.error(detail, 'Sign in failed');
    } finally {
      this.isLoading = false;
    }
  }
}
