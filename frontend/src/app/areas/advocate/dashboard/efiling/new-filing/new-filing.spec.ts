import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewFiling } from './new-filing';

describe('NewFiling', () => {
  let component: NewFiling;
  let fixture: ComponentFixture<NewFiling>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewFiling],
    }).compileComponents();

    fixture = TestBed.createComponent(NewFiling);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
