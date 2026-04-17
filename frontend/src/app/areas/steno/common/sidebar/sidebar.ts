import { Component } from '@angular/core';
import { StenoSidebarMenus } from '../sidebar-menus/sidebar-menus';

@Component({
  selector: 'app-steno-sidebar',
  imports: [StenoSidebarMenus],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css',
})
export class StenoSidebar {}
