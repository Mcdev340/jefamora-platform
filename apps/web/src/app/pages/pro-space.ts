import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { errorText, fcfa, WEEKDAYS, zoneLabel } from '../core/labels';
import { Availability, Page, PortfolioItem, ProService, Specialty, Trade, VerificationCase, Zone } from '../core/models';

@Component({
  selector: 'app-pro-space',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './pro-space.html',
})
export class ProSpacePage {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  readonly auth = inject(AuthService);
  readonly section = signal('profil');
  readonly error = signal('');
  readonly notice = signal('');
  readonly trades = signal<Trade[]>([]);
  readonly specialties = signal<Specialty[]>([]);
  readonly zones = signal<Zone[]>([]);
  readonly services = signal<ProService[]>([]);
  readonly slots = signal<Availability[]>([]);
  readonly works = signal<PortfolioItem[]>([]);
  readonly verification = signal<VerificationCase | null>(null);
  readonly selectedZones = signal<string[]>([]);
  readonly biography = signal('');
  readonly years = signal('');
  readonly businessName = signal('');
  readonly weekdays = WEEKDAYS;
  readonly zoneLabel = zoneLabel;
  readonly fcfa = fcfa;
  readonly serviceDraft = signal({ trade: '', specialty: '', title: '', description: '', starting_price: '' });
  readonly slotDraft = signal({ weekday: '0', start_time: '08:00', end_time: '18:00' });
  readonly workDraft = signal({ trade: '', specialty: '', zone: '', title: '', description: '' });

  constructor() {
    this.route.paramMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      this.section.set(params.get('section') ?? 'profil');
    });
    this.api.get<Page<Trade>>('/catalog/trades/').subscribe({ next: (page) => this.trades.set(page.results) });
    this.api.get<Page<Specialty>>('/catalog/specialties/').subscribe({ next: (page) => this.specialties.set(page.results) });
    this.api.get<Page<Zone>>('/catalog/zones/').subscribe({
      next: (page) => this.zones.set(page.results.filter((item) => item.is_active)),
    });
    this.reload();
  }

  reload(): void {
    this.auth.reloadProfile().subscribe({
      next: (profile) => {
        this.businessName.set(profile.business_name ?? '');
      },
    });
    this.api.get<Record<string, unknown>>('/professionals/me/').subscribe({
      next: (profile) => {
        this.biography.set(String(profile['biography'] ?? ''));
        this.years.set(profile['years_of_experience'] == null ? '' : String(profile['years_of_experience']));
        this.businessName.set(String(profile['business_name'] ?? ''));
        const zones = (profile['zones'] as Zone[] | undefined) ?? [];
        this.selectedZones.set(zones.map((item) => item.id));
      },
      error: (err) => this.error.set(errorText(err)),
    });
    this.api.get<Page<ProService> | ProService[]>('/professionals/me/services/').subscribe({
      next: (payload) => this.services.set(Array.isArray(payload) ? payload : payload.results),
    });
    this.api.get<Page<Availability> | Availability[]>('/professionals/me/availabilities/').subscribe({
      next: (payload) => this.slots.set(Array.isArray(payload) ? payload : payload.results),
    });
    this.api.get<Page<PortfolioItem> | PortfolioItem[]>('/portfolio/').subscribe({
      next: (payload) => this.works.set(Array.isArray(payload) ? payload : payload.results),
    });
    this.api.get<VerificationCase>('/verification/').subscribe({
      next: (item) => this.verification.set(item),
    });
  }

  saveProfile(): void {
    this.api
      .patch('/professionals/me/', {
        business_name: this.businessName(),
        biography: this.biography(),
        years_of_experience: this.years() ? Number(this.years()) : null,
      })
      .subscribe({
        next: () => this.notice.set('Profil enregistré.'),
        error: (err) => this.error.set(errorText(err)),
      });
  }

  toggleZone(id: string, checked: boolean): void {
    const next = new Set(this.selectedZones());
    if (checked) {
      next.add(id);
    } else {
      next.delete(id);
    }
    this.selectedZones.set([...next]);
  }

  saveZones(): void {
    this.api.put('/professionals/me/zones/', { zone_ids: this.selectedZones() }).subscribe({
      next: () => this.notice.set('Zones enregistrées.'),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  addService(): void {
    const draft = this.serviceDraft();
    this.api
      .post('/professionals/me/services/', {
        ...draft,
        specialty: draft.specialty || null,
        is_active: true,
      })
      .subscribe({
        next: () => this.reload(),
        error: (err) => this.error.set(errorText(err)),
      });
  }

  removeService(id: string): void {
    this.api.delete(`/professionals/me/services/${id}/`).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  addSlot(): void {
    const draft = this.slotDraft();
    this.api
      .post('/professionals/me/availabilities/', {
        weekday: Number(draft.weekday),
        start_time: draft.start_time,
        end_time: draft.end_time,
        is_available: true,
      })
      .subscribe({
        next: () => this.reload(),
        error: (err) => this.error.set(errorText(err)),
      });
  }

  removeSlot(id: string): void {
    this.api.delete(`/professionals/me/availabilities/${id}/`).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  addWork(): void {
    const draft = this.workDraft();
    this.api
      .post('/portfolio/', {
        trade: draft.trade,
        specialty: draft.specialty || null,
        zone: draft.zone || null,
        title: draft.title,
        description: draft.description,
      })
      .subscribe({
        next: () => this.reload(),
        error: (err) => this.error.set(errorText(err)),
      });
  }

  uploadMedia(itemId: string, event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) {
      return;
    }
    this.api.upload(`/portfolio/${itemId}/media/`, file, { media_type: 'image' }).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  publish(itemId: string): void {
    this.api.post(`/portfolio/${itemId}/publish/`).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  uploadId(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) {
      return;
    }
    this.api.upload('/verification/', file, { document_type: 'national_id' }).subscribe({
      next: () => {
        this.notice.set('Pièce envoyée. Soumettez ensuite le dossier.');
        this.reload();
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  submitCase(): void {
    this.api.post('/verification/', {}).subscribe({
      next: () => {
        this.notice.set('Dossier soumis.');
        this.reload();
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  patchService(field: string, value: string): void {
    this.serviceDraft.update((current) => ({ ...current, [field]: value }));
  }

  patchSlot(field: string, value: string): void {
    this.slotDraft.update((current) => ({ ...current, [field]: value }));
  }

  patchWork(field: string, value: string): void {
    this.workDraft.update((current) => ({ ...current, [field]: value }));
  }
}
