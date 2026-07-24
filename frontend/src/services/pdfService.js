/**
 * pdfService.js
 *
 * Frontend service handling PDF report downloads from backend.
 * Endpoint: GET /api/research/pdf?molecule_name={molecule}
 *
 * Requests binary PDF bytes from FastAPI backend and triggers browser file save.
 * Does NOT generate PDFs on client side.
 */

import { apiClient } from './apiClient';

/**
 * downloadPdfReport
 *
 * Triggers backend PDF generation and initiates browser file download.
 *
 * @param {string} moleculeName
 * @returns {Promise<string>} — returns downloaded filename on success
 */
export async function downloadPdfReport(moleculeName) {
  if (!moleculeName?.trim()) {
    throw new Error('Molecule name is required to download PDF report.');
  }

  const cleanName = moleculeName.trim();

  try {
    const response = await apiClient.get('/api/research/pdf', {
      params: { molecule_name: cleanName },
      responseType: 'blob',
      timeout: 90000, // PDF generation includes full pipeline execution
    });

    // Determine filename from Content-Disposition header if available
    let filename = `${cleanName.toLowerCase().replace(/\s+/g, '-')}-executive-report.pdf`;
    const contentDisposition = response.headers['content-disposition'];
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^";]+)"?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }

    // Trigger browser file save via object URL
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const blobUrl = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    // Clean up DOM and memory
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);

    return filename;
  } catch (err) {
    if (err.code === 'ECONNABORTED') {
      throw new Error('PDF generation timed out. Please check server status and try again.');
    }
    if (err.response) {
      // If error returned a blob, try parsing text details
      if (err.response.data instanceof Blob) {
        try {
          const errorText = await err.response.data.text();
          const parsed = JSON.parse(errorText);
          throw new Error(parsed.detail || 'Failed to generate PDF report.');
        } catch {
          // Ignore parse error and use default
        }
      }
      throw new Error(err.response.data?.detail || 'Backend failed to generate PDF report.');
    }
    throw new Error('Unable to connect to backend server. Please verify server is running.');
  }
}
