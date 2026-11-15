import { CommonModule } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { ActivatedRoute, RouterLink } from "@angular/router";
import { ApiService, PriceCategory, SiteSettings } from "../core/api.service";
import { AuthService } from "../core/auth.service";

@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `<section class="page-heading">
      <p class="eyebrow">Studio administration</p>
      <h1>{{ sectionTitle }}</h1>
      <p>
        <a routerLink="/staff/pricelist">Pricelist</a> ·
        <a routerLink="/staff/settings">Settings</a> ·
        <a routerLink="/staff/password">Password</a> ·
        <button class="link-button" (click)="logout()">Sign out</button>
      </p>
    </section>
    <section class="editor-panel" aria-live="polite">
      <p *ngIf="message">{{ message }}</p>
      <ng-container *ngIf="section === 'pricelist'"
        ><h2>Pricelist editor</h2>
        <div *ngFor="let category of categories" class="admin-row">
          <strong>{{ category.name }}</strong
          ><button type="button" (click)="removeCategory(category.id)">
            Delete
          </button>
        </div>
        <form (ngSubmit)="addCategory()">
          <label
            >New category<input
              name="categoryName"
              [(ngModel)]="categoryName"
              required /></label
          ><button class="button" type="submit">Add category</button>
        </form></ng-container
      ><ng-container *ngIf="section === 'settings'"
        ><h2>Business settings</h2>
        <form (ngSubmit)="saveSettings()">
          <label
            >Business name<input
              name="business_name"
              [(ngModel)]="settings.business_name" /></label
          ><label
            >Address<input
              name="address"
              [(ngModel)]="settings.address" /></label
          ><label
            >Phone<input name="phone" [(ngModel)]="settings.phone" /></label
          ><label
            >Opening hours<input
              name="opening_hours"
              [(ngModel)]="settings.opening_hours" /></label
          ><button class="button" type="submit">Save settings</button>
        </form></ng-container
      ><ng-container *ngIf="section === 'password'"
        ><h2>Change password</h2>
        <form (ngSubmit)="changePassword()">
          <label
            >Current password<input
              name="current"
              type="password"
              [(ngModel)]="currentPassword"
              required /></label
          ><label
            >New password<input
              name="new"
              type="password"
              [(ngModel)]="newPassword"
              minlength="12"
              required /></label
          ><button class="button" type="submit">Change password</button>
        </form></ng-container
      >
    </section>`,
})
export class StaffComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(ApiService);
  private readonly auth = inject(AuthService);
  section = "";
  categories: PriceCategory[] = [];
  categoryName = "";
  settings: SiteSettings = {
    business_name: "",
    address: "",
    phone: "",
    opening_hours: "",
    instagram_url: "",
    booking_url: "",
  };
  currentPassword = "";
  newPassword = "";
  message = "";
  get sectionTitle(): string {
    return this.section === "password"
      ? "Password"
      : this.section.charAt(0).toUpperCase() + this.section.slice(1);
  }
  ngOnInit(): void {
    this.section = this.route.snapshot.paramMap.get("section") ?? "pricelist";
    if (this.section === "pricelist") this.loadCategories();
    if (this.section === "settings")
      this.api.settings().subscribe((value) => (this.settings = value));
  }
  loadCategories(): void {
    this.api
      .adminCategories()
      .subscribe({
        next: (value) => (this.categories = value),
        error: () => (this.message = "Unable to load the pricelist."),
      });
  }
  addCategory(): void {
    this.api
      .createCategory({
        name: this.categoryName,
        sort_order: this.categories.length,
        is_published: true,
      })
      .subscribe({
        next: () => {
          this.categoryName = "";
          this.loadCategories();
        },
        error: () => (this.message = "Unable to add category."),
      });
  }
  removeCategory(id: number): void {
    this.api
      .deleteCategory(id)
      .subscribe({
        next: () => this.loadCategories(),
        error: () => (this.message = "Unable to delete category."),
      });
  }
  saveSettings(): void {
    this.api.updateSettings(this.settings).subscribe({
      next: (value) => {
        this.settings = value;
        this.message = "Settings saved.";
      },
      error: () => (this.message = "Unable to save settings."),
    });
  }
  changePassword(): void {
    this.api.changePassword(this.currentPassword, this.newPassword).subscribe({
      next: () => {
        this.message = "Password changed. Please sign in again next time.";
        this.currentPassword = "";
        this.newPassword = "";
      },
      error: () => (this.message = "Unable to change password."),
    });
  }
  logout(): void {
    this.auth.logout();
  }
}
