import { Component } from "@angular/core";
import { STUDIO } from "../core/site-content";

@Component({
  standalone: true,
  template: `<section class="hero">
      <p class="eyebrow">Hair artistry in East London</p>
      <h1>{{ studio.businessName }}</h1>
      <div class="hero-details">
        <div class="hero-copy">
          <p class="lead">
            Thoughtful cuts, colour and care for your own kind of beautiful.
          </p>
          <a
            class="button"
            [href]="studio.bookingUrl"
            target="_blank"
            rel="noreferrer"
            >View Services</a
          >
        </div>
        <img class="hero-logo" src="/assets/logo.png" alt="" />
      </div>
    </section>
    <section class="intro">
      <div>
        <p class="eyebrow">The studio</p>
        <h2>Quiet confidence,<br />beautifully finished.</h2>
      </div>
      <div>
        <p>
          Located at {{ studio.address }}. Book your next appointment through
          our trusted booking partner.
        </p>
        <a
          class="button"
          href="{{ studio.bookingUrl }}"
          target="_blank"
          rel="noreferrer"
          >Book Now</a
        >
      </div>
    </section>`,
})
export class HomeComponent {
  readonly studio = STUDIO;
}
