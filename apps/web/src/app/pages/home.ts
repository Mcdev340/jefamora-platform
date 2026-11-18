import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { Page, Trade } from '../core/models';

const LABELS: Record<string, string> = {
  Électricité: 'Électricien',
  Plomberie: 'Plombier',
  Menuiserie: 'Menuisier',
  Maçonnerie: 'Maçon',
  Peinture: 'Peintre',
  Carrelage: 'Carreleur',
  Jardin: 'Jardinier',
  Serrurerie: 'Serrurier',
  Climatisation: 'Climatisation',
  Froid: 'Froid',
  Nettoyage: 'Nettoyage',
};

const TONES: Record<string, string> = {
  Électricité: 'amber',
  Plomberie: 'blue',
  Menuiserie: '',
  Maçonnerie: 'rose',
  Peinture: 'violet',
  Carrelage: 'blue',
  Jardin: 'green',
  Serrurerie: 'rose',
  Climatisation: 'blue',
  Froid: 'blue',
  Nettoyage: 'green',
};

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.html',
})
export class HomePage {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  readonly trades = signal<Trade[]>([]);
  readonly zoneCount = signal(0);
  readonly query = signal('');
  readonly popular = ['Électricité', 'Plomberie', 'Menuiserie', 'Maçonnerie'];

  constructor() {
    this.api.get<Page<Trade>>('/catalog/trades/', { page_size: 100 }).subscribe({
      next: (page) => this.trades.set(page.results.filter((item) => item.is_active)),
    });
    this.api.get<Page<unknown>>('/catalog/zones/', { page_size: 1 }).subscribe({
      next: (page) => this.zoneCount.set(page.count),
    });
  }

  label(name: string): string {
    return LABELS[name] ?? name;
  }

  tone(name: string): string {
    return TONES[name] ?? '';
  }

  search(event: Event): void {
    event.preventDefault();
    this.open(this.query());
  }

  open(text: string): void {
    const wanted = text.trim().toLocaleLowerCase('fr');
    const trade = this.trades().find(
      (item) =>
        item.name.toLocaleLowerCase('fr') === wanted || this.label(item.name).toLocaleLowerCase('fr') === wanted,
    );
    void this.router.navigate(['/professionnels'], trade ? { queryParams: { trade: trade.id } } : {});
  }
}
