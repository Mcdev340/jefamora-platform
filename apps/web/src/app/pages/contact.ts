import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { AuthService } from '../core/auth.service';
import { errorText } from '../core/labels';

const DRAFT_KEY = 'jefamora.contact';

@Component({
  selector: 'app-contact',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './contact.html',
})
export class ContactPage {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  private readonly formBuilder = inject(FormBuilder);
  readonly auth = inject(AuthService);
  readonly error = signal('');
  readonly sent = signal('');
  readonly topics = ['Mon compte', 'Le badge vérifié', 'Une mission', 'Le catalogue'];
  readonly form = this.formBuilder.nonNullable.group({
    phone: ['', [Validators.required, Validators.minLength(8)]],
    email: ['', [Validators.required, Validators.email]],
    subject: ['', [Validators.required, Validators.maxLength(180)]],
    description: ['', [Validators.required, Validators.minLength(10)]],
  });

  constructor() {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (raw) {
      try {
        this.form.patchValue(JSON.parse(raw));
      } catch {
        sessionStorage.removeItem(DRAFT_KEY);
      }
    }
    this.fillContact();
  }

  private fillContact(): void {
    const profile = this.auth.profile();
    if (!profile) {
      return;
    }
    if (!this.form.controls.email.value) {
      this.form.controls.email.setValue(profile.email);
    }
    if (!this.form.controls.phone.value && profile.phone) {
      this.form.controls.phone.setValue(profile.phone);
    }
  }

  pick(topic: string): void {
    this.form.controls.subject.setValue(topic);
  }

  submit(event: Event): void {
    event.preventDefault();
    this.error.set('');
    this.sent.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.error.set('Indiquez votre numéro, votre e-mail, un sujet et un message d’au moins 10 caractères.');
      return;
    }
    if (!this.auth.isLoggedIn()) {
      sessionStorage.setItem(DRAFT_KEY, JSON.stringify(this.form.getRawValue()));
      void this.router.navigate(['/connexion'], { queryParams: { retour: '/contact' } });
      return;
    }
    if (!this.auth.profile()?.is_verified) {
      this.error.set('Confirmez votre e-mail avant d’envoyer un message.');
      return;
    }
    const value = this.form.getRawValue();
    this.api.post('/support/tickets/', {
      subject: value.subject,
      description: `${value.description.trim()}\n\nNuméro : ${value.phone.trim()}\nE-mail : ${value.email.trim()}`,
      priority: 'normal',
    }).subscribe({
      next: () => {
        sessionStorage.removeItem(DRAFT_KEY);
        this.form.reset({ phone: '', email: '', subject: '', description: '' });
        this.fillContact();
        this.sent.set('Message envoyé. Vous le retrouvez dans Compte, rubrique Support.');
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }
}
