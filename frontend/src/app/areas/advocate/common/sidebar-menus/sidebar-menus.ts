import { Component } from '@angular/core';
import { AdvocateMenus } from './advocate-menus/advocate-menus';

@Component({
  selector: 'app-sidebar-menus',
  imports: [AdvocateMenus],
  templateUrl: './sidebar-menus.html',
  styleUrl: './sidebar-menus.css',
})
export class SidebarMenus {}
