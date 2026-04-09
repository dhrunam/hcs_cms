import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ReaderService } from '../../../../services/reader/reader.service';
import { ReaderDailyProceedingsPage } from './daily-proceedings';

describe('ReaderDailyProceedingsPage', () => {
  let component: ReaderDailyProceedingsPage;
  let fixture: ComponentFixture<ReaderDailyProceedingsPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReaderDailyProceedingsPage],
      providers: [
        {
          provide: ReaderService,
          useValue: {
            getDailyProceedings: () => of({ total: 0, items: [] }),
            submitDailyProceeding: () => of({}),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ReaderDailyProceedingsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('creates', () => {
    expect(component).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from "@angular/core/testing";
import { of } from "rxjs";

import { ReaderService } from "../../../../services/reader/reader.service";
import { ReaderDailyProceedingsPage } from "./daily-proceedings";

describe("ReaderDailyProceedingsPage", () => {
  let component: ReaderDailyProceedingsPage;
  let fixture: ComponentFixture<ReaderDailyProceedingsPage>;

  const readerServiceMock = {
    getBenchConfigurations: jasmine.createSpy("getBenchConfigurations").and.returnValue(
      of({ items: [] }),
    ),
    getDailyProceedingsCases: jasmine.createSpy("getDailyProceedingsCases").and.returnValue(
      of({ total: 1, items: [{ efiling_id: 1, case_number: "C-1", petitioner_name: "P", bench: "CJ", can_assign_listing_date: true, listing_officer_synced: false }] }),
    ),
    submitDailyProceeding: jasmine.createSpy("submitDailyProceeding").and.returnValue(
      of({ id: 1, listing_officer_synced: true, steno_status: "PENDING" }),
    ),
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReaderDailyProceedingsPage],
      providers: [{ provide: ReaderService, useValue: readerServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(ReaderDailyProceedingsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should load daily proceedings cases", () => {
    expect(component.items.length).toBe(1);
    expect(component.items[0].efiling_id).toBe(1);
  });
});
