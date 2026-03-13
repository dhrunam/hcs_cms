import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EFile } from './e-file';

describe('EFile', () => {
  let component: EFile;
  let fixture: ComponentFixture<EFile>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EFile],
    }).compileComponents();

    fixture = TestBed.createComponent(EFile);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
