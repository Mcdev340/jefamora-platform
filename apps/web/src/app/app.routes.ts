import { Routes } from '@angular/router';

import { authGuard, clientGuard, guestGuard, professionalGuard } from './core/guards';
import { AccountPage } from './pages/account';
import { LoginPage, RegisterPage, ResetPage, VerifyPage } from './pages/auth';
import { BookingDetailPage, BookingsPage } from './pages/bookings';
import { DashboardPage } from './pages/dashboard';
import { HomePage } from './pages/home';
import { ProSpacePage } from './pages/pro-space';
import { ProfessionalDetailPage, ProfessionalsPage } from './pages/professionals';
import { RequestDetailPage, RequestFormPage, RequestsPage } from './pages/requests';

export const routes: Routes = [
  { path: '', component: HomePage },
  { path: 'connexion', component: LoginPage, canActivate: [guestGuard] },
  { path: 'inscription', component: RegisterPage, canActivate: [guestGuard] },
  { path: 'verification', component: VerifyPage },
  { path: 'mot-de-passe', component: ResetPage },
  { path: 'tableau', component: DashboardPage, canActivate: [authGuard] },
  { path: 'professionnels', component: ProfessionalsPage },
  { path: 'professionnels/:id', component: ProfessionalDetailPage, canActivate: [authGuard] },
  { path: 'demandes', component: RequestsPage, canActivate: [authGuard] },
  { path: 'demandes/nouvelle', component: RequestFormPage, canActivate: [authGuard, clientGuard] },
  { path: 'demandes/:id', component: RequestDetailPage, canActivate: [authGuard] },
  { path: 'missions', component: BookingsPage, canActivate: [authGuard] },
  { path: 'missions/:id', component: BookingDetailPage, canActivate: [authGuard] },
  { path: 'espace-pro/:section', component: ProSpacePage, canActivate: [authGuard, professionalGuard] },
  { path: 'compte/:section', component: AccountPage, canActivate: [authGuard] },
  { path: '**', redirectTo: '' },
];
