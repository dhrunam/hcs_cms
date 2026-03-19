import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CasesScrutiny } from './cases-scrutiny';

describe('CasesScrutiny', () => {
  let component: CasesScrutiny;
  let fixture: ComponentFixture<CasesScrutiny>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CasesScrutiny],
    }).compileComponents();

    fixture = TestBed.createComponent(CasesScrutiny);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
