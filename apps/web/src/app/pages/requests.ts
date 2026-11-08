import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { errorText, fcfa, label, QUOTE_STATUS, RECIPIENT_STATUS, REQUEST_STATUS, URGENCY, zoneLabel } from '../core/labels';
import { Page, ProfessionalCard, Quote, ServiceRequest, Zone } from '../core/models';

@Component({
  selector: 'app-requests',
  imports: [RouterLink],
  templateUrl: './requests.html',
})
export class RequestsPage {
  private readonly api = inject(ApiService);
  readonly auth = inject(AuthService);
  readonly items = signal<ServiceRequest[]>([]);
  readonly error = signal('');
  readonly statusLabel = (value: string) => label(REQUEST_STATUS, value);

  constructor() {
    this.api.get<Page<ServiceRequest>>('/service_requests/').subscribe({
      next: (page) => this.items.set(page.results),
      error: (err) => this.error.set(errorText(err)),
    });
  }
}

@Component({
  selector: 'app-request-form',
  imports: [ReactiveFormsModule],
  templateUrl: './request-form.html',
})
export class RequestFormPage {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly formBuilder = inject(FormBuilder);
  readonly zones = signal<Zone[]>([]);
  readonly professionals = signal<ProfessionalCard[]>([]);
  readonly selected = signal<string[]>(this.initialPros());
  readonly error = signal('');
  readonly zoneLabel = zoneLabel;
  readonly form = this.formBuilder.nonNullable.group({
    zone: ['', Validators.required],
    title: ['', Validators.required],
    description: ['', Validators.required],
    urgency: ['normal'],
    budget: [''],
    desired_date: [''],
  });

  constructor() {
    this.api.get<Page<Zone>>('/catalog/zones/').subscribe({
      next: (page) => this.zones.set(page.results.filter((item) => item.is_active)),
    });
    this.api.get<Page<ProfessionalCard>>('/professionals/').subscribe({
      next: (page) => this.professionals.set(page.results),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  private initialPros(): string[] {
    const pro = this.route.snapshot.queryParamMap.get('pro');
    return pro ? [pro] : [];
  }

  toggle(id: string, checked: boolean): void {
    const current = new Set(this.selected());
    if (checked) {
      current.add(id);
    } else {
      current.delete(id);
    }
    this.selected.set([...current]);
  }

  submit(): void {
    if (this.form.invalid || this.selected().length === 0) {
      this.error.set('Choisissez une zone, un titre et au moins un professionnel.');
      return;
    }
    const value = this.form.getRawValue();
    this.api
      .post<ServiceRequest>('/service_requests/', {
        zone: value.zone,
        title: value.title,
        description: value.description,
        urgency: value.urgency,
        budget: value.budget ? value.budget : null,
        desired_date: value.desired_date ? new Date(value.desired_date).toISOString() : null,
        professional_ids: this.selected(),
      })
      .subscribe({
        next: (created) => void this.router.navigate(['/demandes', created.id]),
        error: (err) => this.error.set(errorText(err)),
      });
  }
}

@Component({
  selector: 'app-request-detail',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './request-detail.html',
})
export class RequestDetailPage {
  private readonly api = inject(ApiService);
  private readonly route = inject(ActivatedRoute);
  private readonly formBuilder = inject(FormBuilder);
  readonly auth = inject(AuthService);
  readonly item = signal<ServiceRequest | null>(null);
  readonly quotes = signal<Quote[]>([]);
  readonly error = signal('');
  readonly notice = signal('');
  readonly declineReason = signal('');
  readonly statusLabel = (value: string) => label(REQUEST_STATUS, value);
  readonly urgencyLabel = (value: string) => label(URGENCY, value);
  readonly quoteLabel = (value: string) => label(QUOTE_STATUS, value);
  readonly recipientLabel = (value: string) => label(RECIPIENT_STATUS, value);
  readonly fcfa = fcfa;
  readonly quoteForm = this.formBuilder.nonNullable.group({
    label: ['Prestation', Validators.required],
    quantity: ['1', Validators.required],
    unit_price: ['', Validators.required],
    estimated_delay: [''],
    conditions: [''],
  });

  constructor() {
    this.route.paramMap.pipe(takeUntilDestroyed()).subscribe((params) => {
      const id = params.get('id');
      if (id) {
        this.load(id);
      }
    });
  }

  load(id = this.item()?.id): void {
    if (!id) {
      return;
    }
    this.api.get<ServiceRequest>(`/service_requests/${id}/`).subscribe({
      next: (item) => this.item.set(item),
      error: (err) => this.error.set(errorText(err)),
    });
    this.api.get<Quote[]>(`/service_requests/${id}/quotes/`).subscribe({
      next: (quotes) => this.quotes.set(quotes),
      error: () => this.quotes.set([]),
    });
  }

  cancel(): void {
    const item = this.item();
    if (!item) {
      return;
    }
    this.api.post(`/service_requests/${item.id}/cancel/`).subscribe({
      next: () => this.load(item.id),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  decline(): void {
    const item = this.item();
    if (!item) {
      return;
    }
    this.api.post(`/service_requests/${item.id}/decline/`, { reason: this.declineReason() }).subscribe({
      next: () => {
        this.notice.set('Demande déclinée.');
        this.load(item.id);
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  sendQuote(): void {
    const item = this.item();
    if (!item || this.quoteForm.invalid) {
      return;
    }
    const value = this.quoteForm.getRawValue();
    const quantity = Number(value.quantity);
    const unit = Number(value.unit_price);
    const total = Math.round(quantity * unit);
    this.api
      .post('/quotes/', {
        service_request: item.id,
        total_amount: total,
        estimated_delay: value.estimated_delay,
        conditions: value.conditions,
        lines: [{ label: value.label, quantity: value.quantity, unit_price: value.unit_price }],
      })
      .subscribe({
        next: () => {
          this.notice.set('Devis envoyé.');
          this.load(item.id);
        },
        error: (err) => this.error.set(errorText(err)),
      });
  }

  decide(quoteId: string, action: 'accept' | 'reject'): void {
    this.api.post(action === 'accept' ? `/quotes/${quoteId}/accept/` : `/quotes/${quoteId}/reject/`).subscribe({
      next: (body) => {
        if (action === 'accept' && body && typeof body === 'object' && 'id' in body) {
          this.notice.set('Devis accepté. La mission est ouverte.');
        }
        this.load();
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }
}
