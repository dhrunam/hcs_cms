import { ComponentFixture, TestBed } from "@angular/core/testing";

import { CaseDetailsV2 } from "./case-details-v2";

describe("CaseDetailsV2", () => {
  let component: CaseDetailsV2;
  let fixture: ComponentFixture<CaseDetailsV2>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CaseDetailsV2],
    }).compileComponents();

    fixture = TestBed.createComponent(CaseDetailsV2);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
