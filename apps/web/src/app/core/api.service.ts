import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/v1';

  get<T>(path: string, query: Record<string, string | number | null | undefined> = {}): Observable<T> {
    let params = new HttpParams();
    for (const [key, value] of Object.entries(query)) {
      if (value !== null && value !== undefined && value !== '') {
        params = params.set(key, String(value));
      }
    }
    return this.http.get<T>(`${this.base}${path}`, { params });
  }

  post<T>(path: string, body: unknown = {}): Observable<T> {
    return this.http.post<T>(`${this.base}${path}`, body);
  }

  patch<T>(path: string, body: unknown): Observable<T> {
    return this.http.patch<T>(`${this.base}${path}`, body);
  }

  put<T>(path: string, body: unknown): Observable<T> {
    return this.http.put<T>(`${this.base}${path}`, body);
  }

  delete<T>(path: string, body?: unknown): Observable<T> {
    return this.http.request<T>('DELETE', `${this.base}${path}`, { body });
  }

  upload<T>(path: string, file: File, fields: Record<string, string> = {}): Observable<T> {
    const data = new FormData();
    data.append('file', file);
    for (const [key, value] of Object.entries(fields)) {
      data.append(key, value);
    }
    return this.http.post<T>(`${this.base}${path}`, data);
  }
}
