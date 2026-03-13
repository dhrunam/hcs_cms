import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Litigant } from './litigant';

describe('Litigant', () => {
  let component: Litigant;
  let fixture: ComponentFixture<Litigant>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Litigant],
    }).compileComponents();

    fixture = TestBed.createComponent(Litigant);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
