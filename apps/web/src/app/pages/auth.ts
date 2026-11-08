import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink, RouterLinkActive } from '@angular/router';

import { AuthService } from '../core/auth.service';
import { errorText } from '../core/labels';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, RouterLink, RouterLinkActive],
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
  });

  submit(event: Event): void {
    event.preventDefault();
    this.error.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.error.set('Indiquez un e-mail et un mot de passe.');
      return;
    }
    const { email, password } = this.form.getRawValue();
    this.auth.login(email, password).subscribe({
      next: () => {
        const retour = this.route.snapshot.queryParamMap.get('retour') || '/';
        void this.router.navigateByUrl(retour);
      },
      error: (err) => this.error.set(errorText(err)),
    });
  }
}

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, RouterLink, RouterLinkActive],
  templateUrl: './register.html',
})
export class RegisterPage {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  private readonly formBuilder = inject(FormBuilder);
  readonly error = signal('');
  readonly showPassword = signal(false);
  readonly form = this.formBuilder.nonNullable.group({
    role: ['client' as 'client' | 'professional', Validators.required],
    full_name: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    accept_terms: [false, Validators.requiredTrue],
  });

  submit(event: Event): void {
    event.preventDefault();
    this.error.set('');
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      this.error.set('Complétez le nom, l’e-mail, le mot de passe et les conditions.');
      return;
    }
    const value = this.form.getRawValue();
    const [firstName, ...rest] = value.full_name.trim().split(/\s+/);
    this.auth.register({
      role: value.role,
      first_name: firstName ?? '',
      last_name: rest.join(' '),
      email: value.email,
      password: value.password,
      phone: '',
      business_name: '',
      company_name: '',
      accept_terms: value.accept_terms,
    }).subscribe({
      next: () => void this.router.navigate(['/verification'], { queryParams: { email: value.email } }),
      error: (err) => this.error.set(errorText(err)),
    });
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
