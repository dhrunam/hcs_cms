import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ScrutinyDetails } from './scrutiny-details';

describe('ScrutinyDetails', () => {
  let component: ScrutinyDetails;
  let fixture: ComponentFixture<ScrutinyDetails>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ScrutinyDetails],
    }).compileComponents();

    fixture = TestBed.createComponent(ScrutinyDetails);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
