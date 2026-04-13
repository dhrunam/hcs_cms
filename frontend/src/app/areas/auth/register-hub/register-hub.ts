import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-register-hub',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './register-hub.html',
  styleUrls: ['../auth-shell.css', './register-hub.css'],
})
export class RegisterHub {}
