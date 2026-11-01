import React, { useState } from 'react';
import '../../styles/PeriodSelector.css';

export type TimePeriod = '1h' | '6h' | '24h' | '7d' | 'custom';

interface PeriodSelectorProps {
  selectedPeriod: TimePeriod;
  onPeriodChange: (period: TimePeriod) => void;
  onCustomRangeChange?: (range: { start: Date; end: Date } | null) => void;
}

export const PeriodSelector: React.FC<PeriodSelectorProps> = ({
  selectedPeriod,
  onPeriodChange,
  onCustomRangeChange
}) => {
  const [showCustom, setShowCustom] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const periods: { value: TimePeriod; label: string }[] = [
    { value: '1h', label: '1 Hour' },
    { value: '6h', label: '6 Hours' },
    { value: '24h', label: '24 Hours' },
    { value: '7d', label: '7 Days' },
    { value: 'custom', label: 'Custom' }
  ];

  const handlePeriodClick = (period: TimePeriod) => {
    onPeriodChange(period);
    if (period === 'custom') {
      setShowCustom(true);
    } else {
      setShowCustom(false);
      if (onCustomRangeChange) {
        onCustomRangeChange(null);
      }
    }
  };

  const handleApplyCustomRange = () => {
    if (startDate && endDate && onCustomRangeChange) {
      onCustomRangeChange({
        start: new Date(startDate),
        end: new Date(endDate)
      });
      setShowCustom(false);
    }
  };

  return (
    <div className="period-selector">
      <div className="period-buttons">
        {periods.map(period => (
          <button
            key={period.value}
            className={`period-btn ${selectedPeriod === period.value ? 'active' : ''}`}
            onClick={() => handlePeriodClick(period.value)}
          >
            {period.label}
          </button>
        ))}
      </div>

      {showCustom && (
        <div className="custom-range">
          <div className="date-inputs">
            <div className="date-input-group">
              <label htmlFor="start-date">Start:</label>
              <input
                id="start-date"
                type="datetime-local"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="date-input-group">
              <label htmlFor="end-date">End:</label>
              <input
                id="end-date"
                type="datetime-local"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
          <button
            className="apply-btn"
            onClick={handleApplyCustomRange}
            disabled={!startDate || !endDate}
          >
            Apply Range
          </button>
        </div>
      )}
    </div>
  );
};
