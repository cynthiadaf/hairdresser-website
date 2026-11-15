import { HttpClient } from "@angular/common/http";
import { Injectable, inject } from "@angular/core";
import { Observable } from "rxjs";

export interface SiteSettings {
  business_name: string;
  address: string;
  phone: string;
  email?: string;
  opening_hours: string;
  instagram_url: string;
  booking_url: string;
  map_media_path?: string;
  logo_media_path?: string;
}

export interface PriceItem {
  id: number;
  category_id: number;
  name: string;
  description?: string;
  duration_minutes?: number;
  price_minor: number;
  currency: string;
  sort_order: number;
  is_published: boolean;
}

export interface PriceCategory {
  id: number;
  name: string;
  description?: string;
  sort_order: number;
  is_published: boolean;
  items: PriceItem[];
}

export interface GalleryItem {
  id: number;
  media_type: string;
  media_path: string;
  thumbnail_path?: string;
  width?: number;
  height?: number;
}

export interface SessionUser {
  id: number;
  phone_number: string;
  must_change_password: boolean;
}

@Injectable({ providedIn: "root" })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = "/api/v1";

  settings(): Observable<SiteSettings> {
    return this.http.get<SiteSettings>(`${this.base}/site-settings`);
  }
  pricelist(): Observable<PriceCategory[]> {
    return this.http.get<PriceCategory[]>(`${this.base}/pricelist`);
  }
  gallery(): Observable<{ items: GalleryItem[]; next_cursor: string | null }> {
    return this.http.get<{ items: GalleryItem[]; next_cursor: string | null }>(
      `${this.base}/gallery`,
    );
  }
  login(
    phone_number: string,
    password: string,
  ): Observable<{ authenticated: boolean }> {
    return this.http.post<{ authenticated: boolean }>(
      `${this.base}/auth/login`,
      { phone_number, password },
      { withCredentials: true },
    );
  }
  logout(): Observable<{ authenticated: boolean }> {
    return this.http.post<{ authenticated: boolean }>(
      `${this.base}/auth/logout`,
      {},
      { withCredentials: true },
    );
  }
  me(): Observable<SessionUser> {
    return this.http.get<SessionUser>(`${this.base}/auth/me`, {
      withCredentials: true,
    });
  }
  changePassword(
    current_password: string,
    new_password: string,
  ): Observable<{ changed: boolean }> {
    return this.http.post<{ changed: boolean }>(
      `${this.base}/auth/change-password`,
      { current_password, new_password },
      { withCredentials: true },
    );
  }
  adminCategories(): Observable<PriceCategory[]> {
    return this.http.get<PriceCategory[]>(
      `${this.base}/admin/pricelist/categories`,
      { withCredentials: true },
    );
  }
  createCategory(payload: Partial<PriceCategory>): Observable<PriceCategory> {
    return this.http.post<PriceCategory>(
      `${this.base}/admin/pricelist/categories`,
      payload,
      { withCredentials: true },
    );
  }
  updateCategory(
    id: number,
    payload: Partial<PriceCategory>,
  ): Observable<PriceCategory> {
    return this.http.patch<PriceCategory>(
      `${this.base}/admin/pricelist/categories/${id}`,
      payload,
      { withCredentials: true },
    );
  }
  deleteCategory(id: number): Observable<void> {
    return this.http.delete<void>(
      `${this.base}/admin/pricelist/categories/${id}`,
      { withCredentials: true },
    );
  }
  createItem(payload: Partial<PriceItem>): Observable<PriceItem> {
    return this.http.post<PriceItem>(
      `${this.base}/admin/pricelist/items`,
      payload,
      { withCredentials: true },
    );
  }
  updateSettings(values: Partial<SiteSettings>): Observable<SiteSettings> {
    return this.http.patch<SiteSettings>(
      `${this.base}/admin/site-settings`,
      { values },
      { withCredentials: true },
    );
  }
}
