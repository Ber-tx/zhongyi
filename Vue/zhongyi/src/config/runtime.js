function parseBoolean(value, fallback = false) {
  if (value === undefined || value === null || value === '') return fallback;
  const normalized = String(value).trim().toLowerCase();
  return ['1', 'true', 'yes', 'on'].includes(normalized);
}

export const SOFTWARE_MODE = parseBoolean(import.meta.env.VITE_SOFTWARE_MODE, false);
export const ENABLE_IDCARD = !SOFTWARE_MODE && parseBoolean(import.meta.env.VITE_ENABLE_IDCARD, true);
export const ENABLE_PULSE = !SOFTWARE_MODE && parseBoolean(import.meta.env.VITE_ENABLE_PULSE, true);

export const FRONTEND_DIAG_KEYS = ENABLE_PULSE
  ? ['wang', 'wen', 'wenjuan', 'qie']
  : ['wang', 'wen', 'wenjuan'];

export const REPORT_DIAG_KEYS = ENABLE_PULSE
  ? ['wang', 'wen_audio', 'wen_questionnaire', 'qie']
  : ['wang', 'wen_audio', 'wen_questionnaire'];
