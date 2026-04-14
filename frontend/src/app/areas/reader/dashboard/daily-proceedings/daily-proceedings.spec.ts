import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ReaderService } from '../../../../services/reader/reader.service';
import { ReaderDailyProceedingsPage } from './daily-proceedings';

describe('ReaderDailyProceedingsPage', () => {
  let component: ReaderDailyProceedingsPage;
  let fixture: ComponentFixture<ReaderDailyProceedingsPage>;
  let readerServiceMock: {
    getDailyProceedings: jasmine.Spy;
    submitDailyProceeding: jasmine.Spy;
  };

  beforeEach(async () => {
    readerServiceMock = {
      getDailyProceedings: jasmine
        .createSpy('getDailyProceedings')
        .and.returnValue(of({ total: 1, items: [{ efiling_id: 1, case_number: 'C-1', petitioner_name: 'P', bench: 'CJ', can_assign_listing_date: true }] })),
      submitDailyProceeding: jasmine.createSpy('submitDailyProceeding').and.returnValue(of({})),
    };

    await TestBed.configureTestingModule({
      imports: [ReaderDailyProceedingsPage],
      providers: [{ provide: ReaderService, useValue: readerServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(ReaderDailyProceedingsPage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('creates', () => {
    expect(component).toBeTruthy();
  });

  it('loads daily proceedings using selected cause-list date', () => {
    expect(readerServiceMock.getDailyProceedings).toHaveBeenCalledWith(
      jasmine.objectContaining({
        cause_list_date: component.selectedCauseListDate,
        page_size: 200,
      }),
    );
  });

  it('submits separate steno and listing remarks', () => {
    const item = component.items[0];
    component.formState[item.efiling_id].steno_remark = 'For steno';
    component.formState[item.efiling_id].listing_remark = 'For listing';
    component.submit(item);
    expect(readerServiceMock.submitDailyProceeding).toHaveBeenCalledWith(
      jasmine.objectContaining({
        steno_remark: 'For steno',
        listing_remark: 'For listing',
      }),
    );
  });
});
