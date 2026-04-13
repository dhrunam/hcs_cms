import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Navbar } from './navbar';
import { AuthService } from '../../../../auth.service';

describe('Navbar', () => {
  let component: Navbar;
  let fixture: ComponentFixture<Navbar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Navbar],
      providers: [
        {
          provide: AuthService,
          useValue: {
            initializeAuth: () => Promise.resolve(),
            isLoggedIn: () => false,
            login: () => {},
            logout: () =>
              Promise.resolve({
                apiSessionLoggedOut: true,
                refreshBlacklisted: true,
                tokensCleared: true,
                success: true,
              }),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(Navbar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
