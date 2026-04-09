import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { ReaderService } from '../../../../../services/reader/reader.service';
import { StenoHomePage } from './home';

describe('StenoHomePage', () => {
  let component: StenoHomePage;
  let fixture: ComponentFixture<StenoHomePage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StenoHomePage],
      providers: [
        {
          provide: ReaderService,
          useValue: {
            getStenoQueue: () => of({ items: [] }),
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
});

