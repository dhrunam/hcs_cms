import { ComponentFixture, TestBed } from "@angular/core/testing";

import { NewFilingV2 } from "./new-filing-v2";

describe("NewFilingV2", () => {
  let component: NewFilingV2;
  let fixture: ComponentFixture<NewFilingV2>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewFilingV2],
    }).compileComponents();

    fixture = TestBed.createComponent(NewFilingV2);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
