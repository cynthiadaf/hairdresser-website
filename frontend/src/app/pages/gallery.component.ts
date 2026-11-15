import { CommonModule } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { ApiService, GalleryItem } from "../core/api.service";

@Component({
  standalone: true,
  imports: [CommonModule],
  template: `<section class="page-heading">
      <p class="eyebrow">Studio journal</p>
      <h1>Gallery</h1>
      <p>
        A visual record of approved work, kept locally for a fast and reliable
        experience.
      </p>
    </section>
    <section
      *ngIf="loading || error || !items.length"
      class="empty-state"
      aria-live="polite"
    >
      <p *ngIf="loading">Loading the gallery...</p>
      <p *ngIf="error">The gallery is temporarily unavailable.</p>
      <ng-container *ngIf="!loading && !error && !items.length"
        ><h2>Gallery awaiting approved media</h2>
        <p>No gallery assets are available yet.</p></ng-container
      >
    </section>
    <section *ngIf="!loading && !error && items.length" class="gallery-grid">
      <figure *ngFor="let item of items">
        <img
          [src]="mediaUrl(item.thumbnail_path || item.media_path)"
          [alt]="''"
          loading="lazy"
        />
      </figure>
    </section>`,
})
export class GalleryComponent implements OnInit {
  private readonly api = inject(ApiService);
  items: GalleryItem[] = [];
  loading = true;
  error = false;
  ngOnInit(): void {
    this.api.gallery().subscribe({
      next: (value) => {
        this.items = value.items;
        this.loading = false;
      },
      error: () => {
        this.error = true;
        this.loading = false;
      },
    });
  }
  mediaUrl(path: string): string {
    return `/api/v1/media/${path}`;
  }
}
