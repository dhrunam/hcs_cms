import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { CauseListService } from '../../../../services/listing/cause-list.service';
import { ListingOfficerHome } from './home';

describe('ListingOfficerHome', () => {
  let component: ListingOfficerHome;
  let fixture: ComponentFixture<ListingOfficerHome>;
  let causeListServiceMock: {
    getBenchConfigurations: jasmine.Spy;
    getDraftPreview: jasmine.Spy;
    getPublishedCauseLists: jasmine.Spy;
    getDraftPdf: jasmine.Spy;
  };

  beforeEach(async () => {
    causeListServiceMock = {
      getBenchConfigurations: jasmine.createSpy('getBenchConfigurations').and.returnValue(
        of({ items: [{ bench_key: 'B1', label: 'Bench 1', bench_code: 'B1', bench_name: 'Bench 1', judge_names: [], judge_user_ids: [], reader_user_ids: [], is_accessible_to_reader: true }] }),
      ),
      getDraftPreview: jasmine.createSpy('getDraftPreview').and.returnValue(
        of({ cause_list_id: 10, cause_list_date: '2026-04-16', bench_key: 'B1', items: [] }),
      ),
      getPublishedCauseLists: jasmine.createSpy('getPublishedCauseLists').and.returnValue(of({ items: [] })),
      getDraftPdf: jasmine.createSpy('getDraftPdf').and.returnValue(of(new Blob(['pdf'], { type: 'application/pdf' }))),
    };

    await TestBed.configureTestingModule({
      imports: [ListingOfficerHome],
      providers: [{ provide: CauseListService, useValue: causeListServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(ListingOfficerHome);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('fetches draft pdf via authenticated service call', () => {
    const state = component.benchStates[0];
    state.cause_list_id = 10;
    const openSpy = spyOn(window, 'open');
    const createUrlSpy = spyOn(URL, 'createObjectURL').and.returnValue('blob:test');
    const revokeSpy = spyOn(URL, 'revokeObjectURL');
    component.selectedDate = '2026-04-16';
    component.viewDraftPdf(state);
    expect(causeListServiceMock.getDraftPdf).toHaveBeenCalledWith('2026-04-16', 'B1');
    expect(openSpy).toHaveBeenCalledWith('blob:test', '_blank', 'noopener');
    expect(createUrlSpy).toHaveBeenCalled();
    expect(revokeSpy).not.toHaveBeenCalled();
  });
});
