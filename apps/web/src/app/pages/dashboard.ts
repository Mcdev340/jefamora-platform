import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { BOOKING_STATUS, errorText, label, REQUEST_STATUS } from '../core/labels';
import { Booking, Notice, Page, ServiceRequest } from '../core/models';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink],
  templateUrl: './dashboard.html',
})
export class DashboardPage {
  private readonly api = inject(ApiService);
  readonly auth = inject(AuthService);
  readonly requests = signal<ServiceRequest[]>([]);
  readonly bookings = signal<Booking[]>([]);
  readonly notices = signal<Notice[]>([]);
  readonly error = signal('');
  readonly requestLabel = (value: string) => label(REQUEST_STATUS, value);
  readonly bookingLabel = (value: string) => label(BOOKING_STATUS, value);

  constructor() {
    this.api.get<Page<ServiceRequest>>('/service_requests/').subscribe({
      next: (page) => this.requests.set(page.results),
      error: (err) => this.error.set(errorText(err)),
    });
    this.api.get<Page<Booking>>('/bookings/').subscribe({
      next: (page) => this.bookings.set(page.results),
      error: (err) => this.error.set(errorText(err)),
    });
    this.api.get<Notice[]>('/notifications/').subscribe({
      next: (items) => this.notices.set(items),
    });
  }

  unread(): number {
    return this.notices().filter((item) => !item.is_read).length;
  }

  quotedCount(): number {
    return this.requests().filter((item) => item.status === 'quoted').length;
  }
}
