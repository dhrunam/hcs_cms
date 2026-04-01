import { ComponentFixture, TestBed } from "@angular/core/testing";

import { ReaderMenus } from "./reader-menus";

describe("ReaderMenus", () => {
  let component: ReaderMenus;
  let fixture: ComponentFixture<ReaderMenus>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReaderMenus],
    }).compileComponents();

    fixture = TestBed.createComponent(ReaderMenus);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
