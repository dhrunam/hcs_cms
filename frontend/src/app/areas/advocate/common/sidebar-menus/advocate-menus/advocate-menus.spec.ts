import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvocateMenus } from './advocate-menus';

describe('AdvocateMenus', () => {
  let component: AdvocateMenus;
  let fixture: ComponentFixture<AdvocateMenus>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdvocateMenus],
    }).compileComponents();

    fixture = TestBed.createComponent(AdvocateMenus);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
