import { Component } from '@angular/core';
import { StenoMenus } from './steno-menus/steno-menus';

@Component({
  selector: 'app-steno-sidebar-menus',
  imports: [StenoMenus],
  templateUrl: './sidebar-menus.html',
  styleUrl: './sidebar-menus.css',
})
export class StenoSidebarMenus {}
