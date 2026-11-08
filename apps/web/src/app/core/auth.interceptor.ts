import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, finalize, shareReplay, switchMap, throwError } from 'rxjs';

import { AuthService } from './auth.service';

let refreshing: ReturnType<AuthService['refreshAccess']> | null = null;

function isPublicAuth(url: string): boolean {
  return (
    url.includes('/users/login') ||
    url.includes('/users/register') ||
    url.includes('/users/verify-email') ||
    url.includes('/users/refresh') ||
    url.includes('/users/password-reset') ||
    url.includes('/users/logout')
  );
}

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const token = isPublicAuth(req.url) ? null : auth.accessToken();
  const outgoing = token ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } }) : req;

  return next(outgoing).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status !== 401 || isPublicAuth(req.url) || !auth.refreshToken()) {
        return throwError(() => error);
      }
      if (!refreshing) {
        refreshing = auth.refreshAccess().pipe(
          finalize(() => {
            refreshing = null;
          }),
          shareReplay(1),
        );
      }
      return refreshing.pipe(
        switchMap((tokens) => next(req.clone({ setHeaders: { Authorization: `Bearer ${tokens.access}` } }))),
        catchError((refreshError: HttpErrorResponse) => {
          auth.clear();
          void router.navigate(['/connexion']);
          return throwError(() => refreshError);
        }),
      );
    }),
  );
};
