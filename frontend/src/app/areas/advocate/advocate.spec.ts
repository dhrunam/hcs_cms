import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Advocate } from './advocate';

describe('Advocate', () => {
  let component: Advocate;
  let fixture: ComponentFixture<Advocate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Advocate],
    }).compileComponents();

    fixture = TestBed.createComponent(Advocate);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
