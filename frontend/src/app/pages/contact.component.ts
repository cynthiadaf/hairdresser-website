import { CommonModule } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { ApiService, SiteSettings } from "../core/api.service";

@Component({
  standalone: true,
  imports: [CommonModule],
  template: `<section class="page-heading">
      <p class="eyebrow">Find us</p>
      <h1>Contact</h1>
    </section>
    <section *ngIf="settings as studio; else status" class="contact-grid">
      <div>
        <h2>{{ studio.business_name }}</h2>
        <p>{{ studio.address }}</p>
        <p>
          <a [href]="'tel:' + studio.phone">{{ studio.phone }}</a>
        </p>
        <p>{{ studio.opening_hours }}</p>
        <p *ngIf="studio.email">
          <a [href]="'mailto:' + studio.email">{{ studio.email }}</a>
        </p>
      </div>
      <figure class="map-image">
        <img src="assets/map.png" alt="Map showing Jewel Essence Hair Studio at 415 Wick Lane" />
        <figcaption>415 Wick Lane, London E3 2JG</figcaption>
      </figure>
    </section>
    <ng-template #status
      ><section class="empty-state" aria-live="polite">
        {{
          error
            ? "Contact details are temporarily unavailable."
            : "Loading contact details..."
        }}
      </section></ng-template
    >
    <section *ngIf="settings as studio" class="contact-links">
      <a [href]="studio.instagram_url" target="_blank" rel="noreferrer"
        >Instagram ↗</a
      ><a [href]="studio.booking_url" target="_blank" rel="noreferrer"
        >Book an appointment ↗</a
      >
    </section>`,
})
export class ContactComponent implements OnInit {
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
