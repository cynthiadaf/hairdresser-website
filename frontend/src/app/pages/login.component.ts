import { Component, inject } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { Router } from "@angular/router";
import { AuthService } from "../core/auth.service";

@Component({
  standalone: true,
  imports: [FormsModule],
  template: `<section class="auth">
    <p class="eyebrow">Private studio access</p>
    <h1>Staff login</h1>
    <form (ngSubmit)="submit()">
      <label
        >Phone number<input
          name="phone"
          type="tel"
          autocomplete="username"
          [(ngModel)]="phone"
          required /></label
      ><label
        >Password<input
          name="password"
          type="password"
          autocomplete="current-password"
          [(ngModel)]="password"
          required /></label
      ><button class="button" type="submit" [disabled]="busy">
        {{ busy ? "Signing in..." : "Sign in" }}
      </button>
      <p class="form-note" aria-live="polite">{{ message }}</p>
    </form>
  </section>`,
})
export class LoginComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  phone = "";
  password = "";
  message = "";
  busy = false;
  submit(): void {
    this.busy = true;
    this.message = "";
    this.auth.login(this.phone, this.password).subscribe({
      next: () => {
        this.busy = false;
        void this.router.navigate(["/staff/pricelist"]);
      },
      error: () => {
        this.busy = false;
        this.message = "Sign-in failed. Check your details and try again.";
      },
    });
  }
}
