import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';

import { AuthService } from '../core/auth.service';

const THEME_KEY = 'jefamora.theme';

@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './shell.html',
  host: {
    class: 'shell',
    '[class.on-home]': 'onHome()',
    '[class.on-auth]': 'onAuth()',
    '[class.on-wide]': 'wide()',
  },
})
export class Shell {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly path = signal(this.router.url);
  readonly dark = signal(document.documentElement.classList.contains('dark'));
  readonly onHome = computed(() => {
    const path = this.path().split(/[?#]/)[0];
    return path === '/' || path === '';
  });
  readonly wide = computed(() =>
    ['/', '/a-propos', '/services', '/fonctionnalites', '/contact'].includes(this.path().split(/[?#]/)[0]),
  );
  readonly onAuth = computed(() => {
    const path = this.path().split(/[?#]/)[0];
    return path === '/connexion' || path === '/inscription';
  });

  constructor() {
    this.router.events
      .pipe(
        filter((event) => event instanceof NavigationEnd),
        takeUntilDestroyed(),
      )
      .subscribe(() => this.path.set(this.router.url));
  }

  toggleTheme(): void {
    const dark = !this.dark();
    this.dark.set(dark);
    document.documentElement.classList.toggle('dark', dark);
    localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light');
  }

  leave(): void {
    this.auth.logout().subscribe({
      complete: () => void this.router.navigate(['/']),
      error: () => void this.router.navigate(['/']),
    });
  }
}
