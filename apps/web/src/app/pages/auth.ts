import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';

import { AuthService } from '../core/auth.service';
import { errorText } from '../core/labels';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './login.html',
})
export class LoginPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly formBuilder = inject(FormBuilder);
  readonly error = signal('');
  readonly showPassword = signal(false);
  readonly form = this.formBuilder.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
    remember: [true],
  });

  submit(event: Event): void {
    event.preventDefault();
    this.error.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.error.set('Indiquez un e-mail et un mot de passe.');
      return;
    }
    const { email, password, remember } = this.form.getRawValue();
    this.auth.login(email, password, remember).subscribe({
      next: () => {
        const retour = this.route.snapshot.queryParamMap.get('retour') || '/';
        void this.router.navigateByUrl(retour);
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  google(): void {
    this.error.set('La connexion avec Google n’est pas ouverte dans cette version.');
  }
}

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.html',
})
export class RegisterPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly formBuilder = inject(FormBuilder);
  readonly error = signal('');
  readonly showPassword = signal(false);
  readonly trades = [
    'Plomberie',
    'Électricité',
    'Maçonnerie',
    'Peinture',
    'Menuiserie',
    'Carrelage',
    'Serrurerie',
    'Climatisation',
    'Froid',
    'Nettoyage',
    'Jardin',
  ];
  readonly cities = [
    'Dakar',
    'Pikine',
    'Guédiawaye',
    'Rufisque',
    'Keur Massar',
    'Bargny',
    'Diamniadio',
    'Sébikotane',
    'Sangalkam',
  ];
  readonly form = this.formBuilder.nonNullable.group({
    role: ['client' as 'client' | 'professional', Validators.required],
    full_name: ['', Validators.required],
    phone: ['', Validators.required],
    trade: [''],
    city: [''],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    accept_terms: [false, Validators.requiredTrue],
  });

  choose(role: 'client' | 'professional'): void {
    this.form.controls.role.setValue(role);
    if (role === 'client') {
      this.form.controls.trade.setValue('');
    }
  }

  strength(): { score: number; note: string } {
    const value = this.form.controls.password.value;
    if (!value) {
      return { score: 0, note: '' };
    }
    if (value.length < 8) {
      return { score: 1, note: '8 caractères minimum.' };
    }
    if (!/[^A-Za-z0-9]/.test(value)) {
      return { score: 3, note: 'Bon · 8 caractères minimum, ajoutez un symbole pour renforcer' };
    }
    return { score: 4, note: 'Très bon · le mot de passe est solide.' };
  }

  submit(event: Event): void {
    event.preventDefault();
    this.error.set('');
    const value = this.form.getRawValue();
    const digits = value.phone.replace(/\D/g, '');
    if (this.form.invalid || digits.length !== 9) {
      this.form.markAllAsTouched();
      this.error.set('Complétez le nom, un numéro à 9 chiffres, l’e-mail, le mot de passe et les conditions.');
      return;
    }
    const [firstName, ...rest] = value.full_name.trim().split(/\s+/);
    const payload: Record<string, unknown> = {
      role: value.role,
      first_name: firstName ?? '',
      last_name: rest.join(' '),
      email: value.email,
      password: value.password,
      phone: `+221${digits}`,
      business_name: value.role === 'professional' ? value.full_name.trim() : '',
      company_name: '',
      accept_terms: value.accept_terms,
    };
    if (value.role === 'professional' && value.trade) {
      payload['trade'] = value.trade;
    }
    if (value.role === 'professional' && value.city) {
      payload['city'] = value.city;
    }
    this.auth.register(payload).subscribe({
      next: () => void this.router.navigate(['/verification'], { queryParams: { email: value.email } }),
      error: (err) => this.error.set(errorText(err)),
    });
  }

  google(): void {
    this.error.set('La connexion avec Google n’est pas ouverte dans cette version.');
  }
}

@Component({
  selector: 'app-verify',
  imports: [ReactiveFormsModule],
  templateUrl: './verify.html',
})
export class VerifyPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly formBuilder = inject(FormBuilder);
  readonly error = signal('');
  readonly form = this.formBuilder.nonNullable.group({
    email: [this.route.snapshot.queryParamMap.get('email') ?? '', [Validators.required, Validators.email]],
    code: ['', Validators.required],
  });

  submit(): void {
    if (this.form.invalid) {
      return;
    }
    const { email, code } = this.form.getRawValue();
    this.auth.verify(email, code).subscribe({
      next: () => void this.router.navigate(['/']),
      error: (err) => this.error.set(errorText(err)),
    });
  }
}

@Component({
  selector: 'app-reset',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './reset.html',
})
export class ResetPage {
  private readonly auth = inject(AuthService);
  private readonly formBuilder = inject(FormBuilder);
  readonly error = signal('');
  readonly message = signal('');
  readonly sent = signal(false);
  readonly ask = this.formBuilder.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });
  readonly confirm = this.formBuilder.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    code: ['', Validators.required],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  requestCode(): void {
    if (this.ask.invalid) {
      return;
    }
    const email = this.ask.getRawValue().email;
    this.auth.requestReset(email).subscribe({
      next: () => {
        this.sent.set(true);
        this.confirm.patchValue({ email });
        this.message.set('Si ce compte existe, un code a été envoyé. En développement, il apparaît dans la console de l’API.');
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }

  changePassword(): void {
    if (this.confirm.invalid) {
      return;
    }
    const value = this.confirm.getRawValue();
    this.auth.confirmReset(value.email, value.code, value.password).subscribe({
      next: (response) => this.message.set(response.message),
      error: (err) => this.error.set(errorText(err)),
    });
  }
}
