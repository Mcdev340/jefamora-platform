import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { ApiService } from '../core/api.service';
import { Category, Page, Trade } from '../core/models';

@Component({
  selector: 'app-services',
  imports: [RouterLink],
  templateUrl: './services.html',
})
export class ServicesPage {
  private readonly api = inject(ApiService);
  readonly categories = signal<Category[]>([]);
  readonly trades = signal<Trade[]>([]);

  constructor() {
    this.api.get<Page<Category>>('/catalog/categories/', { page_size: 100 }).subscribe({
      next: (page) => this.categories.set(page.results.filter((item) => item.is_active)),
    });
    this.api.get<Page<Trade>>('/catalog/trades/', { page_size: 100 }).subscribe({
      next: (page) => this.trades.set(page.results.filter((item) => item.is_active)),
    });
  }

  tradesOf(categoryId: string): Trade[] {
    return this.trades().filter((item) => item.category === categoryId);
  }
}
