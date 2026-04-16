import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ReaderService } from '../../../../../services/reader/reader.service';
import { StenoHomePage } from './home';

describe('StenoHomePage', () => {
  let component: StenoHomePage;
  let fixture: ComponentFixture<StenoHomePage>;

  const queueItem = {
    workflow_id: 1,
    efiling_id: 10,
    case_number: 'C-1',
    e_filing_number: 'EF-1',
    petitioner_vs_respondent: 'A vs B',
    document_type: 'ORDER',
    workflow_status: 'PENDING_UPLOAD',
    judge_approval_status: 'PENDING',
    hearing_date: '2026-04-16',
    next_listing_date: '2026-04-17',
    proceedings_text: 'Proceedings text',
    steno_purpose_code: 7,
    steno_purpose_name: 'Final Order',
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StenoHomePage],
      providers: [
        {
          provide: ReaderService,
          useValue: {
            getStenoQueue: () => of({ items: [queueItem] }),
            uploadStenoDraft: () => of({}),
            uploadStenoDraftFile: () => of({}),
            submitStenoToJudge: () => of({}),
          },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(StenoHomePage);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('creates', () => {
    expect(component).toBeTruthy();
  });

  it('renders the selected steno purpose', () => {
    expect(fixture.nativeElement.textContent).toContain('Purpose: Final Order');
  });
});

