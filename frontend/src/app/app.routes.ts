import { Routes } from "@angular/router";
import { HomeComponent } from "./pages/home.component";
import { PricelistComponent } from "./pages/pricelist.component";
import { GalleryComponent } from "./pages/gallery.component";
import { ContactComponent } from "./pages/contact.component";
import { LoginComponent } from "./pages/login.component";
import { StaffComponent } from "./pages/staff.component";
import { authGuard } from "./core/auth.guard";

export const routes: Routes = [
  { path: "", component: HomeComponent },
  { path: "pricelist", component: PricelistComponent },
  { path: "gallery", component: GalleryComponent },
  { path: "contact", component: ContactComponent },
  { path: "staff/login", component: LoginComponent },
  {
    path: "staff/:section",
    component: StaffComponent,
    canActivate: [authGuard],
  },
  { path: "**", redirectTo: "" },
];
