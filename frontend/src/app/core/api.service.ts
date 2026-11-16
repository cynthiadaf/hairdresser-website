import { HttpClient } from "@angular/common/http";
import { Injectable, inject } from "@angular/core";
import { Observable } from "rxjs";

export interface GalleryItem {
  id: number;
  media_type: string;
  media_path: string;
  thumbnail_path?: string;
  width?: number;
  height?: number;
}

@Injectable({ providedIn: "root" })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = "/api/v1";

  gallery(): Observable<{ items: GalleryItem[]; next_cursor: string | null }> {
    return this.http.get<{ items: GalleryItem[]; next_cursor: string | null }>(
      `${this.base}/gallery`,
    );
  }
}
