import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { BOOKING_STATUS, errorText, label } from '../core/labels';
import { Booking, ChatMessage, Page, Review } from '../core/models';

@Component({
  selector: 'app-bookings',
  imports: [RouterLink, DatePipe],
  templateUrl: './bookings.html',
})
export class BookingsPage {
  private readonly api = inject(ApiService);
  readonly items = signal<Booking[]>([]);
  readonly error = signal('');
  readonly statusLabel = (value: string) => label(BOOKING_STATUS, value);

  constructor() {
    this.api.get<Page<Booking>>('/bookings/').subscribe({
      next: (page) => this.items.set(page.results),
      error: (err) => this.error.set(errorText(err)),
    });
  }
}

@Component({
  selector: 'app-booking-detail',
  imports: [DatePipe],
  templateUrl: './booking-detail.html',
})
export class BookingDetailPage {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  readonly auth = inject(AuthService);
  readonly booking = signal<Booking | null>(null);
  readonly messages = signal<ChatMessage[]>([]);
  readonly review = signal<Review | null>(null);
  readonly draft = signal('');
  readonly rating = signal(5);
  readonly comment = signal('');
  readonly reply = signal('');
  readonly dispute = signal('');
  readonly disputeId = signal('');
  readonly error = signal('');
  readonly notice = signal('');
  readonly statusLabel = (value: string) => label(BOOKING_STATUS, value);

  constructor() {
    this.route.paramMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      const id = params.get('id');
      if (id) {
        this.load(id);
      }
    });
  }

  load(id: string): void {
    this.api.get<Booking>(`/bookings/${id}/`).subscribe({
      next: (booking) => {
        this.booking.set(booking);
        if (booking.review) {
          this.review.set(booking.review);
          this.rating.set(booking.review.rating);
          this.comment.set(booking.review.comment);
        }
        if (booking.conversation_id) {
          this.api.get<ChatMessage[]>(`/messaging/${booking.conversation_id}/messages/`).subscribe({
            next: (messages) => this.messages.set(messages),
            error: (err) => this.error.set(errorText(err)),
          });
        }
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  act(path: string): void {
    const booking = this.booking();
    if (!booking) {
      return;
    }
    this.api.post<Booking>(`/bookings/${booking.id}/${path}/`).subscribe({
      next: () => this.load(booking.id),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  send(): void {
    const booking = this.booking();
    const content = this.draft().trim();
    if (!booking?.conversation_id || !content) {
      return;
    }
    this.api.post<ChatMessage>(`/messaging/${booking.conversation_id}/messages/`, { content }).subscribe({
      next: () => {
        this.draft.set('');
        this.load(booking.id);
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  publishReview(): void {
    const booking = this.booking();
    if (!booking) {
      return;
    }
    this.api
      .post<Review>('/reviews/', { booking: booking.id, rating: this.rating(), comment: this.comment() })
      .subscribe({
        next: (review) => {
          this.review.set(review);
          this.notice.set('Avis publié.');
        },
        error: (err) => this.error.set(errorText(err)),
      });
  }

  sendReply(): void {
    const current = this.review();
    if (!current) {
      return;
    }
    this.api.patch<Review>(`/reviews/${current.id}/`, { professional_reply: this.reply() }).subscribe({
      next: (review) => this.review.set(review),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  openDispute(): void {
    const booking = this.booking();
    if (!booking) {
      return;
    }
    this.api.post<{ id: string }>(`/bookings/${booking.id}/disputes/`, { description: this.dispute() }).subscribe({
      next: (created) => {
        this.disputeId.set(created.id);
        this.notice.set('Litige ouvert. Vous pouvez joindre une preuve.');
        this.load(booking.id);
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  addEvidence(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    const id = this.disputeId();
    if (!file || !id) {
      return;
    }
    this.api.upload(`/support/disputes/${id}/evidence/`, file).subscribe({
      next: () => this.notice.set('Preuve ajoutée.'),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  mine(sender: string): boolean {
    return sender === this.auth.profile()?.id;
  }

  canEditReview(): boolean {
    const until = this.review()?.editable_until;
    return Boolean(until && new Date(until).getTime() > Date.now());
  }

  saveReview(): void {
    const current = this.review();
    if (!current) {
      this.publishReview();
      return;
    }
    this.api.patch<Review>(`/reviews/${current.id}/`, { rating: this.rating(), comment: this.comment() }).subscribe({
      next: (review) => {
        this.review.set(review);
        this.notice.set('Avis mis à jour.');
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }
}
