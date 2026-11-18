import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { Page, Trade, Zone } from '../core/models';

const REFERENCE: Array<Pick<Zone, 'region' | 'city' | 'district'>> = [
  ['Dakar', 'Dakar', 'Plateau'],
  ['Dakar', 'Dakar', 'Médina'],
  ['Dakar', 'Dakar', 'Almadies'],
  ['Dakar', 'Dakar', 'Ouakam'],
  ['Dakar', 'Pikine', 'Pikine'],
  ['Dakar', 'Guédiawaye', 'Guédiawaye'],
  ['Dakar', 'Rufisque', 'Rufisque'],
  ['Dakar', 'Keur Massar', 'Keur Massar'],
  ['Dakar', 'Bargny', 'Bargny'],
  ['Dakar', 'Diamniadio', 'Diamniadio'],
  ['Dakar', 'Sébikotane', 'Sébikotane'],
  ['Dakar', 'Sangalkam', 'Sangalkam'],
  ['Thiès', 'Thiès', 'Thiès Nord'],
  ['Saint-Louis', 'Saint-Louis', 'Centre'],
].map(([region, city, district]) => ({ region, city, district }));

@Component({
  selector: 'app-about',
  imports: [RouterLink],
  templateUrl: './about.html',
})
export class AboutPage {
  private readonly api = inject(ApiService);
  readonly zones = signal<Zone[]>([]);
  readonly tradeCount = signal(0);

  constructor() {
    this.api.get<Page<Zone>>('/catalog/zones/', { page_size: 100 }).subscribe({
      next: (page) => this.zones.set(page.results.filter((item) => item.is_active)),
    });
    this.api.get<Page<Trade>>('/catalog/trades/', { page_size: 100 }).subscribe({
      next: (page) => this.tradeCount.set(page.results.filter((item) => item.is_active).length),
    });
  }

  groups(): { region: string; places: string[] }[] {
    const source = this.zones().length ? this.zones() : REFERENCE;
    return [...new Set(source.map((item) => item.region))].map((region) => ({
      region,
      places: source.filter((item) => item.region === region).map((item) => this.place(item)),
    }));
  }

  private place(zone: Pick<Zone, 'city' | 'district'>): string {
    return zone.district && zone.district !== zone.city ? `${zone.city} · ${zone.district}` : zone.city;
  }
}
