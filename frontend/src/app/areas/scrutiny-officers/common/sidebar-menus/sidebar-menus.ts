import { Component } from '@angular/core';
import { ScrutinyOfficerMenus } from './scrutiny-officer-menus/scrutiny-officer-menus';

@Component({
  selector: 'app-sidebar-menus',
  imports: [ScrutinyOfficerMenus],
  templateUrl: './sidebar-menus.html',
  styleUrl: './sidebar-menus.css',
})
export class SidebarMenus {}
