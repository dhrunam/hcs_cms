import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import {
  RegistrationService,
  formatRegistrationError,
} from '../../../services/registration.service';
import { REGISTRATION_OTP } from '../registration-otp.constants';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

@Component({
  selector: 'app-register-party',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register-party.html',
})
export class RegisterParty {
  private registration = inject(RegistrationService);
  private router = inject(Router);

  registrationStep: 'form' | 'otp' = 'form';
  otpInput = '';
  otpError = '';

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

  submitted = false;

  goToOtpStep(): void {
    this.submitted = true;
    this.formError = '';
    const err = this.clientErrors();
    if (err) {
      this.formError = err;
      return;
    }
    this.otpError = '';
    this.otpInput = '';
    this.registrationStep = 'otp';
  }

  backToForm(): void {
    this.registrationStep = 'form';
    this.otpError = '';
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
    return null;
  }

  completeRegistration(): void {
    this.otpError = '';
    this.formError = '';
    const entered = this.otpInput.trim();
    if (!entered) {
      this.otpError = 'Enter the OTP to complete registration.';
      return;
    }
    if (entered !== REGISTRATION_OTP) {
      this.otpError = 'Invalid OTP. Try again.';
      return;
    }

    const err = this.clientErrors();
    if (err) {
      this.formError = err;
      this.registrationStep = 'form';
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

    this.isLoading = true;
    this.registration.registerParty(fd).subscribe({
      next: (res) => {
        this.isLoading = false;
        if (res.email_verification_required) {
          if (res.verification_token) {
            void this.router.navigate(['/user/verify-email'], {
              queryParams: { token: res.verification_token },
            });
            return;
          }
          void this.router.navigate(['/user/verify-email']);
          return;
        }
        if (res.requires_admin_activation) {
          void this.router.navigate(['/user/login'], { queryParams: { pending_activation: '1' } });
          return;
        }
        void this.router.navigate(['/user/login'], { queryParams: { registered: '1' } });
      },
      error: (e: unknown) => {
        this.isLoading = false;
        this.formError = formatRegistrationError(e);
      },
    });
  }
}
