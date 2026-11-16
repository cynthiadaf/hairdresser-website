import { Component } from "@angular/core";
import { STUDIO } from "../core/site-content";

@Component({
  standalone: true,
  template: `<section class="page-heading">
      <p class="eyebrow">Find us</p>
      <h1>Contact</h1>
    </section>
    <section class="contact-grid">
      <div>
        <h2>{{ studio.businessName }}</h2>
        <p>{{ studio.address }}</p>
        <p>
          <a [href]="'tel:' + studio.phone">{{ studio.phone }}</a>
        </p>
        <p>{{ studio.openingHours }}</p>
      </div>
      <figure class="map-image">
        <img
          src="assets/map.png"
          alt="Map showing Jewel Essence Hair Studio at 415 Wick Lane"
        />
        <figcaption>415 Wick Lane, London E3 2JG</figcaption>
      </figure>
    </section>
    <section class="contact-links">
      <a [href]="studio.instagramUrl" target="_blank" rel="noreferrer"
        >Instagram ↗</a
      ><a [href]="studio.bookingUrl" target="_blank" rel="noreferrer"
        >Book an appointment ↗</a
      >
    </section>`,
})
export class ContactComponent {
  readonly studio = STUDIO;
}
