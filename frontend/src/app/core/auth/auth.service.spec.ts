import { TestBed } from '@angular/core/testing';
import { OAuthService, OAuthModule } from 'angular-oauth2-oidc';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

describe('AuthService', () => {
  let service: AuthService;
  let oauthServiceSpy: jasmine.SpyObj<OAuthService>;

  beforeEach(() => {
    const spy = jasmine.createSpyObj('OAuthService', [
      'configure',
      'setupAutomaticSilentRefresh',
      'loadDiscoveryDocumentAndTryLogin',
      'initCodeFlow',
      'revokeTokenAndLogout',
      'logOut',
      'hasValidAccessToken',
      'getAccessToken',
      'getIdentityClaims',
    ]);
    spy.loadDiscoveryDocumentAndTryLogin.and.returnValue(Promise.resolve(true));

    TestBed.configureTestingModule({
      imports: [OAuthModule.forRoot()],
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: OAuthService, useValue: spy },
      ],
    });

    service = TestBed.inject(AuthService);
    oauthServiceSpy = TestBed.inject(OAuthService) as jasmine.SpyObj<OAuthService>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should call initCodeFlow on login', () => {
    service.login();
    expect(oauthServiceSpy.initCodeFlow).toHaveBeenCalled();
  });

  it('should return false when not authenticated', () => {
    oauthServiceSpy.hasValidAccessToken.and.returnValue(false);
    expect(service.isAuthenticated()).toBeFalse();
  });

  it('should return true when authenticated', () => {
    oauthServiceSpy.hasValidAccessToken.and.returnValue(true);
    expect(service.isAuthenticated()).toBeTrue();
  });

  it('should return the access token', () => {
    oauthServiceSpy.getAccessToken.and.returnValue('test-token');
    expect(service.getAccessToken()).toBe('test-token');
  });

  it('should return user name from identity claims', () => {
    oauthServiceSpy.getIdentityClaims.and.returnValue({ name: 'John Doe', email: 'john@example.com' });
    expect(service.getUserName()).toBe('John Doe');
  });

  it('should return empty string when no identity claims', () => {
    oauthServiceSpy.getIdentityClaims.and.returnValue(null);
    expect(service.getUserName()).toBe('');
  });
});
