import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FactDetails } from './fact-details';

describe('FactDetails', () => {
  let component: FactDetails;
  let fixture: ComponentFixture<FactDetails>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FactDetails],
    }).compileComponents();

    fixture = TestBed.createComponent(FactDetails);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
