import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

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
  Menuiserie: 'orange',
  Maçonnerie: 'slate',
  Peinture: 'violet',
  Carrelage: 'teal',
  Jardin: 'green',
  Serrurerie: 'red',
  Climatisation: 'sky',
  Froid: 'sky',
  Nettoyage: 'teal',
};

@Component({
  selector: 'app-home',
  imports: [RouterLink],
  templateUrl: './home.html',
})
export class HomePage {
  private readonly api = inject(ApiService);
  readonly trades = signal<Trade[]>([]);
  readonly zoneCount = signal(0);

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
    return TONES[name] ?? 'slate';
  }
}
