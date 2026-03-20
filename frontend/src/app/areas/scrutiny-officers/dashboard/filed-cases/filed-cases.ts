import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ActivatedRoute, NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';

@Component({
  selector: 'app-filed-cases',
  standalone: true,
  imports: [CommonModule, RouterOutlet],
  templateUrl: './filed-cases.html',
  styleUrls: ['./filed-cases.css'],
})
export class FiledCases {
  pageTitle = 'Filed Cases';

  constructor(
    private router: Router,
    private route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.updatePageTitle();
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => this.updatePageTitle());
  }

  private updatePageTitle(): void {
    let currentRoute = this.route.firstChild;

    while (currentRoute?.firstChild) {
      currentRoute = currentRoute.firstChild;
    }

    const routeTitle = currentRoute?.snapshot.title ?? '';
    this.pageTitle = routeTitle.replace(' | CMS', '').trim() || 'Filed Cases';
  }
}
