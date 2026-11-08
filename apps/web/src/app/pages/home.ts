import { Component, inject, input, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { errorText } from '../core/labels';
import { Page, Trade } from '../core/models';

const CHIP_LABELS: Record<string, string> = {
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
  Maçonnerie: 'slate',
  Peinture: 'violet',
  Menuiserie: 'orange',
  Carrelage: 'teal',
  Jardin: 'green',
  Serrurerie: 'red',
  Climatisation: 'sky',
  Froid: 'sky',
  Nettoyage: 'teal',
};

@Component({
  selector: 'app-trade-mark',
  template: `
    <svg viewBox="0 0 24 24" aria-hidden="true">
      @switch (name()) {
        @case ('Électricité') { <path d="M13 2 4 14h7l-1 8 10-14h-7l0-6z" /> }
        @case ('Plomberie') { <path d="M12 2.5c2.2 3 5 6 5 9.2a5 5 0 0 1-10 0c0-3.2 2.8-6.2 5-9.2z" /> }
        @case ('Maçonnerie') { <path d="M3 7h18M3 12h18M3 17h18M9 7v10M15 7v10" /> }
        @case ('Peinture') { <path d="M4 15h10a3 3 0 0 1 0 6H8M4 15V5h12v6" /> }
        @case ('Menuiserie') { <path d="M15 4l5 5-2 2-5-5zm-2 2L4 15l2 2 9-9" /> }
        @case ('Carrelage') { <path d="M4 4h7v7H4V4zm9 0h7v7h-7V4zM4 13h7v7H4v-7zm9 0h7v7h-7v-7z" /> }
        @case ('Jardin') { <path d="M12 22V12m0 0c-3 0-6-2-6-6 3 0 6 2 6 6zm0 0c3 0 6-2 6-6-3 0-6 2-6 6z" /> }
        @case ('Serrurerie') { <path d="M8 10V7a4 4 0 1 1 8 0v3h1a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h1zm2 0h4V7a2 2 0 1 0-4 0v3z" /> }
        @case ('Climatisation') { <path d="M12 3v18M5 7l14 10M19 7 5 17M8 4l4 4 4-4M8 20l4-4 4 4" /> }
        @case ('Froid') { <path d="M12 2v20M4.9 6.5l14.2 11M19.1 6.5 4.9 17.5M8 4l4 3 4-3M8 20l4-3 4 3" /> }
        @default { <path d="M5 13h4l2-6 2 10 2-6h4" /> }
      }
    </svg>
  `,
  styles: `
    :host { display: grid; }
    svg { width: 1.35rem; height: 1.35rem; fill: none; stroke: white; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  `,
})
export class TradeMark {
  readonly name = input.required<string>();
}

@Component({
  selector: 'app-home',
  imports: [RouterLink, TradeMark],
  templateUrl: './home.html',
})
export class HomePage {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  readonly trades = signal<Trade[]>([]);
  readonly zoneCount = signal(0);
  readonly error = signal('');
  readonly query = signal('');

  constructor() {
    this.api.get<Page<Trade>>('/catalog/trades/', { page_size: 100 }).subscribe({
      next: (page) => this.trades.set(page.results.filter((item) => item.is_active)),
      error: (err) => this.error.set(errorText(err)),
    });
    this.api.get<Page<unknown>>('/catalog/zones/', { page_size: 1 }).subscribe({
      next: (page) => this.zoneCount.set(page.count),
    });
  }

  tone(name: string): string {
    return TONES[name] ?? 'slate';
  }

  popular(): Trade[] {
    return ['Électricité', 'Plomberie', 'Menuiserie', 'Maçonnerie']
      .map((name) => this.trades().find((item) => item.name === name))
      .filter((item): item is Trade => item !== undefined);
  }

  chip(name: string): string {
    return CHIP_LABELS[name] ?? name;
  }

  onSearch(event: Event): void {
    event.preventDefault();
    const input = (event.target as HTMLFormElement).querySelector('input');
    this.query.set(input?.value ?? '');
    this.search();
  }

  search(trade?: Trade): void {
    const chosen = trade ?? this.matchQuery();
    void this.router.navigate(['/professionnels'], {
      queryParams: chosen ? { trade: chosen.id } : {},
    });
  }

  private matchQuery(): Trade | undefined {
    const text = this.query().trim().toLowerCase();
    if (!text) {
      return undefined;
    }
    return this.trades().find((item) => {
      const label = this.chip(item.name).toLowerCase();
      return item.name.toLowerCase().includes(text) || label.includes(text);
    });
  }
}
