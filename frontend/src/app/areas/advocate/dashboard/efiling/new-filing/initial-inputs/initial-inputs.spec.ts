import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InitialInputs } from './initial-inputs';

describe('InitialInputs', () => {
  let component: InitialInputs;
  let fixture: ComponentFixture<InitialInputs>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InitialInputs],
    }).compileComponents();

    fixture = TestBed.createComponent(InitialInputs);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
