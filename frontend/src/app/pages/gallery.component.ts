import { CommonModule } from "@angular/common";
import { Component, HostListener, OnInit, inject } from "@angular/core";
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
      <button
        *ngFor="let item of items"
        type="button"
        class="gallery-item"
        (click)="openImage(item)"
        [attr.aria-label]="'View gallery image ' + (items.indexOf(item) + 1)"
      >
        <img
          [src]="mediaUrl(item.thumbnail_path || item.media_path)"
          alt=""
          loading="lazy"
        />
      </button>
    </section>
    <div
      *ngIf="selectedItem"
      class="lightbox"
      role="dialog"
      aria-modal="true"
      aria-label="Gallery image preview"
      (click)="closeImage()"
    >
      <div class="lightbox-content" (click)="$event.stopPropagation()">
        <button
          type="button"
          class="lightbox-close"
          aria-label="Close image preview"
          (click)="closeImage()"
        >
          <span aria-hidden="true">&times;</span>
        </button>
        <img
          [src]="mediaUrl(selectedItem.media_path)"
          alt="Enlarged gallery image"
        />
      </div>
    </div>`,
})
export class GalleryComponent implements OnInit {
  private readonly api = inject(ApiService);
  items: GalleryItem[] = [];
  selectedItem: GalleryItem | null = null;
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

  openImage(item: GalleryItem): void {
    this.selectedItem = item;
  }

  closeImage(): void {
    this.selectedItem = null;
  }

  @HostListener("document:keydown.escape")
  handleEscape(): void {
    if (this.selectedItem) {
      this.closeImage();
    }
  }

  mediaUrl(path: string): string {
    return `/api/v1/media/${path}`;
  }
}
