import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SidebarMenus } from './sidebar-menus';

describe('SidebarMenus', () => {
  let component: SidebarMenus;
  let fixture: ComponentFixture<SidebarMenus>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SidebarMenus],
    }).compileComponents();

    fixture = TestBed.createComponent(SidebarMenus);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
