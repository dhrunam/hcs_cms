import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { ApiService } from './api.service';
import { environment } from '../../../environments/environment';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ApiService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should fetch cases', () => {
    const mockCases = { results: [], count: 0 };
    service.getCases().subscribe((data) => {
      expect(data).toEqual(mockCases);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/cases/`);
    expect(req.request.method).toBe('GET');
    req.flush(mockCases);
  });

  it('should fetch a single case', () => {
    const mockCase = { id: 1, case_number: 'WP-001/2024' };
    service.getCase(1).subscribe((data) => {
      expect(data).toEqual(mockCase);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/cases/1/`);
    expect(req.request.method).toBe('GET');
    req.flush(mockCase);
  });

  it('should create a case', () => {
    const newCase = { case_number: 'WP-002/2024', case_title: 'Test Case' };
    service.createCase(newCase).subscribe((data) => {
      expect(data).toEqual({ id: 2, ...newCase });
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/cases/`);
    expect(req.request.method).toBe('POST');
    req.flush({ id: 2, ...newCase });
  });

  it('should delete a case', () => {
    service.deleteCase(1).subscribe();

    const req = httpMock.expectOne(`${environment.apiUrl}/cases/1/`);
    expect(req.request.method).toBe('DELETE');
    req.flush(null);
  });
});
