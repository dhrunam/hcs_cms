import {
  ApplicationConfig,
  APP_INITIALIZER,
  importProvidersFrom,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimations } from '@angular/platform-browser/animations';
import { OAuthModule } from 'angular-oauth2-oidc';
import { routes } from './app.routes';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { AuthService } from './core/auth/auth.service';

function initializeOAuth(authService: AuthService): () => Promise<boolean> {
  return () => authService.configureOAuth();
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations(),
    importProvidersFrom(OAuthModule.forRoot()),
    {
      provide: APP_INITIALIZER,
      useFactory: initializeOAuth,
      deps: [AuthService],
      multi: true,
    },
  ],
};
