import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { errorText, fcfa, label, WEEKDAYS, zoneLabel } from '../core/labels';
import { Page, ProfessionalCard, ProfessionalDetail, Specialty, Trade, Zone } from '../core/models';

@Component({
  selector: 'app-professionals',
  imports: [RouterLink],
  templateUrl: './professionals.html',
})
export class ProfessionalsPage {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  readonly auth = inject(AuthService);
  readonly trades = signal<Trade[]>([]);
  readonly zones = signal<Zone[]>([]);
  readonly items = signal<ProfessionalCard[]>([]);
  readonly error = signal('');
  readonly trade = signal('');
  readonly zone = signal('');
  readonly zoneLabel = zoneLabel;
  readonly fcfa = fcfa;

  constructor() {
    this.api.get<Page<Trade>>('/catalog/trades/').subscribe({
      next: (page) => this.trades.set(page.results),
    });
    this.api.get<Page<Zone>>('/catalog/zones/').subscribe({
      next: (page) => this.zones.set(page.results.filter((item) => item.is_active)),
    });
    this.route.queryParamMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      this.trade.set(params.get('trade') ?? '');
      this.zone.set(params.get('zone') ?? '');
      this.load();
    });
  }

  load(): void {
    if (!this.auth.isLoggedIn()) {
      this.items.set([]);
      return;
    }
    this.api
      .get<Page<ProfessionalCard>>('/professionals/', { trade: this.trade(), zone: this.zone() })
      .subscribe({
        next: (page) => this.items.set(page.results),
        error: (err) => this.error.set(errorText(err)),
      });
  }
}

@Component({
  selector: 'app-professional-detail',
  templateUrl: './professional-detail.html',
})
export class ProfessionalDetailPage {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  readonly auth = inject(AuthService);
  readonly profile = signal<ProfessionalDetail | null>(null);
  readonly specialties = signal<Specialty[]>([]);
  readonly error = signal('');
  readonly notice = signal('');
  readonly reason = signal('other');
  readonly description = signal('');
  readonly zoneLabel = zoneLabel;
  readonly fcfa = fcfa;
  readonly weekdays = WEEKDAYS;

  constructor() {
    this.route.paramMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      const id = params.get('id');
      if (!id) {
        return;
      }
      this.api.get<ProfessionalDetail>(`/professionals/${id}/`).subscribe({
        next: (profile) => {
          this.profile.set(profile);
          this.api.get<Page<Specialty>>('/catalog/specialties/').subscribe({
            next: (page) => this.specialties.set(page.results),
          });
        },
        error: (err) => this.error.set(errorText(err)),
      });
    });
  }

  tradeName(id: string): string {
    return id;
  }

  specialtyName(id: string | null): string {
    if (!id) {
      return '';
    }
    return this.specialties().find((item) => item.id === id)?.name ?? '';
  }

  saveFavorite(): void {
    const profile = this.profile();
    if (!profile) {
      return;
    }
    this.api.post('/favorites/', { professional: profile.id }).subscribe({
      next: () => this.notice.set('Ajouté à vos favoris.'),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  report(): void {
    const profile = this.profile();
    if (!profile) {
      return;
    }
    this.api
      .post('/moderation/reports/', {
        target_type: 'professional_profile',
        target_id: profile.id,
        reason: this.reason(),
        description: this.description(),
      })
      .subscribe({
        next: () => this.notice.set('Signalement envoyé.'),
        error: (err) => this.error.set(errorText(err)),
      });
  }

  askQuote(): void {
    const profile = this.profile();
    if (!profile) {
      return;
    }
    void this.router.navigate(['/demandes/nouvelle'], { queryParams: { pro: profile.id } });
  }

  statusLabel(value: string): string {
    return label({ published: 'Publiée' }, value);
  }
}
