import { Component } from "@angular/core";
import { RouterLink, RouterLinkActive, RouterOutlet } from "@angular/router";
import { STUDIO } from "./core/site-content";

@Component({
  selector: "je-root",
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: ` <a class="skip-link" href="#main">Skip to content</a>
    <header>
      <a
        class="wordmark"
        routerLink="/"
        aria-label="Jewel Essence Hair Studio home"
      >
        Jewel Essence Hair Studio
      </a>
      <nav aria-label="Main navigation">
        <a
          routerLink="/"
          routerLinkActive="active"
          [routerLinkActiveOptions]="{ exact: true }"
          >Home</a
        ><a [href]="bookingUrl" target="_blank" rel="noreferrer">Services</a
        ><a routerLink="/gallery" routerLinkActive="active">Gallery</a
        ><a routerLink="/contact" routerLinkActive="active">Contact</a>
      </nav>
    </header>
    <main id="main"><router-outlet /></main>
    <footer>
      <span>© Xertz Industries {{ year }}</span>
    </footer>`,
})
export class AppComponent {
  year = new Date().getFullYear();
  readonly bookingUrl = STUDIO.bookingUrl;
}
