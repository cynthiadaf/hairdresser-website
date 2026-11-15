import { Injectable, inject } from "@angular/core";
import { Router } from "@angular/router";
import { Observable, catchError, map, of, tap } from "rxjs";
import { ApiService, SessionUser } from "./api.service";

@Injectable({ providedIn: "root" })
export class AuthService {
  private readonly api = inject(ApiService);
  private readonly router = inject(Router);
  private user: SessionUser | null = null;

  login(phone: string, password: string): Observable<boolean> {
    return this.api.login(phone, password).pipe(
      tap(() => (this.user = null)),
      map(() => true),
    );
  }

  currentUser(): Observable<SessionUser | null> {
    if (this.user) return of(this.user);
    return this.api.me().pipe(
      tap((user) => (this.user = user)),
      catchError(() => of(null)),
    );
  }

  logout(): void {
    this.api.logout().subscribe({
      complete: () => {
        this.user = null;
        void this.router.navigate(["/staff/login"]);
      },
    });
  }
}
