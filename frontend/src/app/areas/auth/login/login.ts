import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  form: FormGroup;

  isLoading = false;
  authError = '';

  constructor(
    private fb: FormBuilder,
    private router: Router,
  ) {
    this.form = this.fb.group({
      phone: ['', [Validators.required, Validators.pattern(/^[0-9]{10}$/)]],
      password: ['', [Validators.required]],
    });
  }

  async submit() {
    this.authError = '';
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const phone = String(this.form.value.phone || '').trim();
    const password = String(this.form.value.password || '');

    this.isLoading = true;

    // simulate a short network delay for UX
    await new Promise((r) => setTimeout(r, 700));

    // Static credentials
    if (phone === '7584060563' && password === 'Advocate@123') {
      sessionStorage.setItem('access_token', 'advocate_dummy_token');
      sessionStorage.setItem('user_groups', JSON.stringify(['advocate']));
      sessionStorage.setItem('user_group', 'advocate');
      this.router.navigate(['/advocate/dashboard/home']);
      return;
    }

    if (phone === '8178429427' && password === 'Scrutiny@123') {
      sessionStorage.setItem('access_token', 'scrutiny_dummy_token');
      sessionStorage.setItem('user_groups', JSON.stringify(['scrutiny']));
      sessionStorage.setItem('user_group', 'scrutiny');
      this.router.navigate(['/scrutiny-officers/dashboard/home']);
      return;
    }

    if (phone === '9000000001' && password === 'Listing@123') {
      sessionStorage.setItem('access_token', 'listing_dummy_token');
      sessionStorage.setItem('user_groups', JSON.stringify(['listing']));
      sessionStorage.setItem('user_group', 'listing');
      this.router.navigate(['/listing-officers/dashboard/home']);
      return;
    }

    this.isLoading = false;
    this.authError = 'Invalid phone number or password.';
  }
}
