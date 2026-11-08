import { HttpErrorResponse } from '@angular/common/http';

import { ApiFailure } from './models';

export const REQUEST_STATUS: Record<string, string> = {
  draft: 'Brouillon',
  open: 'Ouverte',
  quoted: 'Devis reçu',
  booked: 'Réservée',
  cancelled: 'Annulée',
  closed: 'Clôturée',
};

export const URGENCY: Record<string, string> = {
  low: 'Faible',
  normal: 'Normale',
  urgent: 'Urgente',
};

export const QUOTE_STATUS: Record<string, string> = {
  draft: 'Brouillon',
  sent: 'Envoyé',
  accepted: 'Accepté',
  refused: 'Refusé',
  expired: 'Expiré',
};

export const BOOKING_STATUS: Record<string, string> = {
  confirmed: 'Confirmée',
  in_progress: 'En cours',
  completed_by_professional: 'Fin déclarée par le professionnel',
  confirmed_by_client: 'Confirmée par le client',
  cancelled: 'Annulée',
  disputed: 'En litige',
};

export const WEEKDAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'];

export const RECIPIENT_STATUS: Record<string, string> = {
  pending: 'En attente',
  quoted: 'Devis envoyé',
  accepted: 'Retenu',
  refused: 'Refusé',
};

export function label(map: Record<string, string>, value: string): string {
  return map[value] ?? value;
}

export function fcfa(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === '') {
    return '—';
  }
  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return String(value);
  }
  return new Intl.NumberFormat('fr-SN', {
    style: 'currency',
    currency: 'XOF',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function zoneLabel(zone: { city: string; district: string; region: string }): string {
  const place = zone.district ? `${zone.city} — ${zone.district}` : zone.city;
  return `${place} (${zone.region})`;
}

export function errorText(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    const body = error.error as ApiFailure | undefined;
    if (body && typeof body === 'object' && body.message) {
      const details = body.fields
        ? Object.values(body.fields)
            .flat()
            .filter(Boolean)
            .join(' ')
        : '';
      return details ? `${body.message} ${details}` : body.message;
    }
    if (error.status === 0) {
      return 'L’API ne répond pas. Vérifiez que le serveur Django est démarré.';
    }
  }
  return 'Une erreur est survenue.';
}
