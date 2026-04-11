import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import {
  RegistrationService,
  formatRegistrationError,
} from '../../../services/registration.service';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

@Component({
  selector: 'app-register-advocate',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register-advocate.html',
  styleUrls: ['../auth-shell.css', './register-advocate.css'],
})
export class RegisterAdvocate {
  private registration = inject(RegistrationService);
  private router = inject(Router);
  private toastr = inject(ToastrService);

  isLoading = false;
  formError = '';
  showPassword = false;
  showPassword2 = false;

  email = '';
  password = '';
  passwordConfirm = '';
  first_name = '';
  last_name = '';
  phone_number = '';
  date_of_birth = '';
  address = '';
  gender: 'M' | 'F' | 'O' | 'U' = 'U';
  bar_id = '';
  bar_id_file: File | null = null;

  submitted = false;

  onBarFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    const f = input.files?.[0];
    this.bar_id_file = f ?? null;
  }

  private clientErrors(): string | null {
    if (!this.email.trim()) return 'Email is required.';
    if (!EMAIL_RE.test(this.email.trim())) return 'Enter a valid email address.';
    if (!this.password) return 'Password is required.';
    if (this.password.length < 8) return 'Password must be at least 8 characters.';
    if (this.password !== this.passwordConfirm) return 'Passwords do not match.';
    if (!this.first_name.trim() || !this.last_name.trim()) return 'First and last name are required.';
    if (!this.phone_number.trim()) return 'Phone number is required.';
    if (!this.date_of_birth) return 'Date of birth is required.';
    if (!this.address.trim()) return 'Address is required.';
    if (!this.bar_id.trim()) return 'Bar ID is required.';
    if (!this.bar_id_file) return 'Bar ID document is required.';
    return null;
  }

  submit(): void {
    this.submitted = true;
    this.formError = '';
    const err = this.clientErrors();
    if (err) {
      this.formError = err;
      return;
    }

    const fd = new FormData();
    fd.append('email', this.email.trim());
    fd.append('password', this.password);
    fd.append('first_name', this.first_name.trim());
    fd.append('last_name', this.last_name.trim());
    fd.append('phone_number', this.phone_number.trim());
    fd.append('date_of_birth', this.date_of_birth);
    fd.append('address', this.address.trim());
    fd.append('gender', this.gender);
    fd.append('bar_id', this.bar_id.trim());
    fd.append('bar_id_file', this.bar_id_file!, this.bar_id_file!.name);

    this.isLoading = true;
    this.registration.registerAdvocate(fd).subscribe({
      next: (res) => {
        this.isLoading = false;
        if (res.email_verification_required) {
          if (res.verification_token) {
            this.router.navigate(['/user/verify-email'], {
              queryParams: { token: res.verification_token },
            });
            return;
          }
          this.toastr.info('Check your email for a verification link.');
          this.router.navigate(['/user/verify-email']);
          return;
        }
        this.toastr.success('Registration successful. You can sign in now.');
        this.router.navigate(['/user/login'], { queryParams: { registered: '1' } });
      },
      error: (e: unknown) => {
        this.isLoading = false;
        this.formError = formatRegistrationError(e);
      },
    });
  }
}
