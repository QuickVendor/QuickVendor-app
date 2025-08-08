import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extends Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Runs a cleanup after each test case
afterEach(() => {
  cleanup();
});

// Mock environment variables for tests
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000/test',
    pathname: '/test',
    search: '',
    hash: '',
  },
  writable: true,
});

// Mock ResizeObserver for tests that might need it
globalThis.ResizeObserver = class ResizeObserver {
  constructor(cb: any) {}
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock fetch for API calls
globalThis.fetch = vi.fn();

// Mock console methods to avoid noise in tests
globalThis.console = {
  ...console,
  log: vi.fn(),
  error: vi.fn(),
  warn: vi.fn(),
} as any;
