import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink, RouterLinkActive } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { errorText } from '../core/labels';
import { Address, DeviceSession, Favorite, Notice, Page, SupportTicket } from '../core/models';

@Component({
  selector: 'app-account',
  imports: [RouterLink, RouterLinkActive],
  templateUrl: './account.html',
})
export class AccountPage {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  readonly auth = inject(AuthService);
  readonly section = signal('profil');
  readonly error = signal('');
  readonly notice = signal('');
  readonly firstName = signal('');
  readonly lastName = signal('');
  readonly phone = signal('');
  readonly company = signal('');
  readonly addresses = signal<Address[]>([]);
  readonly favorites = signal<Favorite[]>([]);
  readonly notices = signal<Notice[]>([]);
  readonly sessions = signal<DeviceSession[]>([]);
  readonly tickets = signal<SupportTicket[]>([]);
  readonly address = signal({ label: '', city: '', district: '' });
  readonly ticket = signal({ subject: '', description: '', priority: 'normal' });
  readonly deletionReason = signal('');

  constructor() {
    this.route.paramMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      this.section.set(params.get('section') ?? 'profil');
      this.reload();
    });
  }

  reload(): void {
    this.auth.reloadProfile().subscribe({
      next: (profile) => {
        this.firstName.set(profile.first_name ?? '');
        this.lastName.set(profile.last_name ?? '');
        this.phone.set(profile.phone ?? '');
        this.company.set(profile.company_name ?? '');
      },
      error: (err) => this.error.set(errorText(err)),
    });
    if (this.auth.isClient()) {
      this.api.get<Page<Address>>('/locations/addresses/').subscribe({
        next: (page) => this.addresses.set(page.results),
      });
      this.api.get<Favorite[]>('/favorites/').subscribe({
        next: (items) => this.favorites.set(items),
      });
    }
    this.api.get<Notice[]>('/notifications/').subscribe({ next: (items) => this.notices.set(items) });
    this.api.get<DeviceSession[]>('/users/sessions/').subscribe({ next: (items) => this.sessions.set(items) });
    this.api.get<SupportTicket[]>('/support/tickets/').subscribe({ next: (items) => this.tickets.set(items) });
  }

  saveProfile(): void {
    this.auth
      .updateProfile({
        first_name: this.firstName(),
        last_name: this.lastName(),
        phone: this.phone(),
        company_name: this.company(),
      })
      .subscribe({
        next: () => this.notice.set('Compte mis à jour.'),
        error: (err) => this.error.set(errorText(err)),
      });
    if (this.auth.isClient()) {
      this.api.patch('/clients/me/', { company_name: this.company() }).subscribe();
    }
  }

  addAddress(): void {
    this.api.post<Address>('/locations/addresses/', this.address()).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  removeAddress(id: string): void {
    this.api.delete(`/locations/addresses/${id}/`).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  removeFavorite(professional: string): void {
    this.api.delete('/favorites/', { professional }).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  markRead(id: string): void {
    this.api.post(`/notifications/${id}/read/`).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  revoke(id: string): void {
    this.api.delete(`/users/sessions/${id}/`).subscribe({
      next: () => this.reload(),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  openTicket(): void {
    this.api.post('/support/tickets/', this.ticket()).subscribe({
      next: () => {
        this.notice.set('Ticket ouvert.');
        this.reload();
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  grantPrivacy(): void {
    this.api.post('/privacy/consents/', { code: 'privacy', granted: true, version: 'v1' }).subscribe({
      next: () => this.notice.set('Consentement enregistré.'),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  askDeletion(): void {
    this.api.post('/privacy/deletion-requests/', { reason: this.deletionReason() }).subscribe({
      next: () => this.notice.set('Demande de suppression envoyée.'),
      error: (err) => this.error.set(errorText(err)),
    });
  }
}
