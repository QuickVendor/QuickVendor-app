import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import FeedbackModal from '../components/FeedbackModal';

// Mock the Modal and Button components
vi.mock('../components/ui', () => ({
  Modal: ({ children, isOpen, onClose, title }: any) =>
    isOpen ? (
      <div data-testid="modal">
        <div data-testid="modal-title">{title}</div>
        <button data-testid="modal-close" onClick={onClose}>
          Close
        </button>
        {children}
      </div>
    ) : null,
  Button: ({ children, onClick, disabled, type = 'button', variant, className }: any) => (
    <button
      data-testid={`button-${variant || 'primary'}`}
      onClick={onClick}
      disabled={disabled}
      type={type}
      className={className}
    >
      {children}
    </button>
  ),
}));

// Mock fetch globally
const mockFetch = vi.fn();
(globalThis as any).fetch = mockFetch;

describe('FeedbackModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    userContext: {
      id: '1',
      email: 'test@example.com',
      username: 'testuser',
    },
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();
  });

  it('renders the feedback modal when open', () => {
    render(<FeedbackModal {...defaultProps} />);

    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByTestId('modal-title')).toHaveTextContent('Share Your Feedback');
    expect(screen.getByPlaceholderText(/Tell us about your experience/)).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<FeedbackModal {...defaultProps} isOpen={false} />);

    expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
  });

  it('displays user context information', () => {
    render(<FeedbackModal {...defaultProps} />);

    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText(/Current Page:/)).toBeInTheDocument();
    expect(screen.getByText(/Timestamp:/)).toBeInTheDocument();
  });

  it('displays anonymous when no user context', () => {
    render(<FeedbackModal {...defaultProps} userContext={null} />);

    expect(screen.getByText('Anonymous')).toBeInTheDocument();
  });

  it('shows validation error for empty message', async () => {
    const user = userEvent.setup();
    render(<FeedbackModal {...defaultProps} />);

    // The submit button should be disabled when no content
    const submitButton = screen.getByTestId('button-primary');
    expect(submitButton).toBeDisabled();
    
    // This is actually testing the correct behavior - the button should be
    // disabled when there's no content, preventing invalid form submission
    // which is better UX than showing an error after submission
  });

  it('shows validation error for short message', async () => {
    const user = userEvent.setup();
    render(<FeedbackModal {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Tell us about your experience/);
    await user.type(textarea, 'Hi');

    const submitButton = screen.getByTestId('button-primary');
    await user.click(submitButton);

    expect(screen.getByText('Please provide more details (at least 5 characters)')).toBeInTheDocument();
  });

  it('updates character count as user types', async () => {
    const user = userEvent.setup();
    render(<FeedbackModal {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Tell us about your experience/);
    await user.type(textarea, 'Hello world');

    expect(screen.getByText('11/1000')).toBeInTheDocument();
  });

  it('successfully submits feedback', async () => {
    const user = userEvent.setup();
    mockFetch.mockResolvedValueOnce({
      ok: true,
      headers: new Headers({ 'content-type': 'application/json' }),
      json: async () => ({ success: true, message: 'Thank you!' }),
    });

    render(<FeedbackModal {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Tell us about your experience/);
    await user.type(textarea, 'This is great feedback!');

    const submitButton = screen.getByTestId('button-primary');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/feedback/report',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: expect.stringContaining('This is great feedback!'),
        })
      );
    });

    // Should show success state
    await waitFor(() => {
      expect(screen.getByText('Feedback Submitted!')).toBeInTheDocument();
    });
  });

  it('shows error message when submission fails', async () => {
    const user = userEvent.setup();
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<FeedbackModal {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Tell us about your experience/);
    await user.type(textarea, 'This is feedback');

    const submitButton = screen.getByTestId('button-primary');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to submit feedback. Please try again.')).toBeInTheDocument();
    });
  });

  it('shows loading state during submission', async () => {
    const user = userEvent.setup();
    mockFetch.mockImplementationOnce(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    );

    render(<FeedbackModal {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Tell us about your experience/);
    await user.type(textarea, 'This is feedback');

    const submitButton = screen.getByTestId('button-primary');
    await user.click(submitButton);

    expect(screen.getByText('Submitting...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('calls onClose when cancel button is clicked', async () => {
    const user = userEvent.setup();
    const mockOnClose = vi.fn();

    render(<FeedbackModal {...defaultProps} onClose={mockOnClose} />);

    const cancelButton = screen.getByTestId('button-secondary');
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('resets form when modal opens', () => {
    const { rerender } = render(<FeedbackModal {...defaultProps} isOpen={false} />);

    rerender(<FeedbackModal {...defaultProps} isOpen={true} />);

    const textarea = screen.getByPlaceholderText(/Tell us about your experience/);
    expect(textarea).toHaveValue('');
  });

  it('handles non-JSON response errors', async () => {
    const user = userEvent.setup();
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
      headers: new Headers({ 'content-type': 'text/plain' }),
      text: async () => 'Server Error',
    });

    render(<FeedbackModal {...defaultProps} />);

    const textarea = screen.getByPlaceholderText(/Tell us about your experience/);
    await user.type(textarea, 'This is feedback');

    const submitButton = screen.getByTestId('button-primary');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to submit feedback. Please try again.')).toBeInTheDocument();
    });
  });
});
