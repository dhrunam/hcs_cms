import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  isLoading = false;
  authErrorMessage = '';

  constructor(
    private authService: AuthService,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    const authError = this.route.snapshot.queryParamMap.get('auth_error');
    const authErrorDescription = this.route.snapshot.queryParamMap.get('auth_error_description');

    if (!authError) {
      return;
    }

    this.authErrorMessage = authErrorDescription || `SSO login failed: ${authError}`;
  }

  submit(): void {
    this.isLoading = true;
    this.authService.login();
  }
}
