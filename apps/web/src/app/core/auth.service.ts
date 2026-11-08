import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { Profile, Tokens } from './models';

interface Session extends Tokens {
  profile: Profile;
}

const STORAGE_KEY = 'jefamora.session';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly session = signal<Session | null>(this.read());

  readonly profile = computed(() => this.session()?.profile ?? null);
  readonly isLoggedIn = computed(() => Boolean(this.session()?.access));
  readonly isClient = computed(() => this.profile()?.role === 'client');
  readonly isProfessional = computed(() => this.profile()?.role === 'professional');

  accessToken(): string | null {
    return this.session()?.access ?? null;
  }

  refreshToken(): string | null {
    return this.session()?.refresh ?? null;
  }

  register(payload: Record<string, unknown>): Observable<{ email: string; message: string }> {
    return this.http.post<{ email: string; message: string }>('/api/v1/users/register/', payload);
  }

  verify(email: string, code: string): Observable<Session> {
    return this.http
      .post<Session>('/api/v1/users/verify-email/', { email, code })
      .pipe(tap((value) => this.store(value)));
  }

  login(email: string, password: string): Observable<Session> {
    return this.http
      .post<Session>('/api/v1/users/login/', { email, password })
      .pipe(tap((value) => this.store(value)));
  }

  refreshAccess(): Observable<Tokens> {
    return this.http.post<Tokens>('/api/v1/users/refresh/', { refresh: this.refreshToken() }).pipe(
      tap((tokens) => {
        const current = this.session();
        if (current) {
          this.store({ ...current, ...tokens });
        }
      }),
    );
  }

  logout(): Observable<unknown> {
    const refresh = this.refreshToken();
    this.clear();
    return this.http.post('/api/v1/users/logout/', { refresh });
  }

  requestReset(email: string): Observable<{ message?: string }> {
    return this.http.post<{ message?: string }>('/api/v1/users/password-reset/', { email });
  }

  confirmReset(email: string, code: string, password: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>('/api/v1/users/password-reset/confirm/', {
      email,
      code,
      password,
    });
  }

  reloadProfile(): Observable<Profile> {
    return this.http.get<Profile>('/api/v1/users/me/').pipe(
      tap((profile) => {
        const current = this.session();
        if (current) {
          this.store({ ...current, profile });
        }
      }),
    );
  }

  updateProfile(body: Partial<Profile>): Observable<Profile> {
    return this.http.patch<Profile>('/api/v1/users/me/', body).pipe(
      tap((profile) => {
        const current = this.session();
        if (current) {
          this.store({ ...current, profile });
        }
      }),
    );
  }

  clear(): void {
    this.session.set(null);
    localStorage.removeItem(STORAGE_KEY);
  }

  private store(value: Session): void {
    this.session.set(value);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  }

  private read(): Session | null {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as Session;
    } catch {
      return null;
    }
  }
}
