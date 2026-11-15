import { CommonModule } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { RouterLink } from "@angular/router";
import { ApiService, SiteSettings } from "../core/api.service";

@Component({
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `<ng-container *ngIf="settings as studio; else loading"
      ><section class="hero">
        <img class="hero-logo" src="assets/logo.jpg" alt="" />
        <p class="eyebrow">Hair artistry in East London</p>
        <h1>{{ studio.business_name }}</h1>
        <p class="lead">
          Thoughtful cuts, colour and care for your own kind of beautiful.
        </p>
        <a class="button" routerLink="/pricelist">Explore the pricelist</a>
      </section>
      <section class="intro">
        <div>
          <p class="eyebrow">The studio</p>
          <h2>Quiet confidence,<br />beautifully finished.</h2>
        </div>
        <p>
          Located at {{ studio.address }}. Book your next appointment through
          our trusted booking partner.
        </p>
      </section></ng-container
    ><ng-template #loading
      ><section class="empty-state" aria-live="polite">
        <p *ngIf="!error">Loading studio details...</p>
        <p *ngIf="error">
          Studio details are temporarily unavailable. Please try again shortly.
        </p>
      </section></ng-template
    >`,
})
export class HomeComponent implements OnInit {
  private readonly api = inject(ApiService);
  settings: SiteSettings | null = null;
  error = false;
  ngOnInit(): void {
    this.api
      .settings()
      .subscribe({
        next: (value) => (this.settings = value),
        error: () => (this.error = true),
      });
  }
}
