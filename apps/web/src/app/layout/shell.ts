import { Component, computed, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';

import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-shell',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './shell.html',
  host: {
    class: 'shell',
    '[class.on-home]': 'onHome()',
    '[class.on-auth]': 'onAuth()',
  },
})
export class Shell {
  readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly path = signal(this.router.url);
  readonly onHome = computed(() => {
    const path = this.path().split(/[?#]/)[0];
    return path === '/' || path === '';
  });
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

  leave(): void {
    this.auth.logout().subscribe({
      complete: () => void this.router.navigate(['/']),
      error: () => void this.router.navigate(['/']),
    });
  }
}
