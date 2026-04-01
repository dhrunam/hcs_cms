import { Component } from "@angular/core";
import { ReaderMenus } from "./reader-menus/reader-menus";

@Component({
  selector: "app-sidebar-menus",
  imports: [ReaderMenus],
  templateUrl: "./sidebar-menus.html",
  styleUrl: "./sidebar-menus.css",
})
export class SidebarMenus {}
