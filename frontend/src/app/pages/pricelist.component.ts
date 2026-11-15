import { CommonModule } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { ApiService, PriceCategory } from "../core/api.service";

@Component({
  standalone: true,
  imports: [CommonModule],
  template: `<section class="page-heading">
      <p class="eyebrow">Services & care</p>
      <h1>Pricelist</h1>
      <p>Current services and prices published by the studio.</p>
    </section>
    <section
      *ngIf="loading || error || !categories.length"
      class="empty-state"
      aria-live="polite"
    >
      <p *ngIf="loading">Loading the pricelist...</p>
      <p *ngIf="error">The pricelist is temporarily unavailable.</p>
      <ng-container *ngIf="!loading && !error && !categories.length"
        ><h2>Pricelist coming soon</h2>
        <p>
          New services will appear here as they are published.
        </p></ng-container
      >
    </section>
    <section *ngIf="!loading && !error && categories.length" class="price-list">
      <article *ngFor="let category of categories">
        <h2>{{ category.name }}</h2>
        <p *ngIf="category.description" class="muted">
          {{ category.description }}
        </p>
        <div *ngFor="let item of category.items" class="price-row">
          <div>
            <strong>{{ item.name }}</strong
            ><span *ngIf="item.duration_minutes" class="muted"
              >{{ item.duration_minutes }} min</span
            ><small *ngIf="item.description">{{ item.description }}</small>
          </div>
          <strong>{{
            item.price_minor / 100
              | currency: item.currency : "symbol" : "1.2-2"
          }}</strong>
        </div>
      </article>
    </section>`,
})
export class PricelistComponent implements OnInit {
  private readonly api = inject(ApiService);
  categories: PriceCategory[] = [];
  loading = true;
  error = false;
  ngOnInit(): void {
    this.api.pricelist().subscribe({
      next: (value) => {
        this.categories = value;
        this.loading = false;
      },
      error: () => {
        this.error = true;
        this.loading = false;
      },
    });
  }
}
