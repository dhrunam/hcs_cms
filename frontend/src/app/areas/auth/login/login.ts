import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
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
    private router: Router,
  ) {
    const role = window.sessionStorage.getItem('user_group');
    switch (role) {
      case 'API_ADVOCATE':
        this.router.navigate(['/advocate/dashboard/home']);
        break;
      case 'API_SCRUTINY_OFFICER':
        this.router.navigate(['/scrutiny-officers/dashboard/home']);
        break;
      case 'API_COURT_READER':
        this.router.navigate(['/reader/dashboard/home']);
        break;
      case 'API_LISTING_OFFICER':
        this.router.navigate(['/listing-officers/dashboard/home']);
        break;
      case 'API_JUDGE':
        this.router.navigate(['/judge/dashboard/home']);
        break;
      case 'API_STENOGRAPHER':
        this.router.navigate(['/steno/dashboard/home']);
        break;
    }
  }

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
