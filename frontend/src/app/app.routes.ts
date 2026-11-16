import { Routes } from "@angular/router";
import { HomeComponent } from "./pages/home.component";
import { GalleryComponent } from "./pages/gallery.component";
import { ContactComponent } from "./pages/contact.component";

export const routes: Routes = [
  { path: "", component: HomeComponent },
  { path: "gallery", component: GalleryComponent },
  { path: "contact", component: ContactComponent },
  { path: "**", redirectTo: "" },
];
