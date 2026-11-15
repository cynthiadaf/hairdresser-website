import { Component } from "@angular/core";
import { RouterLink, RouterLinkActive, RouterOutlet } from "@angular/router";

@Component({
  selector: "je-root",
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: ` <a class="skip-link" href="#main">Skip to content</a>
    <header>
      <a class="wordmark" routerLink="/" aria-label="Jewel Essence Hair Studio home">
        <img src="assets/logo.jpg" alt="Jewel Essence Hair Studio" />
      </a>
      <nav aria-label="Main navigation">
        <a
          routerLink="/"
          routerLinkActive="active"
          [routerLinkActiveOptions]="{ exact: true }"
          >Home</a
        ><a routerLink="/pricelist" routerLinkActive="active">Pricelist</a
        ><a routerLink="/gallery" routerLinkActive="active">Gallery</a
        ><a routerLink="/contact" routerLinkActive="active">Contact</a>
      </nav>
    </header>
    <main id="main"><router-outlet /></main>
    <footer>
      <span>© Xertz Industries {{ year }}</span
      ><a routerLink="/staff/login">Staff</a>
    </footer>`,
})
export class AppComponent {
  year = new Date().getFullYear();
}
