import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApprovedCases } from './approved-cases';

describe('ApprovedCases', () => {
  let component: ApprovedCases;
  let fixture: ComponentFixture<ApprovedCases>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApprovedCases],
    }).compileComponents();

    fixture = TestBed.createComponent(ApprovedCases);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
