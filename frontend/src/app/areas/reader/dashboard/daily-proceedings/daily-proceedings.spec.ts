import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ReaderService } from '../../../../services/reader/reader.service';
import { ReaderDailyProceedingsPage } from './daily-proceedings';

describe('ReaderDailyProceedingsPage', () => {
  let component: ReaderDailyProceedingsPage;
  let fixture: ComponentFixture<ReaderDailyProceedingsPage>;
  let readerServiceMock: {
    getDailyProceedings: jasmine.Spy;
    getPurposes: jasmine.Spy;
    submitDailyProceeding: jasmine.Spy;
  };

  beforeEach(async () => {
    readerServiceMock = {
      getDailyProceedings: jasmine
        .createSpy('getDailyProceedings')
        .and.returnValue(
          of({
            total: 1,
            items: [
              {
                efiling_id: 1,
                case_number: 'C-1',
                petitioner_name: 'P',
                bench: 'CJ',
                can_assign_listing_date: true,
                latest_steno_purpose_code: 7,
                hearing_dates_with_steno: [],
              },
            ],
          }),
        ),
      getPurposes: jasmine.createSpy('getPurposes').and.returnValue(of([{ purpose_code: 7, purpose_name: 'Final Order' }])),
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
    expect(readerServiceMock.getPurposes).toHaveBeenCalled();
  });

  it('preloads and submits the selected steno purpose', () => {
    const item = component.items[0];
    expect(component.formState[item.efiling_id].steno_purpose_code).toBe(7);

    component.formState[item.efiling_id].steno_purpose_code = 11;
    component.formState[item.efiling_id].listing_remark = 'For listing';
    component.submit(item);
    expect(readerServiceMock.submitDailyProceeding).toHaveBeenCalledWith(
      jasmine.objectContaining({
        steno_purpose_code: 11,
        listing_remark: 'For listing',
      }),
    );
  });

  it('disables submit only when the selected hearing date already has a steno workflow', async () => {
    readerServiceMock.submitDailyProceeding.calls.reset();
    const lockedHearing = '2024-06-15';
    readerServiceMock.getDailyProceedings.and.returnValue(
      of({
        total: 1,
        items: [
          {
            efiling_id: 99,
            case_number: 'C-99',
            petitioner_name: 'P',
            bench: 'CJ',
            can_assign_listing_date: true,
            last_hearing_date: lockedHearing,
            hearing_dates_with_steno: [lockedHearing],
            steno_workflow_status: 'PENDING_UPLOAD',
          },
        ],
      }),
    );
    const f = TestBed.createComponent(ReaderDailyProceedingsPage);
    f.detectChanges();
    await f.whenStable();
    const cmp = f.componentInstance;
    expect(cmp.isProceedingsLocked(cmp.items[0])).toBe(true);
    const btn = f.nativeElement.querySelector('button.btn-primary') as HTMLButtonElement | null;
    expect(btn?.disabled).toBe(true);
    cmp.submit(cmp.items[0]);
    expect(readerServiceMock.submitDailyProceeding).not.toHaveBeenCalled();
  });

  it('allows submit when the hearing date is changed away from a locked date', async () => {
    readerServiceMock.submitDailyProceeding.calls.reset();
    const lockedDate = '2024-06-15';
    const otherDate = '2024-07-01';
    readerServiceMock.getDailyProceedings.and.returnValue(
      of({
        total: 1,
        items: [
          {
            efiling_id: 88,
            case_number: 'C-88',
            petitioner_name: 'P',
            bench: 'CJ',
            can_assign_listing_date: true,
            last_hearing_date: lockedDate,
            hearing_dates_with_steno: [lockedDate],
          },
        ],
      }),
    );
    const f = TestBed.createComponent(ReaderDailyProceedingsPage);
    f.detectChanges();
    await f.whenStable();
    const cmp = f.componentInstance;
    expect(cmp.isProceedingsLocked(cmp.items[0])).toBe(true);
    cmp.formState[88].hearing_date = otherDate;
    f.detectChanges();
    expect(cmp.isProceedingsLocked(cmp.items[0])).toBe(false);
    const btn = f.nativeElement.querySelector('button.btn-primary') as HTMLButtonElement | null;
    expect(btn?.disabled).toBe(false);
  });
});
