import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { Page, Zone } from '../core/models';

@Component({
  selector: 'app-about',
  imports: [RouterLink],
  templateUrl: './about.html',
})
export class AboutPage {
  private readonly api = inject(ApiService);
  readonly zones = signal<Zone[]>([]);

  constructor() {
    this.api.get<Page<Zone>>('/catalog/zones/', { page_size: 100 }).subscribe({
      next: (page) => this.zones.set(page.results.filter((item) => item.is_active)),
    });
  }

  regions(): string[] {
    return [...new Set(this.zones().map((item) => item.region))];
  }
}
