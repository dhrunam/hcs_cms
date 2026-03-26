import { Component } from '@angular/core';
import { ListingOfficerMenus } from './listing-officer-menus/listing-officer-menus';

@Component({
  selector: 'app-sidebar-menus',
  imports: [ListingOfficerMenus],
  templateUrl: './sidebar-menus.html',
  styleUrl: './sidebar-menus.css',
})
export class SidebarMenus {}

