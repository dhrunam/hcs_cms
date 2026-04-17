import { ComponentFixture, TestBed } from "@angular/core/testing";

import { PublishedCases } from "./published-cases";

describe("PublishedCases", () => {
  let component: PublishedCases;
  let fixture: ComponentFixture<PublishedCases>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PublishedCases],
    }).compileComponents();

    fixture = TestBed.createComponent(PublishedCases);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
